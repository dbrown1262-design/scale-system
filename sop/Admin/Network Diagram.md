# SOP -- Network Topology and Configuration

## 1. Purpose

This SOP documents the network topology and configuration used at the
facility. It provides a reference for maintenance, troubleshooting,
equipment replacement, and future expansion.

## 2. Scope

This procedure applies to the Spectrum internet connection, TP-Link
router, switches, wireless access point, cameras, servers, environmental
controllers, monitoring devices, and employee Wi-Fi access.

## 3. Network Overview

The facility connects to the Internet through Spectrum Fiber service.

A Spectrum fiber modem converts the fiber connection to Ethernet and
connects to the WAN port of the TP-Link ER7206 router. The router
provides firewall services, DHCP, and IP address reservations.

The router distributes connectivity to:
- Crew Room PoE switch
- Processing Room PoE switch
- Hash Room PoE switch

A NetGear AC750 operates in Access Point mode and provides Wi-Fi
coverage in the main building for facility devices and employee portable equipment.

A TP-Link EAP610 operates in Access Point mode and provides Wi-Fi
coverage in the Hash Room for facility devices and employee portable equipment.

## 4. IP Addressing

``` text
   Purpose              Range
   -------------------- --------------------------------
   Router               192.168.1.1
   Reserved addresses   192.168.1.2 -- 192.168.1.99
   DHCP pool            192.168.1.100 -- 192.168.1.199
```

Permanent devices should use DHCP reservations.

## 5. TP-Link ER7206 Router

### Management

-   Address: `192.168.1.1`
-   Username: `admin`
-   Password: `admin?`

### WAN

-   Connected to Spectrum modem.

### LAN Connections

#### Crew Room RLA-PS1 8-Port PoE

``` text
  IP             Device
  -------------- ----------------------------
  192.168.1.3    EcoFlow Delta 2 Powaer Station
                   User Id: dbrown1262@verizon.net  Password:  Adirondack1891?
  192.168.1.10   Synology NAS
                   User Id: AdkAdmin   Password: Adk1891?
  192.168.1.12   Mike's Server
  192.168.1.14   NAS Monitor (Raspberry Pi)
  192.168.1.15   Workstation
  192.168.1.22   Front Door Camera
                    User Id: admin  Password: Adk1891
```

#### Processing Room RLA-PS1 8-Port PoE

``` text
  IP             Device
  -------------- ----------------------------
  192.168.1.20   Sample Camera
  192.168.1.21   Processing Camera
  192.168.1.51   TrolMaster -- Mom Room
  192.168.1.52   TrolMaster -- Grow 1
  192.168.1.53   TrolMaster -- Grow 2
  192.168.1.2    NetGear AC750 Access Point
                     User Id: admin   Password: admin
```

## 6. NetGear AC750 Access Point

Configured in **Access Point Mode**.

### 2.4 GHz

-   SSID: `MySpectrumWiFi09-2G`
-   Security: WPA2
-   Password: `jollyrock947`

### 5 GHz

-   SSID: `MySpectrumWiFi09-5G`
-   Security: WPA2
-   Password: `jollyrock947`

Reserved Devices

``` text
  IP             Device
  -------------- ---------------------------
  192.168.1.30   UbiBot -- Hash Room
  192.168.1.31   UbiBot -- Drying Room
  192.168.1.32   UbiBot -- Grow 1
  192.168.1.33   UbiBot -- Grow 2
  192.168.1.34   UbiBot -- Mom Room
  192.168.1.35   UbiBot -- Processing Room
  192.168.1.36   UbiBot -- Hash Entry
  192.168.1.40   Ring Chime
  192.168.1.41   Ring Doorbell
```

## 7. Hash Room

``` text
  IP    Device
  ------------   --------------------------------------
  192.168.1.4    Tplink EAP610 wireless access point
                    User Id: admin1  Password: admin1
  xxxxxxxxxxx    Tplink TL-SF1006P 4 port POE switch
  192.168.1.23   Hash Room Camera
  192.168.1.xx   TTlock gateway
  192.168.1.30   UbiBot Hash Room
  192.168.1.36   UbiBot Hash Entry
```

## 8. Administration

1.  Use DHCP reservations for permanent devices.
2.  Assign new infrastructure devices within the reserved range.
3.  Document network changes promptly.
4.  Verify reservations after router replacement or restoration.

## 9. High-Level Topology

``` text
Internet
    │
Spectrum Fiber
    │
Spectrum Modem
    │
TP-Link ER7206 (192.168.1.1)
    ├── Crew Room PoE Switch
    │      ├── EcoFlow Delta 2 Power Station
    │      ├── NAS
    │      ├── NAS Monitor
    │      ├── Mike's Server
    │      ├── Workstation
    │      └── Front Door Camera
    │
    ├── Processing PoE Switch
    │      ├── Sample Camera
    │      ├── Processing Camera
    │      ├── TrolMaster Controllers
    │      └── NetGear AC750 Access Point
    │             └── Wi-Fi Devices
    │
    ├── Hash Room PoE Switch
    │      ├── Hash Camera
    │      └── Tp-Link EAP610 WiFi access point
    │             └── Wi-Fi Devices
    │
    └── TTLock Gateway
```
