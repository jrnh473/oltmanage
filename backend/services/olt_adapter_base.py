from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)

@dataclass
class ONUInfo:
    """ONU Information"""
    id: str
    port_id: int
    onu_index: int
    serial_number: Optional[str] = None
    mac_address: Optional[str] = None
    ip_address: Optional[str] = None
    status: str = 'OFFLINE'
    vendor_name: Optional[str] = None
    hardware_version: Optional[str] = None
    software_version: Optional[str] = None
    optical_power_downstream: Optional[float] = None
    optical_power_upstream: Optional[float] = None
    distance_km: Optional[float] = None
    vlan_id: Optional[int] = None

@dataclass
class PortInfo:
    """Port Information"""
    id: str
    port_number: int
    port_name: str
    status: str
    port_type: str  # 'PON' or 'ETH'
    optical_power: Optional[float] = None
    wavelength: Optional[str] = None
    speed: Optional[str] = None
    duplex: Optional[str] = None
    mtu: Optional[int] = None
    onu_count: Optional[int] = None

@dataclass
class DeviceInfo:
    """Device Information"""
    model: str
    vendor: str
    status: str
    cpu_usage: float
    memory_usage: float
    temperature: float
    uptime_seconds: int
    firmware_version: Optional[str] = None
    serial_number: Optional[str] = None
    total_onu_count: int = 0
    online_onu_count: int = 0

@dataclass
class OperationResult:
    """Operation Result"""
    success: bool
    message: str
    data: Optional[Any] = None
    error_code: Optional[str] = None


class BaseOLTAdapter(ABC):
    """Base OLT Adapter - All adapters must inherit from this"""
    
    SUPPORTED_MODELS = []
    VENDOR = None
    
    def __init__(self, device_config: Dict[str, Any]):
        """
        Initialize adapter with device configuration
        
        Args:
            device_config: Device configuration dict with ip_address, username, password, etc.
        """
        self.device_config = device_config
        self.ip_address = device_config.get('ip_address')
        self.port = device_config.get('snmp_port', 161)
        self.username = device_config.get('username')
        self.password = device_config.get('password')
        self.snmp_community = device_config.get('snmp_community')
        self.connection_timeout = 10
        self.is_connected = False
        
    @abstractmethod
    async def connect(self) -> OperationResult:
        """Establish connection to device"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> OperationResult:
        """Close connection to device"""
        pass
    
    @abstractmethod
    async def get_device_info(self) -> OperationResult:
        """Get device basic information"""
        pass
    
    @abstractmethod
    async def get_pon_ports(self) -> OperationResult:
        """Get PON ports information"""
        pass
    
    @abstractmethod
    async def get_ethernet_ports(self) -> OperationResult:
        """Get Ethernet ports information"""
        pass
    
    @abstractmethod
    async def discover_onus(self, port_id: Optional[int] = None) -> OperationResult:
        """
        Discover ONUs on specific port or all PON ports
        
        Args:
            port_id: Specific PON port ID (None = all ports)
        """
        pass
    
    @abstractmethod
    async def get_onu_info(self, port_id: int, onu_index: int) -> OperationResult:
        """Get specific ONU information"""
        pass
    
    @abstractmethod
    async def configure_onu(self, port_id: int, onu_index: int, config: Dict) -> OperationResult:
        """
        Configure ONU with provided settings
        
        Args:
            port_id: PON port ID
            onu_index: ONU index on port
            config: Configuration dict (vlan_id, bandwidth, etc.)
        """
        pass
    
    @abstractmethod
    async def reset_onu(self, port_id: int, onu_index: int) -> OperationResult:
        """Reset specific ONU"""
        pass
    
    @abstractmethod
    async def reboot_onu(self, port_id: int, onu_index: int) -> OperationResult:
        """Reboot specific ONU"""
        pass
    
    @abstractmethod
    async def enable_port(self, port_id: int, port_type: str = 'PON') -> OperationResult:
        """Enable port (PON or ETH)"""
        pass
    
    @abstractmethod
    async def disable_port(self, port_id: int, port_type: str = 'PON') -> OperationResult:
        """Disable port (PON or ETH)"""
        pass
    
    @abstractmethod
    async def clear_port(self, port_id: int) -> OperationResult:
        """Clear all ONUs from PON port"""
        pass
    
    @abstractmethod
    async def get_port_statistics(self, port_id: int, port_type: str = 'PON') -> OperationResult:
        """Get port statistics"""
        pass
    
    async def health_check(self) -> bool:
        """Check if device is responsive"""
        try:
            result = await self.get_device_info()
            return result.success
        except Exception as e:
            logger.error(f"Health check failed for {self.ip_address}: {str(e)}")
            return False
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.ip_address})"
