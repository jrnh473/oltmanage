"""
Database Service Abstraction Layer
This service is database-agnostic and can be easily replaced with any database implementation.
To use a different database (PostgreSQL, MongoDB, etc.), simply replace the implementation 
while keeping the same interface.
"""

import logging
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class DatabaseService(ABC):
    """Abstract base class for database operations"""
    
    # ==================== Device Operations ====================
    
    @abstractmethod
    def create_device(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new OLT device"""
        pass
    
    @abstractmethod
    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get device by ID"""
        pass
    
    @abstractmethod
    def get_all_devices(self) -> List[Dict[str, Any]]:
        """Get all devices"""
        pass
    
    @abstractmethod
    def get_device_by_ip(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """Get device by IP address"""
        pass
    
    @abstractmethod
    def update_device(self, device_id: str, updates: Dict[str, Any]) -> bool:
        """Update device"""
        pass
    
    @abstractmethod
    def delete_device(self, device_id: str) -> bool:
        """Delete device"""
        pass
    
    # ==================== PON Port Operations ====================
    
    @abstractmethod
    def create_pon_port(self, port_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create PON port"""
        pass
    
    @abstractmethod
    def get_pon_port(self, port_id: str) -> Optional[Dict[str, Any]]:
        """Get PON port by ID"""
        pass
    
    @abstractmethod
    def get_pon_ports_by_device(self, device_id: str) -> List[Dict[str, Any]]:
        """Get all PON ports for device"""
        pass
    
    @abstractmethod
    def update_pon_port(self, port_id: str, updates: Dict[str, Any]) -> bool:
        """Update PON port"""
        pass
    
    @abstractmethod
    def delete_pon_port(self, port_id: str) -> bool:
        """Delete PON port"""
        pass
    
    # ==================== ONU Operations ====================
    
    @abstractmethod
    def create_onu(self, onu_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create ONU"""
        pass
    
    @abstractmethod
    def get_onu(self, onu_id: str) -> Optional[Dict[str, Any]]:
        """Get ONU by ID"""
        pass
    
    @abstractmethod
    def get_onus_by_device(self, device_id: str) -> List[Dict[str, Any]]:
        """Get all ONUs for device"""
        pass
    
    @abstractmethod
    def get_onus_by_port(self, device_id: str, port_id: int) -> List[Dict[str, Any]]:
        """Get ONUs for specific port"""
        pass
    
    @abstractmethod
    def update_onu(self, onu_id: str, updates: Dict[str, Any]) -> bool:
        """Update ONU"""
        pass
    
    @abstractmethod
    def delete_onu(self, onu_id: str) -> bool:
        """Delete ONU"""
        pass
    
    @abstractmethod
    def delete_onus_by_device(self, device_id: str) -> bool:
        """Delete all ONUs for device"""
        pass
    
    # ==================== Ethernet Port Operations ====================
    
    @abstractmethod
    def create_ethernet_port(self, port_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Ethernet port"""
        pass
    
    @abstractmethod
    def get_ethernet_port(self, port_id: str) -> Optional[Dict[str, Any]]:
        """Get Ethernet port by ID"""
        pass
    
    @abstractmethod
    def get_ethernet_ports_by_device(self, device_id: str) -> List[Dict[str, Any]]:
        """Get all Ethernet ports for device"""
        pass
    
    @abstractmethod
    def update_ethernet_port(self, port_id: str, updates: Dict[str, Any]) -> bool:
        """Update Ethernet port"""
        pass
    
    @abstractmethod
    def delete_ethernet_port(self, port_id: str) -> bool:
        """Delete Ethernet port"""
        pass
    
    # ==================== Metric Operations ====================
    
    @abstractmethod
    def create_metric(self, metric_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create device metric"""
        pass
    
    @abstractmethod
    def get_metrics_by_device(self, device_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get metrics for device"""
        pass
    
    # ==================== Log Operations ====================
    
    @abstractmethod
    def create_log(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create device log"""
        pass
    
    @abstractmethod
    def get_logs_by_device(self, device_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get logs for device"""
        pass
    
    # ==================== Batch Operations ====================
    
    @abstractmethod
    def batch_create_onus(self, device_id: str, onus_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create multiple ONUs at once"""
        pass
    
    @abstractmethod
    def batch_update_onus(self, updates_list: List[tuple]) -> bool:
        """Update multiple ONUs at once (list of (onu_id, updates) tuples)"""
        pass


class SQLAlchemyDatabaseService(DatabaseService):
    """SQLAlchemy implementation of DatabaseService (Flask-SQLAlchemy)"""
    
    def __init__(self, db):
        """Initialize with SQLAlchemy instance"""
        self.db = db
        # Import models here to avoid circular imports
        from models.olt_models import OLTDevice, PONPort, ONU, EthernetPort, DeviceMetric, DeviceLog
        self.OLTDevice = OLTDevice
        self.PONPort = PONPort
        self.ONU = ONU
        self.EthernetPort = EthernetPort
        self.DeviceMetric = DeviceMetric
        self.DeviceLog = DeviceLog
    
    # ==================== Device Operations ====================
    
    def create_device(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            device = self.OLTDevice(
                id=device_data.get('id', str(uuid.uuid4())),
                model=device_data['model'],
                vendor=device_data['vendor'],
                ip_address=device_data['ip_address'],
                snmp_port=device_data.get('snmp_port', 161),
                ssh_port=device_data.get('ssh_port', 22),
                snmp_community=device_data.get('snmp_community', 'public'),
                username=device_data.get('username'),
                password=device_data.get('password'),
                connection_method=device_data.get('connection_method', 'SNMP'),
                status=device_data.get('status', 'UNKNOWN')
            )
            self.db.session.add(device)
            self.db.session.commit()
            return device.to_dict()
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error creating device: {str(e)}")
            raise
    
    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        try:
            device = self.OLTDevice.query.get(device_id)
            return device.to_dict() if device else None
        except Exception as e:
            logger.error(f"Error getting device: {str(e)}")
            return None
    
    def get_all_devices(self) -> List[Dict[str, Any]]:
        try:
            devices = self.OLTDevice.query.all()
            return [device.to_dict() for device in devices]
        except Exception as e:
            logger.error(f"Error getting all devices: {str(e)}")
            return []
    
    def get_device_by_ip(self, ip_address: str) -> Optional[Dict[str, Any]]:
        try:
            device = self.OLTDevice.query.filter_by(ip_address=ip_address).first()
            return device.to_dict() if device else None
        except Exception as e:
            logger.error(f"Error getting device by IP: {str(e)}")
            return None
    
    def update_device(self, device_id: str, updates: Dict[str, Any]) -> bool:
        try:
            device = self.OLTDevice.query.get(device_id)
            if not device:
                return False
            
            for key, value in updates.items():
                if hasattr(device, key) and key != 'id':
                    setattr(device, key, value)
            
            device.updated_at = datetime.utcnow()
            self.db.session.commit()
            return True
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error updating device: {str(e)}")
            return False
    
    def delete_device(self, device_id: str) -> bool:
        try:
            device = self.OLTDevice.query.get(device_id)
            if not device:
                return False
            
            self.db.session.delete(device)
            self.db.session.commit()
            return True
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error deleting device: {str(e)}")
            return False
    
    # ==================== PON Port Operations ====================
    
    def create_pon_port(self, port_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            port = self.PONPort(
                id=port_data.get('id', str(uuid.uuid4())),
                device_id=port_data['device_id'],
                port_number=port_data['port_number'],
                port_name=port_data.get('port_name'),
                status=port_data.get('status', 'DOWN'),
                optical_power_downstream=port_data.get('optical_power_downstream'),
                optical_power_upstream=port_data.get('optical_power_upstream'),
                wavelength=port_data.get('wavelength'),
                onu_count=port_data.get('onu_count', 0),
                enabled=port_data.get('enabled', True),
                admin_status=port_data.get('admin_status', 'UP'),
                description=port_data.get('description')
            )
            self.db.session.add(port)
            self.db.session.commit()
            return port.to_dict()
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error creating PON port: {str(e)}")
            raise
    
    def get_pon_port(self, port_id: str) -> Optional[Dict[str, Any]]:
        try:
            port = self.PONPort.query.get(port_id)
            return port.to_dict() if port else None
        except Exception as e:
            logger.error(f"Error getting PON port: {str(e)}")
            return None
    
    def get_pon_ports_by_device(self, device_id: str) -> List[Dict[str, Any]]:
        try:
            ports = self.PONPort.query.filter_by(device_id=device_id).all()
            return [port.to_dict() for port in ports]
        except Exception as e:
            logger.error(f"Error getting PON ports: {str(e)}")
            return []
    
    def update_pon_port(self, port_id: str, updates: Dict[str, Any]) -> bool:
        try:
            port = self.PONPort.query.get(port_id)
            if not port:
                return False
            
            for key, value in updates.items():
                if hasattr(port, key) and key != 'id':
                    setattr(port, key, value)
            
            port.updated_at = datetime.utcnow()
            self.db.session.commit()
            return True
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error updating PON port: {str(e)}")
            return False
    
    def delete_pon_port(self, port_id: str) -> bool:
        try:
            port = self.PONPort.query.get(port_id)
            if not port:
                return False
            
            self.db.session.delete(port)
            self.db.session.commit()
            return True
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error deleting PON port: {str(e)}")
            return False
    
    # ==================== ONU Operations ====================
    
    def create_onu(self, onu_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            onu = self.ONU(
                id=onu_data.get('id'),
                device_id=onu_data['device_id'],
                port_id=onu_data['port_id'],
                onu_index=onu_data['onu_index'],
                serial_number=onu_data.get('serial_number'),
                mac_address=onu_data.get('mac_address'),
                ip_address=onu_data.get('ip_address'),
                status=onu_data.get('status', 'OFFLINE'),
                vendor_name=onu_data.get('vendor_name'),
                hardware_version=onu_data.get('hardware_version'),
                software_version=onu_data.get('software_version'),
                optical_power_downstream=onu_data.get('optical_power_downstream'),
                optical_power_upstream=onu_data.get('optical_power_upstream'),
                distance_km=onu_data.get('distance_km'),
                vlan_id=onu_data.get('vlan_id'),
                bandwidth_upstream=onu_data.get('bandwidth_upstream'),
                bandwidth_downstream=onu_data.get('bandwidth_downstream'),
                description=onu_data.get('description')
            )
            self.db.session.add(onu)
            self.db.session.commit()
            return onu.to_dict()
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error creating ONU: {str(e)}")
            raise
    
    def get_onu(self, onu_id: str) -> Optional[Dict[str, Any]]:
        try:
            onu = self.ONU.query.get(onu_id)
            return onu.to_dict() if onu else None
        except Exception as e:
            logger.error(f"Error getting ONU: {str(e)}")
            return None
    
    def get_onus_by_device(self, device_id: str) -> List[Dict[str, Any]]:
        try:
            onus = self.ONU.query.filter_by(device_id=device_id).all()
            return [onu.to_dict() for onu in onus]
        except Exception as e:
            logger.error(f"Error getting ONUs: {str(e)}")
            return []
    
    def get_onus_by_port(self, device_id: str, port_id: int) -> List[Dict[str, Any]]:
        try:
            onus = self.ONU.query.filter_by(device_id=device_id, port_id=port_id).all()
            return [onu.to_dict() for onu in onus]
        except Exception as e:
            logger.error(f"Error getting ONUs by port: {str(e)}")
            return []
    
    def update_onu(self, onu_id: str, updates: Dict[str, Any]) -> bool:
        try:
            onu = self.ONU.query.get(onu_id)
            if not onu:
                return False
            
            for key, value in updates.items():
                if hasattr(onu, key) and key != 'id':
                    setattr(onu, key, value)
            
            onu.updated_at = datetime.utcnow()
            self.db.session.commit()
            return True
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error updating ONU: {str(e)}")
            return False
    
    def delete_onu(self, onu_id: str) -> bool:
        try:
            onu = self.ONU.query.get(onu_id)
            if not onu:
                return False
            
            self.db.session.delete(onu)
            self.db.session.commit()
            return True
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error deleting ONU: {str(e)}")
            return False
    
    def delete_onus_by_device(self, device_id: str) -> bool:
        try:
            self.ONU.query.filter_by(device_id=device_id).delete()
            self.db.session.commit()
            return True
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error deleting ONUs: {str(e)}")
            return False
    
    # ==================== Ethernet Port Operations ====================
    
    def create_ethernet_port(self, port_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            port = self.EthernetPort(
                id=port_data.get('id', str(uuid.uuid4())),
                device_id=port_data['device_id'],
                port_number=port_data['port_number'],
                port_name=port_data.get('port_name'),
                status=port_data.get('status', 'DOWN'),
                speed=port_data.get('speed'),
                duplex=port_data.get('duplex', 'FULL'),
                mtu=port_data.get('mtu', 1500),
                vlan_id=port_data.get('vlan_id'),
                enabled=port_data.get('enabled', True),
                admin_status=port_data.get('admin_status', 'UP'),
                description=port_data.get('description')
            )
            self.db.session.add(port)
            self.db.session.commit()
            return port.to_dict()
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error creating Ethernet port: {str(e)}")
            raise
    
    def get_ethernet_port(self, port_id: str) -> Optional[Dict[str, Any]]:
        try:
            port = self.EthernetPort.query.get(port_id)
            return port.to_dict() if port else None
        except Exception as e:
            logger.error(f"Error getting Ethernet port: {str(e)}")
            return None
    
    def get_ethernet_ports_by_device(self, device_id: str) -> List[Dict[str, Any]]:
        try:
            ports = self.EthernetPort.query.filter_by(device_id=device_id).all()
            return [port.to_dict() for port in ports]
        except Exception as e:
            logger.error(f"Error getting Ethernet ports: {str(e)}")
            return []
    
    def update_ethernet_port(self, port_id: str, updates: Dict[str, Any]) -> bool:
        try:
            port = self.EthernetPort.query.get(port_id)
            if not port:
                return False
            
            for key, value in updates.items():
                if hasattr(port, key) and key != 'id':
                    setattr(port, key, value)
            
            port.updated_at = datetime.utcnow()
            self.db.session.commit()
            return True
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error updating Ethernet port: {str(e)}")
            return False
    
    def delete_ethernet_port(self, port_id: str) -> bool:
        try:
            port = self.EthernetPort.query.get(port_id)
            if not port:
                return False
            
            self.db.session.delete(port)
            self.db.session.commit()
            return True
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error deleting Ethernet port: {str(e)}")
            return False
    
    # ==================== Metric Operations ====================
    
    def create_metric(self, metric_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            metric = self.DeviceMetric(
                device_id=metric_data['device_id'],
                cpu_usage=metric_data.get('cpu_usage'),
                memory_usage=metric_data.get('memory_usage'),
                temperature=metric_data.get('temperature'),
                online_onu_count=metric_data.get('online_onu_count'),
                timestamp=metric_data.get('timestamp', datetime.utcnow())
            )
            self.db.session.add(metric)
            self.db.session.commit()
            return metric.to_dict()
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error creating metric: {str(e)}")
            raise
    
    def get_metrics_by_device(self, device_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        try:
            metrics = self.DeviceMetric.query.filter_by(device_id=device_id)\
                .order_by(self.DeviceMetric.timestamp.desc())\
                .limit(limit).all()
            return [metric.to_dict() for metric in metrics]
        except Exception as e:
            logger.error(f"Error getting metrics: {str(e)}")
            return []
    
    # ==================== Log Operations ====================
    
    def create_log(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            log = self.DeviceLog(
                device_id=log_data['device_id'],
                log_type=log_data.get('log_type', 'INFO'),
                message=log_data.get('message'),
                operation=log_data.get('operation'),
                status=log_data.get('status'),
                created_at=log_data.get('created_at', datetime.utcnow())
            )
            self.db.session.add(log)
            self.db.session.commit()
            return log.to_dict()
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error creating log: {str(e)}")
            raise
    
    def get_logs_by_device(self, device_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        try:
            logs = self.DeviceLog.query.filter_by(device_id=device_id)\
                .order_by(self.DeviceLog.created_at.desc())\
                .limit(limit).all()
            return [log.to_dict() for log in logs]
        except Exception as e:
            logger.error(f"Error getting logs: {str(e)}")
            return []
    
    # ==================== Batch Operations ====================
    
    def batch_create_onus(self, device_id: str, onus_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        try:
            created_onus = []
            for onu_data in onus_data:
                onu_data['device_id'] = device_id
                onu = self.create_onu(onu_data)
                created_onus.append(onu)
            return created_onus
        except Exception as e:
            logger.error(f"Error batch creating ONUs: {str(e)}")
            raise
    
    def batch_update_onus(self, updates_list: List[tuple]) -> bool:
        try:
            for onu_id, updates in updates_list:
                self.update_onu(onu_id, updates)
            return True
        except Exception as e:
            logger.error(f"Error batch updating ONUs: {str(e)}")
            return False
