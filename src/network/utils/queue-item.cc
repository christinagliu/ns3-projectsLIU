/*
 * Copyright (c) 2016 Universita' degli Studi di Napoli Federico II
 *
 * SPDX-License-Identifier: GPL-2.0-only
 *
 * Author: Stefano Avallone <stefano.avallone@unina.it>
 */

#include "queue-item.h"

#include "ns3/log.h"
#include "ns3/packet.h"

namespace ns3
{

NS_LOG_COMPONENT_DEFINE("QueueItem");

QueueItem::QueueItem(Ptr<Packet> p)
{
    NS_LOG_FUNCTION(this << p);
    m_packet = p;
}

QueueItem::~QueueItem()
{
    NS_LOG_FUNCTION(this);
    m_packet = nullptr;
}

Ptr<Packet>
QueueItem::GetPacket() const
{
    NS_LOG_FUNCTION(this);
    return m_packet;
}

uint32_t
QueueItem::GetSize() const
{
    NS_LOG_FUNCTION(this);
    NS_ASSERT(m_packet);
    return m_packet->GetSize();
}

bool
QueueItem::GetUint8Value(QueueItem::Uint8Values field, uint8_t& value) const
{
    NS_LOG_FUNCTION(this);
    return false;
}

void
QueueItem::Print(std::ostream& os) const
{
    os << GetPacket();
}

std::ostream&
operator<<(std::ostream& os, const QueueItem& item)
{
    item.Print(os);
    return os;
}

QueueDiscItem::QueueDiscItem(Ptr<Packet> p, const Address& addr, uint16_t protocol)
    : QueueItem(p),
      m_address(addr),
      m_protocol(protocol),
      m_txq(0)
{
    NS_LOG_FUNCTION(this << p << addr << protocol);
}

QueueDiscItem::~QueueDiscItem()
{
    NS_LOG_FUNCTION(this);
}

Address
QueueDiscItem::GetAddress() const
{
    NS_LOG_FUNCTION(this);
    return m_address;
}

uint16_t
QueueDiscItem::GetProtocol() const
{
    NS_LOG_FUNCTION(this);
    return m_protocol;
}

uint8_t
QueueDiscItem::GetTxQueueIndex() const
{
    NS_LOG_FUNCTION(this);
    return m_txq;
}

void
QueueDiscItem::SetTxQueueIndex(uint8_t txq)
{
    NS_LOG_FUNCTION(this << (uint16_t)txq);
    m_txq = txq;
}

Time
QueueDiscItem::GetTimeStamp() const
{
    NS_LOG_FUNCTION(this);
    return m_tstamp;
}

void
QueueDiscItem::SetTimeStamp(Time t)
{
    NS_LOG_FUNCTION(this << t);
    m_tstamp = t;
}

void
QueueDiscItem::Print(std::ostream& os) const
{
    os << GetPacket() << " "
       << "Dst addr " << m_address << " "
       << "proto " << m_protocol << " "
       << "txq " << +m_txq;
}

uint32_t
QueueDiscItem::Hash(uint32_t perturbation) const
{
    NS_LOG_WARN("The Hash method should be redefined by subclasses");
    return 0;
}

} // namespace ns3