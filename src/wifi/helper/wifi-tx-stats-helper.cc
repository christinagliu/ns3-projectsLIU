/*
 * Copyright (c) 2024 Huazhong University of Science and Technology
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#include "wifi-tx-stats-helper.h"

#include <ns3/nstime.h>
#include <ns3/wifi-net-device.h>
#include <ns3/net-device-container.h>
#include <ns3/wifi-mac-queue.h>
#include <ns3/frame-exchange-manager.h>
#include <ns3/node-container.h>

namespace ns3
{

WifiTxStatsHelper::WifiTxStatsHelper()
{
}

void WifiTxStatsHelper::Enable(NodeContainer nodes, const std::map<Mac48Address, uint32_t> &MacToNodeMap)
{
    NetDeviceContainer devCon;
    for (auto node = nodes.Begin(); node != nodes.End(); ++node)
    {
        Ptr<NetDevice> dev = (*node)->GetDevice(0);
        NS_ASSERT_MSG(dev, "net device should exist");
        devCon.Add(dev);
    }
    Enable(devCon);
}

void
WifiTxStatsHelper::Enable(const NetDeviceContainer& devices)
{
    NS_ABORT_MSG_IF(m_traceSink, "A trace sink is already configured for this helper");
    m_traceSink = CreateObject<WifiTxStatsTraceSink>();

    for (auto dev = devices.Begin(); dev != devices.End(); ++dev)
    {
        Ptr<WifiNetDevice> wifiDev = DynamicCast<WifiNetDevice>(*dev);
        if (wifiDev)
        {
            for (auto& ac : m_aci)
            {
                if (wifiDev->GetMac()->GetTxopQueue(ac))
                {
                    // Trace enqueue & dequeue for available ACs
                    wifiDev->GetMac()->GetTxopQueue(ac)->TraceConnectWithoutContext(
                        "Enqueue",
                        MakeCallback(&WifiTxStatsTraceSink::NotifyMacEnqueue, m_traceSink));
                    wifiDev->GetMac()->GetTxopQueue(ac)->TraceConnectWithoutContext(
                        "Dequeue",
                        MakeCallback(&WifiTxStatsTraceSink::NotifyMacDequeue, m_traceSink));
                }
                if (wifiDev->GetMac()->GetQosTxop(ac))
                {
                    // Handle Block Ack for QoS ACs
                    wifiDev->GetMac()->GetQosTxop(ac)->GetBaManager()->TraceConnectWithoutContext(
                        "AckedMpdu",
                        MakeCallback(&WifiTxStatsTraceSink::NotifyAcked, m_traceSink));
                }
            }

            for (int i = 0; i < wifiDev->GetNPhys(); i++)
            {
                // Handle non-Block Ack
                wifiDev->GetMac()->GetFrameExchangeManager(i)->TraceConnectWithoutContext(
                    "AckedMpdu",
                    MakeCallback(&WifiTxStatsTraceSink::NotifyAcked, m_traceSink));
                wifiDev->GetPhy(i)->TraceConnectWithoutContext(
                    "PhyTxBegin",
                    MakeCallback(&WifiTxStatsTraceSink::NotifyTxStart, m_traceSink));
            }
        }
    }
}

WifiTxStatistics
WifiTxStatsHelper::GetStatistics()
{
    NS_ABORT_MSG_IF(!m_traceSink, "WifiTxStatsHelper not enabled.");
    return m_traceSink->DoGetStatistics();
}

const WifiPktTxRecordMap&
WifiTxStatsHelper::GetSuccessInfoMap()
{
    NS_ABORT_MSG_IF(!m_traceSink, "WifiTxStatsHelper not enabled.");
    return m_traceSink->DoGetSuccessInfoMap();
}

const WifiPktNodeIdMap&
WifiTxStatsHelper::GetFailureInfoMap()
{
    NS_ABORT_MSG_IF(!m_traceSink, "WifiTxStatsHelper not enabled.");
    return m_traceSink->DoGetFailureInfoMap();
}

void
WifiTxStatsHelper::Start(const Time& startTime)
{
    NS_ABORT_MSG_IF(!m_traceSink, "WifiTxStatsHelper not enabled.");
    Simulator::Schedule(startTime, &WifiTxStatsTraceSink::DoStart, m_traceSink);
}

void
WifiTxStatsHelper::Stop(const Time& stopTime)
{
    NS_ABORT_MSG_IF(!m_traceSink, "WifiTxStatsHelper not enabled.");
    Simulator::Schedule(stopTime, &WifiTxStatsTraceSink::DoStop, m_traceSink);
}

void
WifiTxStatsHelper::Reset()
{
    NS_ABORT_MSG_IF(!m_traceSink, "WifiTxStatsHelper not enabled.");
    m_traceSink->DoReset();
}

NS_OBJECT_ENSURE_REGISTERED(WifiTxStatsTraceSink);

WifiTxStatsTraceSink::WifiTxStatsTraceSink() : m_statsCollecting(false)
{
}

TypeId
WifiTxStatsTraceSink::GetTypeId()
{
    static TypeId tid =
        TypeId("ns3::WifiTxStatsTraceSink")
            .SetParent<Object>()
            .SetGroupName("Wifi")
            .AddConstructor<WifiTxStatsTraceSink>();
    return tid;
}

void
WifiTxStatsTraceSink::DoStart()
{
    m_statsCollecting = true;
}

void
WifiTxStatsTraceSink::DoStop()
{
    m_statsCollecting = false;
}

void
WifiTxStatsTraceSink::DoReset()
{
    m_inflightMap.clear();
    m_successMap.clear();
    m_failureMap.clear();
}

WifiTxStatistics
WifiTxStatsTraceSink::DoGetStatistics() const
{
    WifiTxStatistics results;
    std::map<uint32_t /* Node ID */, uint64_t> numSuccessPerNode;
    // Iterate through success map
    for (const auto& [nodeId, linkMap] : m_successMap)
    {
        for (const auto& [linkId, recordVec] : linkMap)
        {
            for (const auto& record : recordVec)
            {
                results.m_numSuccessPerNodeLink[nodeId][linkId]++;
                numSuccessPerNode[nodeId]++;
                if (record.m_failures > 0)
                {
                    results.m_numRetransmittedPktsPerNode[nodeId]++;
                    results.m_numRetransmissionPerNode[nodeId] += record.m_failures;
                }
            }
        }
    }
    // Iterate through failure map
    for (const auto& [nodeId, recordVec] : m_failureMap)
    {
        results.m_numFinalFailedPerNode[nodeId] += recordVec.size();
    }
    // Get total results
    for (const auto& [nodeId, linkMap] : results.m_numSuccessPerNodeLink)
    {
        for (const auto& [linkId, pktNum] : linkMap)
        {
            results.m_numSuccess += pktNum;
        }
    }
    for (const auto& [nodeId, num] : results.m_numRetransmittedPktsPerNode)
    {
        results.m_numRetransmitted += num;
    }
    uint64_t numRetransmission = 0;
    for (const auto&[nodeId, num] : results.m_numRetransmissionPerNode)
    {
        results.m_avgFailuresPerNode[nodeId] = static_cast<long double>(num) /
            numSuccessPerNode[nodeId];
        numRetransmission += num;
    }
    results.m_avgFailures = static_cast<long double>(numRetransmission) / results.m_numSuccess;
    for (const auto &[nodeId, num]: results.m_numFinalFailedPerNode)
    {
        results.m_numFinalFailed += num;
    }
    return results;
}

const WifiPktTxRecordMap&
WifiTxStatsTraceSink::DoGetSuccessInfoMap()
{
    return m_successMap;
}

const WifiPktNodeIdMap&
WifiTxStatsTraceSink::DoGetFailureInfoMap()
{
    return m_failureMap;
}

void
WifiTxStatsTraceSink::NotifyMacEnqueue(Ptr<const WifiMpdu> mpdu)
{
    if (mpdu->GetHeader().IsData())
    {
        if (mpdu->GetPacketSize() == 0)
        {
            // exclude Null frame
            return;
        }
        WifiTxPerPktRecord record;
        record.m_srcNodeId = Simulator::GetContext();
        record.m_enqueueMs = Simulator::Now().ToDouble(Time::MS);
        record.m_tid = mpdu->GetHeader().IsQosData() ? mpdu->GetHeader().GetQosTid() : 0;
        m_inflightMap[mpdu->GetPacket()->GetUid()] = record;
    }
}

void
WifiTxStatsTraceSink::NotifyTxStart(Ptr<const Packet> pkt, double txPowerW)
{
    if (const auto mapIt = m_inflightMap.find(pkt->GetUid()); mapIt != m_inflightMap.end())
    {
        if (!mapIt->second.m_txStarted)
        {
            mapIt->second.m_txStarted = true;
            mapIt->second.m_txStartMs = Simulator::Now().ToDouble(Time::MS);
        }
        else
        {
            mapIt->second.m_failures++;
        }
    }
}

void
WifiTxStatsTraceSink::NotifyAcked(Ptr<const WifiMpdu> mpdu, const uint8_t linkId)
{
    if (const auto mapIt = m_inflightMap.find(mpdu->GetPacket()->GetUid()); mapIt != m_inflightMap.end())
    {
        mapIt->second.m_acked = true;
        mapIt->second.m_ackMs = Simulator::Now().ToDouble(Time::MS);
        mapIt->second.m_successLinkId = linkId;
    }
}

void
WifiTxStatsTraceSink::NotifyMacDequeue(Ptr<const WifiMpdu> mpdu)
{
    if (const auto mapIt = m_inflightMap.find(mpdu->GetPacket()->GetUid()); mapIt != m_inflightMap.end())
    {
        mapIt->second.m_dequeued = true;
        mapIt->second.m_dequeueMs = Simulator::Now().ToDouble(Time::MS);
        mapIt->second.m_seqNum = mpdu->GetHeader().GetSequenceNumber();

        if (m_statsCollecting)
        {
            if (mapIt->second.m_acked)
            {
                // Put record into success map and remove it from inflight map
                m_successMap[mapIt->second.m_srcNodeId][mapIt->second.m_successLinkId].emplace_back(mapIt->second);
            }
            else
            {
                mapIt->second.m_failures += 1;
                // Put record into failure map and remove it from inflight map
                m_failureMap[mapIt->second.m_srcNodeId].emplace_back(mapIt->second);
            }
        }
        m_inflightMap.erase(mapIt);
    }
}

}
