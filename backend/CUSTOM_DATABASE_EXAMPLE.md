# কাস্টম Database Implementation Example

এই দল্ল আপনার নিজের database দিয়ে কীভাবে service replace করতে হয় তা দেখায়।

## Example 1: PostgreSQL + psycopg2

### Step 1: নতুন Service Class তৈরি করুন

**File**: `services/database_service.py` এ এই class যোগ করুন:

```python
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import Dict, List, Optional, Any

class PostgreSQLDatabaseService(DatabaseService):
    """PostgreSQL implementation using psycopg2"""
    
    def __init__(self, connection_string: str):
        """
        Initialize PostgreSQL connection
        
        Args:
            connection_string: PostgreSQL connection string
            e.g., "postgresql://user:password@localhost:5432/oltmanage"
        """
        self.conn_string = connection_string
        self.connection = psycopg2.connect(connection_string)
    
    def _execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Execute SELECT query"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Query execution error: {str(e)}")
            raise
    
    def _execute_insert(self, query: str, params: tuple) -> None:
        """Execute INSERT/UPDATE/DELETE query"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Insert execution error: {str(e)}")
            raise
    
    # ==================== Device Operations ====================
    
    def create_device(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        query = """
            INSERT INTO olt_devices 
            (id, model, vendor, ip_address, snmp_port, ssh_port, 
             snmp_community, username, password, connection_method, status, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            device_data.get('id'),
            device_data['model'],
            device_data['vendor'],
            device_data['ip_address'],
            device_data.get('snmp_port', 161),
            device_data.get('ssh_port', 22),
            device_data.get('snmp_community', 'public'),
            device_data.get('username'),
            device_data.get('password'),
            device_data.get('connection_method', 'SNMP'),
            device_data.get('status', 'UNKNOWN'),
            datetime.utcnow(),
            datetime.utcnow()
        )
        self._execute_insert(query, params)
        return device_data
    
    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM olt_devices WHERE id = %s"
        result = self._execute_query(query, (device_id,))
        return dict(result[0]) if result else None
    
    def get_all_devices(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM olt_devices"
        return [dict(row) for row in self._execute_query(query)]
    
    def get_device_by_ip(self, ip_address: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM olt_devices WHERE ip_address = %s"
        result = self._execute_query(query, (ip_address,))
        return dict(result[0]) if result else None
    
    def update_device(self, device_id: str, updates: Dict[str, Any]) -> bool:
        if not updates:
            return True
        
        set_clause = ", ".join([f"{key} = %s" for key in updates.keys()])
        set_clause += ", updated_at = %s"
        
        query = f"UPDATE olt_devices SET {set_clause} WHERE id = %s"
        values = list(updates.values()) + [datetime.utcnow(), device_id]
        
        try:
            self._execute_insert(query, tuple(values))
            return True
        except:
            return False
    
    def delete_device(self, device_id: str) -> bool:
        query = "DELETE FROM olt_devices WHERE id = %s"
        try:
            self._execute_insert(query, (device_id,))
            return True
        except:
            return False
    
    # ==================== ONU Operations ====================
    
    def create_onu(self, onu_data: Dict[str, Any]) -> Dict[str, Any]:
        query = """
            INSERT INTO onus 
            (id, device_id, port_id, onu_index, serial_number, mac_address, 
             ip_address, status, vendor_name, hardware_version, software_version,
             optical_power_downstream, optical_power_upstream, distance_km,
             vlan_id, bandwidth_upstream, bandwidth_downstream, description,
             created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            onu_data.get('id'),
            onu_data['device_id'],
            onu_data['port_id'],
            onu_data['onu_index'],
            onu_data.get('serial_number'),
            onu_data.get('mac_address'),
            onu_data.get('ip_address'),
            onu_data.get('status', 'OFFLINE'),
            onu_data.get('vendor_name'),
            onu_data.get('hardware_version'),
            onu_data.get('software_version'),
            onu_data.get('optical_power_downstream'),
            onu_data.get('optical_power_upstream'),
            onu_data.get('distance_km'),
            onu_data.get('vlan_id'),
            onu_data.get('bandwidth_upstream'),
            onu_data.get('bandwidth_downstream'),
            onu_data.get('description'),
            datetime.utcnow(),
            datetime.utcnow()
        )
        self._execute_insert(query, params)
        return onu_data
    
    def get_onu(self, onu_id: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM onus WHERE id = %s"
        result = self._execute_query(query, (onu_id,))
        return dict(result[0]) if result else None
    
    def get_onus_by_device(self, device_id: str) -> List[Dict[str, Any]]:
        query = "SELECT * FROM onus WHERE device_id = %s ORDER BY port_id, onu_index"
        return [dict(row) for row in self._execute_query(query, (device_id,))]
    
    def get_onus_by_port(self, device_id: str, port_id: int) -> List[Dict[str, Any]]:
        query = "SELECT * FROM onus WHERE device_id = %s AND port_id = %s ORDER BY onu_index"
        return [dict(row) for row in self._execute_query(query, (device_id, port_id))]
    
    def update_onu(self, onu_id: str, updates: Dict[str, Any]) -> bool:
        if not updates:
            return True
        
        set_clause = ", ".join([f"{key} = %s" for key in updates.keys()])
        set_clause += ", updated_at = %s"
        
        query = f"UPDATE onus SET {set_clause} WHERE id = %s"
        values = list(updates.values()) + [datetime.utcnow(), onu_id]
        
        try:
            self._execute_insert(query, tuple(values))
            return True
        except:
            return False
    
    def delete_onu(self, onu_id: str) -> bool:
        query = "DELETE FROM onus WHERE id = %s"
        try:
            self._execute_insert(query, (onu_id,))
            return True
        except:
            return False
    
    def delete_onus_by_device(self, device_id: str) -> bool:
        query = "DELETE FROM onus WHERE device_id = %s"
        try:
            self._execute_insert(query, (device_id,))
            return True
        except:
            return False
    
    def batch_create_onus(self, device_id: str, onus_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Bulk insert ONUs"""
        try:
            with self.connection.cursor() as cursor:
                for onu_data in onus_data:
                    onu_data['device_id'] = device_id
                    self.create_onu(onu_data)
            return onus_data
        except Exception as e:
            logger.error(f"Batch create error: {str(e)}")
            raise
    
    def batch_update_onus(self, updates_list: List[tuple]) -> bool:
        try:
            for onu_id, updates in updates_list:
                self.update_onu(onu_id, updates)
            return True
        except:
            return False
    
    # ==================== PON Port Operations ====================
    
    def create_pon_port(self, port_data: Dict[str, Any]) -> Dict[str, Any]:
        query = """
            INSERT INTO pon_ports
            (id, device_id, port_number, port_name, status,
             optical_power_downstream, optical_power_upstream, wavelength,
             onu_count, enabled, admin_status, description, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            port_data.get('id'),
            port_data['device_id'],
            port_data['port_number'],
            port_data.get('port_name'),
            port_data.get('status', 'DOWN'),
            port_data.get('optical_power_downstream'),
            port_data.get('optical_power_upstream'),
            port_data.get('wavelength'),
            port_data.get('onu_count', 0),
            port_data.get('enabled', True),
            port_data.get('admin_status', 'UP'),
            port_data.get('description'),
            datetime.utcnow(),
            datetime.utcnow()
        )
        self._execute_insert(query, params)
        return port_data
    
    def get_pon_ports_by_device(self, device_id: str) -> List[Dict[str, Any]]:
        query = "SELECT * FROM pon_ports WHERE device_id = %s ORDER BY port_number"
        return [dict(row) for row in self._execute_query(query, (device_id,))]
    
    def update_pon_port(self, port_id: str, updates: Dict[str, Any]) -> bool:
        if not updates:
            return True
        
        set_clause = ", ".join([f"{key} = %s" for key in updates.keys()])
        set_clause += ", updated_at = %s"
        
        query = f"UPDATE pon_ports SET {set_clause} WHERE id = %s"
        values = list(updates.values()) + [datetime.utcnow(), port_id]
        
        try:
            self._execute_insert(query, tuple(values))
            return True
        except:
            return False
    
    # ==================== Remaining Methods ====================
    # ... similarly implement ethernet_ports, metrics, logs ...
```

### Step 2: app.py Update করুন

```python
# backend/app.py

# Old initialization:
# from services.database_service import SQLAlchemyDatabaseService
# init_db_service(db)

# New initialization:
from services.database_service import PostgreSQLDatabaseService
from routes.olt_routes import init_db_service

# Create PostgreSQL service
postgres_service = PostgreSQLDatabaseService(
    "postgresql://user:password@localhost:5432/oltmanage"
)

# Initialize with new service
init_db_service(postgres_service)
```

### Step 3: Dependencies Update করুন

```bash
# requirements.txt এ যোগ করুন:
psycopg2-binary>=2.9.0
```

## Example 2: MongoDB

```python
from pymongo import MongoClient
from bson.objectid import ObjectId

class MongoDBDatabaseService(DatabaseService):
    """MongoDB implementation"""
    
    def __init__(self, connection_string: str):
        self.client = MongoClient(connection_string)
        self.db = self.client.oltmanage
    
    def create_device(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        result = self.db.devices.insert_one({
            '_id': device_data['id'],
            'model': device_data['model'],
            'vendor': device_data['vendor'],
            'ip_address': device_data['ip_address'],
            'status': device_data.get('status', 'UNKNOWN'),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            # ... other fields
        })
        return device_data
    
    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        device = self.db.devices.find_one({'_id': device_id})
        if device:
            device['id'] = device.pop('_id')
        return device
    
    # ... implement other methods similarly ...
```

## কী মনে রাখতে হবে

1. **সকল methods implement করুন** - abstract class এর সকল methods override করতে হবে
2. **Error handling** - সকল database operations এ try-except রাখুন
3. **Data format সমান রাখুন** - returns همলে always dictionary হতে হবে
4. **Connection management** - database connection properly close করুন
5. **Transactions** - যেখানে multiple operations আছে সেখানে transaction ব্যবহার করুন
6. **Logging** - সকল errors log করুন

## Testing

নতুন service test করার জন্য:

```python
# Test script
from services.database_service import PostgreSQLDatabaseService

service = PostgreSQLDatabaseService("postgresql://user:pass@localhost/oltmanage")

# Test device operations
device = service.create_device({
    'id': 'test-123',
    'model': 'FD1208S',
    'vendor': 'C-DATA',
    'ip_address': '192.168.1.100'
})

retrieved = service.get_device('test-123')
print("Create & Get:", retrieved)

# Test update
service.update_device('test-123', {'status': 'ONLINE'})
updated = service.get_device('test-123')
print("Updated:", updated)

# Test delete
service.delete_device('test-123')
print("Deleted")
```

এভাবে সহজেই আপনার নিজের database implementation করতে পারবেন!
