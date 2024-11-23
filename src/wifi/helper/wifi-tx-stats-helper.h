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

#ifndef WIFI_TX_STATS_HELPER_H
#define WIFI_TX_STATS_HELPER_H

#include <cstdint>
#include <map>
#include <vector>
#include <ranges>

#include <ns3/object.h>
#include <ns3/type-id.h>
#include <ns3/qos-utils.h>
#include <ns3/nstime.h>

namespace ns3
{

// The final result
struct WifiTxStatistics
{
    std::map<uint32_t /* Node ID */, std::map<uint8_t /* Link ID */, uint64_t>> m_numSuccessPerNodeLink; // # successful pkts
    std::map<uint32_t /* Node ID */, uint64_t> m_numRetransmittedPktsPerNode; // # successful pkts with 2 or more TX
    std::map<uint32_t /* Node ID */, uint64_t> m_numRetransmissionPerNode; // # retransmissions (i.e. failures)
    std::map<uint32_t /* Node ID */, double> m_avgFailuresPerNode; // # retransmissions / # successful pkts
    std::map<uint32_t /* Node ID */, uint64_t> m_numFinalFailedPerNode; // # failed pkts
    uint64_t m_numSuccess{0};
    uint64_t m_numRetransmitted{0};
    double m_avgFailures{0};
    uint64_t m_numFinalFailed{0};
};

// Per-packet record, created when enqueued at MAC layer
struct WifiTxPerPktRecord
{
    bool m_txStarted{false};
    bool m_acked{false};
    bool m_dequeued{false};
    uint64_t m_seqNum{0};
    uint32_t m_srcNodeId{0};
    uint32_t m_failures{0};
    double m_enqueueMs{0};
    double m_txStartMs{0};
    double m_ackMs{0};
    double m_dequeueMs{0};
    uint8_t m_tid{0};
    uint8_t m_successLinkId{0};
};
typedef std::map<uint32_t /* Node ID */, std::map<uint8_t /* Link ID */, std::vector<WifiTxPerPktRecord>>> WifiPktTxRecordMap;
typedef std::map<uint64_t /* UID */, WifiTxPerPktRecord> WifiPktUidMap;
typedef std::map<uint32_t /* Node ID */, std::vector<WifiTxPerPktRecord>> WifiPktNodeIdMap;

// Forward declaration
class NetDeviceContainer;
class NodeContainer;
class Time;
class Packet;
class WifiMpdu;
class WifiTxStatsTraceSink;

class WifiTxStatsHelper
{
  public:
    WifiTxStatsHelper();
    /**
     * Enables trace collection for all nodes and WifiNetDevices in the specified NodeContainer.
     * @param nodes The NodeContainer to which traces are to be connected.
     * @param MacToNodeMap (optional) A mapping from MAC address to node ID. If not provided, a
     * mapping is built automatically.
     */
    void Enable(NodeContainer nodes, const std::map<Mac48Address, uint32_t>& MacToNodeMap = {});
    void Enable(const NetDeviceContainer& devices);
    WifiTxStatistics GetStatistics();
    const WifiPktTxRecordMap& GetSuccessInfoMap();
    const WifiPktNodeIdMap& GetFailureInfoMap();
    void Start(const Time& startTime);
    void Stop(const Time& stopTime);
    void Reset();
    const std::list<AcIndex> m_aci = {
        AC_BE,
        AC_BK,
        AC_VI,
        AC_VO,
        AC_BE_NQOS
    };

  private:
    Ptr<WifiTxStatsTraceSink> m_traceSink;
};

class WifiTxStatsTraceSink : public Object
{
  public:
    WifiTxStatsTraceSink();
    static TypeId GetTypeId();
    void DoStart();
    void DoStop();
    void DoReset();
    WifiTxStatistics DoGetStatistics() const;
    const WifiPktTxRecordMap& DoGetSuccessInfoMap();
    const WifiPktNodeIdMap& DoGetFailureInfoMap();

    // functions to be called back
    void NotifyMacEnqueue(Ptr<const WifiMpdu> mpdu);
    void NotifyTxStart(Ptr<const Packet> pkt, double txPowerW);
    void NotifyAcked(Ptr<const WifiMpdu> mpdu, uint8_t linkId);
    void NotifyMacDequeue(Ptr<const WifiMpdu> mpdu);

  private:
    bool m_statsCollecting;
    WifiPktUidMap m_inflightMap;
    WifiPktTxRecordMap m_successMap;
    WifiPktNodeIdMap m_failureMap;
};

}

#endif // WIFI_TX_STATS_HELPER_H
