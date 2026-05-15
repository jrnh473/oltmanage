# OLT Management System - Flask + React Integration Guide

একটি সম্পূর্ণ Multi-Vendor OLT Management System যা Flask Backend এবং React Frontend এর সাথে Socket.IO Real-time Communication সাপোর্ট করে।

## সিস্টেম আর্কিটেকচার

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (Port 3000)               │
│  ┌──────────┐  ┌──────────────────┐  ┌─────────────────┐   │
│  │ Components│  │ useOLTAPI Hook   │  │ useOLTWebSocket │   │
│  │ - List   │  │ - REST calls      │  │ - Socket.IO     │   │
│  │ - Details│  │ - Device Mgmt    │  │ - Real-time     │   │
│  │ - ONU    │  │ - ONU ops        │  │ - Live updates  │   │
│  │ - Ports  │  │ - Port control   │  │ - Events        │   │
│  └──────────┘  └──────────────────┘  └─────────────────┘   │
└───────────────────────────┬──────────────────────────────────┘
                            │ Axios + Socket.IO
┌───────────────────────────▼──────────────────────────────────┐
│              Flask Backend (Port 5000)                        │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │ REST API Routes  │  │ Socket.IO Events │                 │
│  │ /api/olt/*       │  │ - Device updates │                 │
│  │ - Devices        │  │ - ONU discovery  │                 │
│  │ - ONUs           │  │ - Port status    │                 │
│  │ - Ports          │  │ - Real-time data │                 │
│  └──────────────────┘  └──────────────────┘                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Adapter Pattern Layer                        │   │
│  │  ┌──────────────┐  ┌──────────────────────┐         │   │
│  │  │ Base Adapter │  │ OLT Manager (Factory)│         │   │
│  │  └──────────────┘  └──────────────────────┘         │   │
│  │        ▲                       ▲                      │   │
│  │        │                       │                      │   │
│  │  ┌─────┴──────┬─────────────┬──┴───────┐            │   │
│  │  │ SNMP       │ CLI (SSH)   │ CLI      │            │   │
│  │  │ Adapter    │ Adapter     │(Telnet)  │            │   │
│  │  │ (Primary)  │ (Fallback)  │          │            │   │
│  │  └────────────┴─────────────┴──────────┘            │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────────┬──────────────────────────────────┘
                            │ SQL queries
┌───────────────────────────▼──────────────────────────────────┐
│           MariaDB (OLTManage Database)                        │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ Tables:                                              │    │
│  │ - olt_devices (OLT Equipment)                        │    │
│  │ - onus (ONUs Connected)                              │    │
│  │ - pon_ports (PON Ports)                              │    │
│  │ - ethernet_ports (ETH Ports)                         │    │
│  │ - device_metrics (Performance History)               │    │
│  │ - device_logs (Operation Logs)                       │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

## প্রয়োজনীয় প্যাকেজ

### Backend (Flask)
```bash
pip install flask flask-sqlalchemy flask-socketio python-socketio
pip install pysnmp paramiko flask-cors pydantic python-dotenv
pip install pymysql  # For MariaDB
```

### Frontend (React)
```bash
npm install axios socket.io-client
```

## ফাইল স্ট্রাকচার

```
backend/
├── models/
│   └── olt_models.py          # SQLAlchemy models (6 tables)
├── services/
│   ├── olt_adapter_base.py    # Base Adapter class (abstract)
│   ├── olt_snmp_adapter.py    # SNMP implementation
│   ├── olt_cli_adapter.py     # SSH/Telnet implementation
│   ├── olt_manager.py         # Adapter Factory + Manager
│   └── socketio_events.py     # Socket.IO handlers
├── routes/
│   └── olt_routes.py          # Flask Blueprint routes (18 endpoints)
├── config/
│   └── olt_socket_config.py   # Flask + Socket.IO initialization
└── migrations/
    └── create_olt_tables.sql  # Database schema

src/
├── hooks/
│   ├── useOLTAPI.ts           # REST API client hook
│   └── useOLTWebSocket.ts     # Socket.IO hook
└── components/
    ├── OLTManagementDashboard.tsx  # Main dashboard
    ├── OLTDeviceList.tsx           # Device list
    ├── OLTDeviceDetails.tsx        # Device details modal
    ├── OLTRegisterDevice.tsx       # Registration form
    └── OLTONUDiscovery.tsx         # ONU management
```

## স্টেপ বাই স্টেপ সেটআপ

### 1. Database সেটআপ

```bash
# MariaDB এ নতুন database তৈরি করুন
mysql -u root -p
> CREATE DATABASE oltmanage CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
> EXIT;

# Migration script চালান
mysql -u root -p oltmanage < backend/migrations/create_olt_tables.sql
```

### 2. Flask Backend সেটআপ

```bash
cd backend

# Virtual environment তৈরি করুন
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Requirements install করুন
pip install -r requirements.txt

# Environment variables সেটআপ
cat > .env << EOF
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=mysql+pymysql://root:password@localhost/oltmanage
SECRET_KEY=your-secret-key-here
FRONTEND_URL=http://localhost:3000
EOF

# Flask app চালান (app.py তে init করতে হবে)
python app.py
```

### 3. Flask App Initialization (app.py)

```python
from flask import Flask
from config.olt_socket_config import init_olt_app

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/oltmanage'
app.config['SECRET_KEY'] = 'your-secret-key'

# Initialize OLT system with Socket.IO
socketio = init_olt_app(app)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
```

### 4. React Frontend সেটআপ

```bash
cd frontend

# Environment variables সেটআপ
cat > .env << EOF
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_SOCKET_URL=http://localhost:5000
EOF

# আপনার main App component এ OLT Dashboard যোগ করুন
# import { OLTManagementDashboard } from './components/OLTManagementDashboard';

# <OLTManagementDashboard /> ব্যবহার করুন
```

## সাপোর্টেড OLT মডেল

সমস্ত মডেল SNMP-প্রথম, SSH/Telnet ফলব্যাক সাপোর্ট করে:

| Vendor | মডেল | PON পোর্ট | ETH পোর্ট |
|--------|-------|----------|----------|
| C-DATA | FD1104SN | 4 | 2 |
| C-DATA | FD1204S | 4 | 2 |
| C-DATA | FD1208S | 8 | 4 |
| C-DATA | FD1304E | 4 | 2 |
| ECOM | E08GP | 8 | 4 |
| ECOM | E1204ES | 4 | 2 |
| ECOM | E1208ES | 8 | 4 |
| Connect+ | CPE-804-2S+ | 4 | 2 |
| VSOL | 1600-G1 | 4 | 2 |
| VSOL | V1601E04 | 4 | 2 |
| VSOL | V1600D8 | 8 | 4 |
| BDCOM | 1608V | 8 | 4 |
| BDCOM | P3608B | 8 | 4 |
| DBC | 3310-2AC | 4 | 2 |
| AVEIS | AV-OLT-E04 | 4 | 2 |
| HSGQ | HSGQ-OLT-E04 | 4 | 2 |
| PHYHOME | FHL-104C | 4 | 2 |

## REST API এন্ডপয়েন্ট

### Device Management
- `GET /api/olt/devices` - সব devices পান
- `GET /api/olt/devices/{id}` - নির্দিষ্ট device
- `POST /api/olt/devices` - নতুন device register
- `PUT /api/olt/devices/{id}` - device আপডেট
- `DELETE /api/olt/devices/{id}` - device ডিলিট
- `GET /api/olt/devices/{id}/health` - health check

### ONU Management
- `GET /api/olt/devices/{id}/onus` - সব ONUs
- `POST /api/olt/devices/{id}/onus/discover` - ONU discovery
- `POST /api/olt/devices/{id}/onus/{onu_id}/configure` - ONU কনফিগার
- `POST /api/olt/devices/{id}/onus/{onu_id}/reset` - ONU রিসেট

### Port Management
- `GET /api/olt/devices/{id}/ports` - সব ports
- `POST /api/olt/devices/{id}/ports/{port_id}/enable` - port enable
- `POST /api/olt/devices/{id}/ports/{port_id}/disable` - port disable

### System
- `GET /api/olt/supported-models` - সাপোর্টেড মডেলস
- `GET /api/health` - সার্ভার health check

## Socket.IO ইভেন্ট

### Client → Server
```
- subscribe_device (device_id)
- unsubscribe_device (device_id)
- get_device_status (device_id)
- discover_onus_start (device_id, port_id?)
- configure_onu (device_id, onu_id, config)
- reset_onu (device_id, onu_id)
- get_port_info (device_id, port_id, port_type)
```

### Server → Client (Real-time)
```
- device_update (device_id, metrics)
- device_status (status, cpu, memory, temp, onu_count)
- discovery_started, discovery_progress, discovery_complete, discovery_error
- onu_status_change (onu_id, status)
- configure_started, configure_complete, configure_error
- reset_started, reset_complete, reset_error
- port_status_change (port_id, status, port_type)
- port_info (port details)
```

## React Hooks ব্যবহার

### useOLTAPI - REST API Access
```typescript
const { 
  getDevices, 
  registerDevice, 
  discoverONUs, 
  resetONU,
  loading, 
  error 
} = useOLTAPI();

// Device list পান
const devices = await getDevices();

// নতুন device register করুন
const device = await registerDevice({
  model: 'FD1104SN',
  vendor: 'C-DATA',
  ip_address: '192.168.1.100',
  snmp_community: 'public'
});
```

### useOLTWebSocket - Real-time Updates
```typescript
const {
  isConnected,
  deviceUpdates,
  subscribeToDevice,
  discoverONUs,
  resetONU
} = useOLTWebSocket();

// Device subscribe করুন
useEffect(() => {
  subscribeToDevice(deviceId);
  return () => unsubscribeFromDevice(deviceId);
}, [deviceId]);

// Real-time updates পান
useEffect(() => {
  if (deviceUpdates[deviceId]) {
    // Update UI with new device data
  }
}, [deviceUpdates]);
```

## কাস্টম Vendor যোগ করা

নতুন vendor support যোগ করতে:

1. **olt_manager.py তে মডেল যোগ করুন:**
```python
SUPPORTED_OLT_MODELS = {
    'MODEL_NAME': {'vendor': 'VENDOR', 'pon_ports': 4, 'eth_ports': 2},
    # ...
}
```

2. **CLI Commands যোগ করুন (olt_cli_adapter.py):**
```python
VENDOR_COMMANDS = {
    'VENDOR': {
        'info': 'show version',
        'pon_status': 'show interface pon',
        # ... more commands
    }
}
```

3. **Test করুন - ONU discovery চালান**

## Troubleshooting

### Database Connection Error
```
Error: (pymysql.Error) (1045, "Access denied...")
Solution: MariaDB credentials check করুন .env ফাইলে
```

### Socket.IO Connection Failed
```
Error: WebSocket is closed before the connection is established
Solution: Backend CORS settings এবং frontend URL verify করুন
```

### SNMP Timeout
```
Error: Timeout getting device info
Solution: Device IP accessibility check করুন, firewall rules verify করুন
```

## পারফরম্যান্স Optimization

1. **Connection Pooling** - SQLAlchemy pool_size set করুন
2. **Caching** - Redis add করুন device info এর জন্য
3. **Async Operations** - Background tasks এর জন্য Celery use করুন
4. **Database Indexes** - created_at, device_id, status এ indices যোগ করুন

## Security বিবেচনা

1. ✅ HTTPS করুন production এ
2. ✅ JWT authentication implement করুন API routes এ
3. ✅ Password encryption করুন database তে
4. ✅ Rate limiting যোগ করুন API endpoints এ
5. ✅ Input validation করুন সব endpoints এ

## পরবর্তী উন্নতি

- [ ] Real SNMP library integration (pysnmp/easysnmp)
- [ ] Real SSH library integration (paramiko)
- [ ] Prometheus metrics export
- [ ] Performance trending charts
- [ ] Automated health check background task
- [ ] Device configuration backup
- [ ] Multi-user authentication
- [ ] Audit logging

## সহায়তা

Documentation: OLT_ARCHITECTURE.md, IMPLEMENTATION_GUIDE.md
Issues: GitHub issues tracker এ লগ করুন
Discussions: কমিউনিটি ফোরাম check করুন
