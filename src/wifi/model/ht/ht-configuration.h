/*
 * Copyright (c) 2018  Sébastien Deronne
 *
 * SPDX-License-Identifier: GPL-2.0-only
 *
 * Author: Sébastien Deronne <sebastien.deronne@gmail.com>
 */

#ifndef HT_CONFIGURATION_H
#define HT_CONFIGURATION_H

#include "ns3/object.h"

namespace ns3
{

/**
 * \brief HT configuration
 * \ingroup wifi
 *
 * This object stores HT configuration information, for use in modifying
 * AP or STA behavior and for constructing HT-related information elements.
 *
 */
class HtConfiguration : public Object
{
  public:
    HtConfiguration();
    ~HtConfiguration() override;

    /**
     * \brief Get the type ID.
     * \return the object TypeId
     */
    static TypeId GetTypeId();

    /**
     * Enable or disable SGI support.
     *
     * \param enable true if SGI is to be supported,
     *               false otherwise
     */
    void SetShortGuardIntervalSupported(bool enable);
    /**
     * \return whether the device supports SGI.
     *
     * \return true if SGI is supported,
     *         false otherwise.
     */
    bool GetShortGuardIntervalSupported() const;
    /**
     * Enable or disable LDPC support.
     *
     * \param enable true if LDPC is to be supported,
     *               false otherwise
     */
    void SetLdpcSupported(bool enable);
    /**
     * \return whether the device supports LDPC.
     *
     * \return true if LDPC is supported,
     *         false otherwise.
     */
    bool GetLdpcSupported() const;
    /**
     * Enable or disable 40 MHz operation support.
     *
     * \param enable true if both 20 MHz and 40 MHz operation is to be supported,
     *               false if only 20 MHz operation is to be supported
     */
    void Set40MHzOperationSupported(bool enable);
    /**
     * \return true if both 20 MHz and 40 MHz operation is supported, false if
     *         only 20 MHz operation is supported
     */
    bool Get40MHzOperationSupported() const;

  private:
    bool m_sgiSupported;   ///< flag whether short guard interval is supported
    bool m_ldpcSupported;  ///< flag whether LDPC coding is supported
    bool m_40MHzSupported; ///< whether 40 MHz operation is supported
};

} // namespace ns3

#endif /* HT_CONFIGURATION_H */