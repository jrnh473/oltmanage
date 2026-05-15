# Quick Start Guide - OLT Management System

## ৫ মিনিটে সেটআপ করুন

### Phase 1: Database সেটআপ (1 মিনিট)

```bash
# MariaDB এ login করুন
mysql -u root -p

# Database তৈরি করুন
CREATE DATABASE oltmanage CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# Tables তৈরি করুন
mysql -u root -p oltmanage < backend/migrations/create_olt_tables.sql
```

### Phase 2: Backend সেটআপ (2 মিনিট)

```bash
cd backend

# Python virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac: venv\Scripts\activate (Windows)

# Install packages
pip install flask flask-sqlalchemy flask-socketio python-socketio
pip install pysnmp paramiko flask-cors pydantic python-dotenv pymysql

# Create .env file
cat > .env << 'EOF'
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=mysql+pymysql://root:yourpassword@localhost/oltmanage
SECRET_KEY=dev-secret-key-change-in-production
FRONTEND_URL=http://localhost:3000
EOF

# Run Flask
python app.py
```

### Phase 3: Frontend সেটআপ (2 মিনিট)

```bash
cd ../frontend  # or wherever your React app is

# Create .env file
cat > .env << 'EOF'
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_SOCKET_URL=http://localhost:5000
EOF

# Add to your App.tsx or main component
import { OLTManagementDashboard } from './components/OLTManagementDashboard';

// In your render:
<OLTManagementDashboard />

# Start development server
npm run dev  # or yarn dev
```

---

## এখন ব্যবহার করুন

1. **ব্রাউজার খুলুন**: http://localhost:3000
2. **Device register করুন**: "Register Device" বাটন ক্লিক করুন
3. **তথ্য পূরণ করুন**:
   - Model: `FD1104SN` (C-DATA)
   - Vendor: `C-DATA` (auto-filled)
   - IP Address: `192.168.1.100` (আপনার OLT IP)
   - SNMP Community: `public`
   - Username/Password: প্রয়োজন হলে পূরণ করুন

4. **Device register করুন** → Status "ONLINE" হওয়ার জন্য অপেক্ষা করুন

5. **ONU discover করুন**:
   - Device select করুন
   - "Start Discovery" বাটন ক্লিক করুন
   - Real-time updates Socket.IO এর মাধ্যমে আসবে

---

## মূল ফাইল যেখানে কি আছে

| File | উদ্দেশ্য |
|------|---------|
| `backend/models/olt_models.py` | Database models (OLTDevice, ONU, Ports) |
| `backend/services/olt_manager.py` | SNMP/SSH adapter factory & manager |
| `backend/routes/olt_routes.py` | REST API endpoints (18টি) |
| `backend/services/socketio_events.py` | Real-time WebSocket events |
| `src/hooks/useOLTAPI.ts` | React API client hook |
| `src/hooks/useOLTWebSocket.ts` | React Socket.IO hook |
| `src/components/OLTManagementDashboard.tsx` | Main dashboard component |

---

## Common Commands

```bash
# Backend logs দেখুন
tail -f backend/app.log

# Database status check করুন
mysql -u root -p oltmanage -e "SHOW TABLES;"

# Device list দেখুন (API call)
curl http://localhost:5000/api/olt/devices

# Supported models দেখুন
curl http://localhost:5000/api/olt/supported-models

# Health check করুন
curl http://localhost:5000/api/health
```

---

## Troubleshooting

### Backend starts কিন্তু Database error দেখা দিচ্ছে
```bash
# .env file check করুন
cat backend/.env

# Database connection test করুন
mysql -u root -p -h localhost
```

### Frontend can't connect to backend
```bash
# CORS is enabled
# Check: backend আছে কিনা http://localhost:5000
# Check: frontend .env REACT_APP_API_URL সঠিক কিনা
```

### Socket.IO not connected
```bash
# Check console in browser DevTools
# Verify: backend Socket.IO server running
# Verify: frontend REACT_APP_SOCKET_URL = http://localhost:5000
```

---

## পরবর্তী পদক্ষেপ

1. **Real SNMP integrate করুন**: 
   - `pysnmp` library ব্যবহার করুন `backend/services/olt_snmp_adapter.py` এ

2. **Real SSH integrate করুন**:
   - `paramiko` library ব্যবহার করুন `backend/services/olt_cli_adapter.py` এ

3. **Authentication যোগ করুন**:
   - JWT tokens implement করুন `/api/auth` routes এ
   - Backend protected routes এ auth middleware যোগ করুন

4. **Monitoring dashboard যোগ করুন**:
   - Device metrics সংগ্রহ করুন periodically
   - Charts render করুন trending data এর জন্য

5. **Production deployment**:
   - gunicorn/uwsgi use করুন Flask এর জন্য
   - nginx reverse proxy configure করুন
   - SSL/TLS setup করুন

---

## যোগাযোগ করুন

কোনো প্রশ্ন থাকলে documentation files দেখুন:
- `OLT_FLASK_REACT_SETUP.md` - সম্পূর্ণ setup guide
- `OLT_ARCHITECTURE.md` - সিস্টেম ডিজাইন
- `IMPLEMENTATION_GUIDE.md` - implementation details
