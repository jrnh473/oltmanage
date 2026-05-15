# Database Service Abstraction Layer - Implementation Guide

## Overview

এই প্রজেক্টে একটি **Database Service Abstraction Layer** ব্যবহার করা হয়েছে যা database-agnostic এবং সম্পূর্ণভাবে replaceable।

### বর্তমান Implementation
- **File**: `services/database_service.py`
- **Class**: `SQLAlchemyDatabaseService`
- **Database**: MySQL/MariaDB (Flask-SQLAlchemy এর মাধ্যমে)

## আপনার নিজের Database কীভাবে Implement করবেন

### Step 1: নতুন Service Class তৈরি করুন

`services/database_service.py` ফাইলে `DatabaseService` abstract class রয়েছে যার সকল abstract methods implement করতে হবে।

```python
# Example: PostgreSQL implementation
from services.database_service import DatabaseService
import psycopg2

class PostgreSQLDatabaseService(DatabaseService):
    """PostgreSQL implementation"""
    
    def __init__(self, connection_string):
        self.conn_string = connection_string
        self.connection = psycopg2.connect(connection_string)
    
    def create_device(self, device_data):
        """Create device in PostgreSQL"""
        query = """
            INSERT INTO olt_devices 
            (id, model, vendor, ip_address, snmp_port, ...)
            VALUES (%s, %s, %s, %s, %s, ...)
        """
        cursor = self.connection.cursor()
        cursor.execute(query, (
            device_data['id'],
            device_data['model'],
            # ... rest of the fields
        ))
        self.connection.commit()
        return device_data
    
    # Implement all other abstract methods...
```

### Step 2: `app.py` Update করুন

```python
# Old
from services.database_service import SQLAlchemyDatabaseService
init_db_service(db)

# New
from services.database_service import PostgreSQLDatabaseService
db_service = PostgreSQLDatabaseService("postgresql://user:pass@localhost/oltmanage")
init_db_service(db_service)
```

### Step 3: Routes Update করুন (Optional)

যদি আপনার database implementation ভিন্ন হয়, তাহলে `routes/olt_routes.py` এ `init_db_service` function update করুন:

```python
def init_db_service(database_service):
    """Initialize database service with custom implementation"""
    global db_service
    db_service = database_service
```

## Database Service Methods

### Device Operations

| Method | Purpose | Returns |
|--------|---------|---------|
| `create_device(device_data)` | নতুন OLT device তৈরি করুন | Device dictionary |
| `get_device(device_id)` | Device ID দিয়ে device খুঁজুন | Device dict or None |
| `get_all_devices()` | সকল devices পান | List of devices |
| `get_device_by_ip(ip_address)` | IP address দিয়ে device খুঁজুন | Device dict or None |
| `update_device(device_id, updates)` | Device update করুন | Boolean |
| `delete_device(device_id)` | Device delete করুন | Boolean |

### PON Port Operations

| Method | Purpose | Returns |
|--------|---------|---------|
| `create_pon_port(port_data)` | নতুন PON port তৈরি করুন | PON port dictionary |
| `get_pon_port(port_id)` | PON port খুঁজুন | PON port dict or None |
| `get_pon_ports_by_device(device_id)` | Device এর সকল PON ports | List of ports |
| `update_pon_port(port_id, updates)` | PON port update | Boolean |
| `delete_pon_port(port_id)` | PON port delete | Boolean |

### ONU Operations

| Method | Purpose | Returns |
|--------|---------|---------|
| `create_onu(onu_data)` | নতুন ONU তৈরি করুন | ONU dictionary |
| `get_onu(onu_id)` | ONU খুঁজুন | ONU dict or None |
| `get_onus_by_device(device_id)` | Device এর সকল ONUs | List of ONUs |
| `get_onus_by_port(device_id, port_id)` | Port এর ONUs | List of ONUs |
| `update_onu(onu_id, updates)` | ONU update | Boolean |
| `delete_onu(onu_id)` | ONU delete | Boolean |
| `delete_onus_by_device(device_id)` | Device এর সকল ONUs delete | Boolean |
| `batch_create_onus(device_id, onus_data)` | Multiple ONUs একসাথে তৈরি | List of ONUs |
| `batch_update_onus(updates_list)` | Multiple ONUs একসাথে update | Boolean |

### Ethernet Port Operations

| Method | Purpose | Returns |
|--------|---------|---------|
| `create_ethernet_port(port_data)` | নতুন Ethernet port তৈরি করুন | Port dictionary |
| `get_ethernet_port(port_id)` | Ethernet port খুঁজুন | Port dict or None |
| `get_ethernet_ports_by_device(device_id)` | Device এর Ethernet ports | List of ports |
| `update_ethernet_port(port_id, updates)` | Ethernet port update | Boolean |
| `delete_ethernet_port(port_id)` | Ethernet port delete | Boolean |

### Metric & Log Operations

| Method | Purpose | Returns |
|--------|---------|---------|
| `create_metric(metric_data)` | নতুন metric তৈরি করুন | Metric dictionary |
| `get_metrics_by_device(device_id, limit)` | Device metrics পান | List of metrics |
| `create_log(log_data)` | নতুন log তৈরি করুন | Log dictionary |
| `get_logs_by_device(device_id, limit)` | Device logs পান | List of logs |

## Data Format Examples

### Device Data Format
```python
device_data = {
    'id': 'uuid-string',
    'model': 'FD1208S',
    'vendor': 'C-DATA',
    'ip_address': '192.168.1.100',
    'snmp_port': 161,
    'ssh_port': 22,
    'snmp_community': 'public',
    'username': 'admin',
    'password': 'password',
    'connection_method': 'SNMP',
    'status': 'ONLINE'
}
```

### ONU Data Format
```python
onu_data = {
    'id': 'ONU-ID-string',
    'device_id': 'device-uuid',
    'port_id': 1,
    'onu_index': 1,
    'serial_number': 'SERIAL123',
    'mac_address': '00:11:22:33:44:55',
    'ip_address': '192.168.2.1',
    'status': 'ONLINE',
    'vendor_name': 'Vendor Name',
    'optical_power_downstream': -5.5,
    'optical_power_upstream': 4.2,
    'distance_km': 15.5
}
```

### PON Port Data Format
```python
port_data = {
    'id': 'port-id-string',
    'device_id': 'device-uuid',
    'port_number': 1,
    'port_name': 'PON 1/1',
    'status': 'UP',
    'optical_power_downstream': -5.0,
    'optical_power_upstream': 4.0,
    'wavelength': '1490nm',
    'onu_count': 2,
    'enabled': True,
    'admin_status': 'UP'
}
```

## Implementation Checklist

যখন আপনি নিজের database implement করবেন:

- [ ] নতুন DatabaseService subclass তৈরি করুন
- [ ] সকল abstract methods implement করুন
- [ ] Database connection initialize করুন
- [ ] Error handling সঠিকভাবে করুন (try-except blocks)
- [ ] সকল database operations atomic হওয়া নিশ্চিত করুন
- [ ] Proper logging যোগ করুন
- [ ] Database schema তৈরি করুন (migrations)
- [ ] `app.py` এ নতুন service initialize করুন
- [ ] Testing করুন - সকল CRUD operations কাজ করছে কি না
- [ ] Performance optimization (indices, connection pooling)

## কীভাবে Routes কাজ করে

Routes এখন database service layer ব্যবহার করে:

```python
# Example: Device registration
@olt_bp.route('/devices', methods=['POST'])
async def register_device():
    # ... validation ...
    
    # Create device using service
    device_data = {...}
    created_device = db_service.create_device(device_data)
    
    # Update device using service
    db_service.update_device(device_id, {'status': 'ONLINE'})
    
    # Get device using service
    final_device = db_service.get_device(device_id)
```

যেকোনো database implementation দিয়েও routes এভাবেই চলবে, শুধু underlying database different হবে।

## বর্তমানে কী ঠিক হয়েছে

### সমস্যা:
- Device registration এর পর PON Ports/ONUs data নেই
- "Device not registered" error আসছিল

### সমাধান:
1. Database abstraction layer যুক্ত করেছি
2. Device discovery সম্পূর্ণ করেছি - এখন ports discover হবে
3. Ports discovery data এখন database-এ save হবে
4. Service layer দিয়ে সকল operations centralized হয়েছে

এখন device registration এর পর automatically ports এবং ONUs discover হবে এবং database-এ save থাকবে।
