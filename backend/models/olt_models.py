# models/olt_models.py

from extensions import db
from datetime import datetime
import uuid


class OLTDevice(db.Model):
    """OLT Device Model"""
    __tablename__ = 'olt_devices'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    model = db.Column(db.String(100), nullable=False)
    vendor = db.Column(db.String(50), nullable=False)
    ip_address = db.Column(db.String(50), nullable=False)
    snmp_port = db.Column(db.Integer, default=161)
    ssh_port = db.Column(db.Integer, default=22)
    snmp_community = db.Column(db.String(255))
    username = db.Column(db.String(100))
    password = db.Column(db.String(255))
    connection_method = db.Column(db.String(20), default='SNMP')
    status = db.Column(db.String(20), default='UNKNOWN')
    cpu_usage = db.Column(db.Float, default=0.0)
    memory_usage = db.Column(db.Float, default=0.0)
    temperature = db.Column(db.Float, default=0.0)
    uptime_seconds = db.Column(db.Integer, default=0)
    firmware_version = db.Column(db.String(100))
    serial_number = db.Column(db.String(100))
    total_onu_count = db.Column(db.Integer, default=0)
    online_onu_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_check_at = db.Column(db.DateTime)
    
    # Relationships
    onus = db.relationship('ONU', backref='device', lazy=True, cascade='all, delete-orphan')
    pon_ports = db.relationship('PONPort', backref='device', lazy=True, cascade='all, delete-orphan')
    ethernet_ports = db.relationship('EthernetPort', backref='device', lazy=True, cascade='all, delete-orphan')
    metrics = db.relationship('DeviceMetric', backref='device', lazy=True, cascade='all, delete-orphan')
    logs = db.relationship('DeviceLog', backref='device', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'model': self.model,
            'vendor': self.vendor,
            'ip_address': self.ip_address,
            'status': self.status,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'temperature': self.temperature,
            'uptime_seconds': self.uptime_seconds,
            'firmware_version': self.firmware_version,
            'serial_number': self.serial_number,
            'total_onu_count': self.total_onu_count,
            'online_onu_count': self.online_onu_count,
            'last_check_at': self.last_check_at.isoformat() if self.last_check_at else None,
            'created_at': self.created_at.isoformat()
        }


class ONU(db.Model):
    """ONU (Optical Network Unit) Model"""
    __tablename__ = 'onus'
    
    id = db.Column(db.String(100), primary_key=True)
    device_id = db.Column(db.String(36), db.ForeignKey('olt_devices.id'), nullable=False)
    port_id = db.Column(db.Integer, nullable=False)
    onu_index = db.Column(db.Integer, nullable=False)
    serial_number = db.Column(db.String(100))
    mac_address = db.Column(db.String(20))
    ip_address = db.Column(db.String(50))
    status = db.Column(db.String(20), default='OFFLINE')
    vendor_name = db.Column(db.String(100))
    hardware_version = db.Column(db.String(100))
    software_version = db.Column(db.String(100))
    optical_power_downstream = db.Column(db.Float)
    optical_power_upstream = db.Column(db.Float)
    distance_km = db.Column(db.Float)
    vlan_id = db.Column(db.Integer)
    bandwidth_upstream = db.Column(db.Integer)
    bandwidth_downstream = db.Column(db.Integer)
    description = db.Column(db.String(255))
    last_state_change = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'port_id': self.port_id,
            'onu_index': self.onu_index,
            'serial_number': self.serial_number,
            'mac_address': self.mac_address,
            'ip_address': self.ip_address,
            'status': self.status,
            'vendor_name': self.vendor_name,
            'optical_power_downstream': self.optical_power_downstream,
            'optical_power_upstream': self.optical_power_upstream,
            'distance_km': self.distance_km,
            'vlan_id': self.vlan_id,
            'bandwidth_upstream': self.bandwidth_upstream,
            'bandwidth_downstream': self.bandwidth_downstream,
            'description': self.description,
            'updated_at': self.updated_at.isoformat()
        }


class PONPort(db.Model):
    """PON Port Model"""
    __tablename__ = 'pon_ports'
    
    id = db.Column(db.String(100), primary_key=True)
    device_id = db.Column(db.String(36), db.ForeignKey('olt_devices.id'), nullable=False)
    port_number = db.Column(db.Integer, nullable=False)
    port_name = db.Column(db.String(100))
    status = db.Column(db.String(20), default='DOWN')
    optical_power_downstream = db.Column(db.Float)
    optical_power_upstream = db.Column(db.Float)
    wavelength = db.Column(db.String(50))
    onu_count = db.Column(db.Integer, default=0)
    enabled = db.Column(db.Boolean, default=True)
    admin_status = db.Column(db.String(20), default='UP')
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'port_number': self.port_number,
            'port_name': self.port_name,
            'status': self.status,
            'optical_power_downstream': self.optical_power_downstream,
            'optical_power_upstream': self.optical_power_upstream,
            'wavelength': self.wavelength,
            'onu_count': self.onu_count,
            'enabled': self.enabled,
            'admin_status': self.admin_status,
            'description': self.description,
            'updated_at': self.updated_at.isoformat()
        }


class EthernetPort(db.Model):
    """Ethernet Port Model"""
    __tablename__ = 'ethernet_ports'
    
    id = db.Column(db.String(100), primary_key=True)
    device_id = db.Column(db.String(36), db.ForeignKey('olt_devices.id'), nullable=False)
    port_number = db.Column(db.Integer, nullable=False)
    port_name = db.Column(db.String(100))
    status = db.Column(db.String(20), default='DOWN')
    speed = db.Column(db.String(20))
    duplex = db.Column(db.String(20), default='FULL')
    mtu = db.Column(db.Integer, default=1500)
    vlan_id = db.Column(db.Integer)
    enabled = db.Column(db.Boolean, default=True)
    admin_status = db.Column(db.String(20), default='UP')
    rx_packets = db.Column(db.BigInteger, default=0)
    tx_packets = db.Column(db.BigInteger, default=0)
    rx_bytes = db.Column(db.BigInteger, default=0)
    tx_bytes = db.Column(db.BigInteger, default=0)
    rx_errors = db.Column(db.BigInteger, default=0)
    tx_errors = db.Column(db.BigInteger, default=0)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'port_number': self.port_number,
            'port_name': self.port_name,
            'status': self.status,
            'speed': self.speed,
            'duplex': self.duplex,
            'mtu': self.mtu,
            'vlan_id': self.vlan_id,
            'enabled': self.enabled,
            'admin_status': self.admin_status,
            'rx_packets': self.rx_packets,
            'tx_packets': self.tx_packets,
            'rx_bytes': self.rx_bytes,
            'tx_bytes': self.tx_bytes,
            'rx_errors': self.rx_errors,
            'tx_errors': self.tx_errors,
            'description': self.description,
            'updated_at': self.updated_at.isoformat()
        }


class DeviceMetric(db.Model):
    """Device Performance Metrics"""
    __tablename__ = 'device_metrics'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    device_id = db.Column(db.String(36), db.ForeignKey('olt_devices.id'), nullable=False)
    cpu_usage = db.Column(db.Float)
    memory_usage = db.Column(db.Float)
    temperature = db.Column(db.Float)
    online_onu_count = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'device_id': self.device_id,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'temperature': self.temperature,
            'online_onu_count': self.online_onu_count,
            'timestamp': self.timestamp.isoformat()
        }


class DeviceLog(db.Model):
    """Device Operation Logs"""
    __tablename__ = 'device_logs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    device_id = db.Column(db.String(36), db.ForeignKey('olt_devices.id'), nullable=False)
    log_type = db.Column(db.String(20), default='INFO')
    message = db.Column(db.Text)
    operation = db.Column(db.String(100))
    status = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'log_type': self.log_type,
            'message': self.message,
            'operation': self.operation,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
