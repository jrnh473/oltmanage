# OLT Management System - Flask + React + MariaDB

একটি সম্পূর্ণ Multi-Vendor OLT (Optical Line Terminal) ম্যানেজমেন্ট সিস্টেম Adapter Pattern ভিত্তিক Flask ব্যাকএন্ড এবং React ফ্রন্টএন্ড দিয়ে তৈরি।

## 🎯 বৈশিষ্ট্য

- **Multi-Vendor সাপোর্ট**: ৯টি OLT ভেন্ডর (C-DATA, ECOM, VSOL, BDCOM, Connect+, DBC, AVEIS, HSGQ, PHYHOME)
- **Dual Connection Method**: SNMP (প্রাথমিক) + SSH/Telnet (ফলব্যাক)
- **Real-time Updates**: Socket.IO WebSocket সাথে তাত্ক্ষণিক UI রিফ্রেশ
- **Adapter Pattern**: নতুন vendor যোগ করা সহজ
- **Full CRUD Operations**: Device, ONU, Port ম্যানেজমেন্ট
- **Performance Monitoring**: CPU, Memory, Temperature মেট্রিক্স
- **Audit Trail**: সব অপারেশনের লগ সংরক্ষণ

## 📁 প্রজেক্ট স্ট্রাকচার

```
OLT Management System/
├── backend/                          # Flask Backend (Python)
│   ├── migrations/
│   │   └── create_olt_tables.sql    # MariaDB Schema
│   ├── models/
│   │   └── olt_models.py            # SQLAlchemy Models
│   ├── services/
│   │   ├── olt_adapter_base.py      # Base Adapter Class
│   │   ├── olt_snmp_adapter.py      # SNMP Implementation
│   │   ├── olt_cli_adapter.py       # SSH/Telnet Implementation
│   │   ├── olt_manager.py           # Adapter Factory
│   │   └── socketio_events.py       # WebSocket Events
│   ├── routes/
│   │   └── olt_routes.py            # Flask Blueprint Routes
│   └── config/
│       └── olt_socket_config.py     # Socket.IO Configuration
│
├── src/                              # React Frontend (TypeScript)
│   ├── main.tsx                      # Entry Point
│   ├── App.tsx                       # Main App Component
│   ├── App.css                       # App Styles
│   ├── index.css                     # Global Styles
│   ├── hooks/
│   │   ├── useOLTAPI.ts              # REST API Client Hook
│   │   └── useOLTWebSocket.ts        # Socket.IO Hook
│   └── components/
│       ├── OLTManagementDashboard.tsx # Main Dashboard
│       ├── OLTDeviceList.tsx          # Device Grid View
│       ├── OLTDeviceDetails.tsx       # Device Details Modal
│       ├── OLTRegisterDevice.tsx      # Registration Form
│       └── OLTONUDiscovery.tsx        # ONU Management
│
├── index.html                        # Vite HTML Entry
├── tsconfig.json                     # TypeScript Config
├── package.json                      # Node Dependencies
├── QUICK_START.md                    # দ্রুত শুরু গাইড
├── OLT_FLASK_REACT_SETUP.md          # বিস্তারিত সেটআপ
└── PROJECT_SUMMARY.md                # প্রজেক্ট সারসংক্ষেপ
```

## 🚀 দ্রুত শুরু

### Step 1: Database সেটআপ

```bash
# MariaDB এ SQL স্ক্রিপ্ট চালান
mysql -u root -p oltmanage < backend/migrations/create_olt_tables.sql
```

### Step 2: Flask Backend সেটআপ

```bash
# Python dependencies ইনস্টল করুন
pip install -r backend/requirements.txt

# Backend চালান (Port 5000)
cd backend
python app.py
```

### Step 3: React Frontend সেটআপ

```bash
# Node dependencies ইনস্টল করুন
pnpm install

# Frontend চালান (Port 3000, Vite proxy দিয়ে Flask এ রুট করা)
pnpm dev
```

### Step 4: ব্যবহার শুরু করুন

1. http://localhost:3000 খুলুন
2. "Register Device" বাটনে ক্লিক করুন
3. OLT ডিভাইসের তথ্য পূরণ করুন:
   - Device Model (ড্রপডাউন থেকে সিলেক্ট করুন)
   - IP Address
   - SSH/SNMP Credentials
4. "Register" বাটন চাপুন
5. ডিভাইস লিস্টে প্রদর্শিত হবে
6. "Discover ONUs" দিয়ে ONU খুঁজে বের করুন

## 🏗 Backend আর্কিটেকচার

### Adapter Pattern

```
BaseOLTAdapter (Abstract)
    ├── SNMPOLTAdapter (SNMP Protocol)
    └── CLIOLTAdapter (SSH/Telnet Protocol)

OLTManager (Factory)
    ├── Device registration
    ├── Adapter selection (SNMP first, fallback to SSH)
    └── Operation delegation
```

### REST API Endpoints

**Device Management**
- `GET /api/olt/devices` - সব ডিভাইস লিস্ট
- `POST /api/olt/devices` - নতুন ডিভাইস রেজিস্টার
- `PUT /api/olt/devices/<id>` - ডিভাইস আপডেট
- `DELETE /api/olt/devices/<id>` - ডিভাইস ডিলিট
- `GET /api/olt/devices/<id>/health` - ডিভাইস হেলথ চেক

**ONU Operations**
- `GET /api/olt/devices/<id>/onus` - ONU লিস্ট
- `POST /api/olt/devices/<id>/discover-onus` - ONU ডিসকভারি শুরু করুন
- `PUT /api/olt/devices/<id>/onus/<onu_id>` - ONU কনফিগার করুন
- `POST /api/olt/devices/<id>/onus/<onu_id>/reset` - ONU রিসেট করুন

**Port Operations**
- `GET /api/olt/devices/<id>/ports` - পোর্ট লিস্ট
- `PUT /api/olt/devices/<id>/ports/<port_id>` - পোর্ট কনফিগার করুন
- `POST /api/olt/devices/<id>/ports/<port_id>/enable` - পোর্ট এনেবল করুন
- `POST /api/olt/devices/<id>/ports/<port_id>/disable` - পোর্ট ডিসেবল করুন

### Socket.IO Events

**Client → Server**
- `connect` - ক্লায়েন্ট সংযোগ
- `start_monitoring` - ডিভাইস মনিটরিং শুরু করুন
- `stop_monitoring` - মনিটরিং থামান

**Server → Client**
- `device_status` - ডিভাইস স্ট্যাটাস আপডেট
- `metrics_update` - CPU/Memory/Temperature মেট্রিক্স
- `onu_discovered` - ONU ডিসকভার হয়েছে
- `port_status_changed` - পোর্ট স্ট্যাটাস পরিবর্তিত
- `operation_complete` - অপারেশন সম্পন্ন

## 🗄 Database Schema

### olt_devices
- `id` - অনন্য আইডি
- `model`, `vendor` - ডিভাইস তথ্য
- `ip_address`, `port` - নেটওয়ার্ক সেটিংস
- `connection_method` - SNMP/SSH/Telnet
- `snmp_community`, `username`, `password` - Credentials
- `status`, `cpu_usage`, `memory_usage`, `temperature` - মেট্রিক্স

### onus
- `id`, `device_id`, `port_id` - রেফারেন্স
- `status`, `serial_number`, `mac_address` - ONU তথ্য
- `ip_address`, `vlan_id` - নেটওয়ার্ক কনফিগ

### pon_ports, ethernet_ports
- Port-specific configuration এবং statistics

### device_metrics, operation_logs
- Performance data এবং audit trail

## 🎨 Frontend Components

**OLTManagementDashboard** - Main container
**OLTDeviceList** - Grid view সব ডিভাইসের
**OLTDeviceDetails** - Modal detail view
**OLTRegisterDevice** - Device registration form
**OLTONUDiscovery** - ONU management interface

## 📡 Real-time Features

Socket.IO WebSocket integration সাথে:
- Real-time device metrics streaming
- ONU discovery progress updates
- Port status change notifications
- Live alert/error notifications

## 🔒 নিরাপত্তা

- Input validation (Pydantic models)
- SQL injection প্রতিরোধ (parameterized queries)
- Password hashing/encryption
- CORS enabled for Flask
- Operation logging এবং audit trail

## 📚 ডকুমেন্টেশন

- **QUICK_START.md** - 5 মিনিটের সেটআপ গাইড
- **OLT_FLASK_REACT_SETUP.md** - বিস্তারিত ইনস্টলেশন
- **PROJECT_SUMMARY.md** - সম্পূর্ণ প্রজেক্ট ওভারভিউ

## 🛠 প্রয়োজনীয় প্যাকেজ

**Backend (Python 3.8+)**
```
flask
flask-sqlalchemy
flask-socketio
python-socketio
paramiko
pysnmp
python-dotenv
pymysql
```

**Frontend (Node.js 16+)**
```
react
react-dom
typescript
socket.io-client
axios
```

## 🤝 ভবিষ্যত উন্নতি

- [ ] Redis caching for performance
- [ ] LDAP/AD authentication
- [ ] Bulk ONU operations
- [ ] Advanced filtering and search
- [ ] Export reports (PDF/CSV)
- [ ] Multi-user role management
- [ ] Dark mode support

## 📞 সহায়তা

সমস্যার জন্য দেখুন:
1. Backend logs: `backend/logs/`
2. Browser console
3. Socket.IO connection status
4. Database connectivity

---

**Version**: 1.0.0
**Last Updated**: May 2026
**Author**: OLT Management Team
