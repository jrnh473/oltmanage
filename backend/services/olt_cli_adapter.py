import asyncio
import logging
from typing import Dict, List, Optional, Any
from .olt_adapter_base import BaseOLTAdapter, ONUInfo, PortInfo, DeviceInfo, OperationResult

logger = logging.getLogger(__name__)

# Vendor-specific CLI commands mapping
VENDOR_COMMANDS = {
    'C-DATA': {
        'info': 'show version',
        'pon_status': 'show interface pon',
        'onu_list': 'show onu list-all',
        'onu_info': 'show onu detail {port} {onu}',
        'enable_pon': 'interface pon {port}\nno shutdown',
        'disable_pon': 'interface pon {port}\nshutdown',
    },
    'ECOM': {
        'info': 'show system',
        'pon_status': 'show interface pon brief',
        'onu_list': 'show onu',
        'onu_info': 'show onu {port} {onu}',
        'enable_pon': 'config terminal\ninterface pon {port}\nno shutdown',
        'disable_pon': 'config terminal\ninterface pon {port}\nshutdown',
    },
    'VSOL': {
        'info': 'display version',
        'pon_status': 'display pon interface',
        'onu_list': 'display onu all',
        'onu_info': 'display onu {port} {onu}',
        'enable_pon': 'config\ninterface pon {port}\nno shutdown',
        'disable_pon': 'config\ninterface pon {port}\nshutdown',
    },
    'BDCOM': {
        'info': 'show device-info',
        'pon_status': 'show interface pon',
        'onu_list': 'show onu list all',
        'onu_info': 'show onu detail {port} {onu}',
        'enable_pon': 'configure\ninterface pon {port}\nno shutdown',
        'disable_pon': 'configure\ninterface pon {port}\nshutdown',
    }
}


class CLIOLTAdapter(BaseOLTAdapter):
    """CLI-based OLT Adapter (SSH/Telnet) for multi-vendor support"""
    
    def __init__(self, device_config: Dict[str, Any]):
        super().__init__(device_config)
        self.connection = None
        self.vendor = device_config.get('vendor', 'UNKNOWN')
        self.port = device_config.get('ssh_port', 22)
        self.telnet_port = device_config.get('telnet_port', 23)
        self.commands = VENDOR_COMMANDS.get(self.vendor, {})
    
    def _get_command(self, cmd_key: str, **kwargs) -> Optional[str]:
        """Get vendor-specific command"""
        cmd = self.commands.get(cmd_key)
        if cmd:
            return cmd.format(**kwargs)
        return None
    
    async def connect(self) -> OperationResult:
        """Establish SSH or Telnet connection"""
        try:
            # Mock SSH/Telnet connection - replace with actual paramiko/telnetlib
            await asyncio.sleep(0.5)
            self.is_connected = True
            return OperationResult(
                success=True,
                message=f"CLI connection established to {self.ip_address}"
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"CLI connection failed: {str(e)}",
                error_code="CLI_CONNECT_ERROR"
            )
    
    async def disconnect(self) -> OperationResult:
        """Close connection"""
        try:
            self.is_connected = False
            return OperationResult(
                success=True,
                message="CLI connection closed"
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"Disconnect failed: {str(e)}",
                error_code="CLI_DISCONNECT_ERROR"
            )
    
    async def _send_command(self, cmd: str) -> str:
        """Send command to device (mock implementation)"""
        # Mock command execution
        await asyncio.sleep(0.2)
        return f"Output of: {cmd}"
    
    async def get_device_info(self) -> OperationResult:
        """Get device information via CLI"""
        try:
            if not self.is_connected:
                await self.connect()
            
            cmd = self._get_command('info')
            if not cmd:
                # Fallback to mock data
                pass
            
            info = DeviceInfo(
                model=self.device_config.get('model', 'Unknown'),
                vendor=self.vendor,
                status='ONLINE',
                cpu_usage=32.1,
                memory_usage=52.3,
                temperature=45.2,
                uptime_seconds=720000,
                firmware_version='V3.2.1',
                serial_number='SN98765432',
                total_onu_count=16,
                online_onu_count=14
            )
            
            return OperationResult(
                success=True,
                message="Device info retrieved",
                data=info
            )
        except Exception as e:
            logger.error(f"Failed to get device info: {str(e)}")
            return OperationResult(
                success=False,
                message=f"Failed to get device info: {str(e)}",
                error_code="GET_DEVICE_INFO_ERROR"
            )
    
    async def get_pon_ports(self) -> OperationResult:
        """Get PON ports information"""
        try:
            cmd = self._get_command('pon_status')
            ports = []
            
            for i in range(1, 5):
                port = PortInfo(
                    id=f"PON{i}",
                    port_number=i,
                    port_name=f"pon {i}",
                    status="UP" if i <= 3 else "DOWN",
                    port_type="PON",
                    optical_power=-4.8,
                    wavelength="1310nm",
                    onu_count=3 if i <= 3 else 0
                )
                ports.append(port)
            
            return OperationResult(
                success=True,
                message="PON ports retrieved",
                data=ports
            )
        except Exception as e:
            logger.error(f"Failed to get PON ports: {str(e)}")
            return OperationResult(
                success=False,
                message=f"Failed to get PON ports: {str(e)}",
                error_code="GET_PON_PORTS_ERROR"
            )
    
    async def get_ethernet_ports(self) -> OperationResult:
        """Get Ethernet ports information"""
        try:
            ports = []
            
            for i in range(1, 5):
                port = PortInfo(
                    id=f"ETH{i}",
                    port_number=i,
                    port_name=f"eth{i}",
                    status="UP" if i <= 2 else "DOWN",
                    port_type="ETH",
                    speed="1000Mbps",
                    duplex="FULL"
                )
                ports.append(port)
            
            return OperationResult(
                success=True,
                message="Ethernet ports retrieved",
                data=ports
            )
        except Exception as e:
            logger.error(f"Failed to get Ethernet ports: {str(e)}")
            return OperationResult(
                success=False,
                message=f"Failed to get Ethernet ports: {str(e)}",
                error_code="GET_ETH_PORTS_ERROR"
            )
    
    async def discover_onus(self, port_id: Optional[int] = None) -> OperationResult:
        """Discover ONUs on PON port(s)"""
        try:
            cmd = self._get_command('onu_list')
            onus = []
            ports = [port_id] if port_id else range(1, 5)
            
            for port in ports:
                for onu_idx in range(1, 4):
                    onu = ONUInfo(
                        id=f"PON{port}_ONU{onu_idx}",
                        port_id=port,
                        onu_index=onu_idx,
                        serial_number=f"GPHF{12345000+onu_idx:08d}",
                        mac_address=f"00:00:5e:00:53:{onu_idx:02x}",
                        status="ONLINE",
                        vendor_name="GPON",
                        optical_power_downstream=-27.2,
                        optical_power_upstream=-2.8,
                        distance_km=16.2
                    )
                    onus.append(onu)
            
            return OperationResult(
                success=True,
                message=f"Discovered {len(onus)} ONUs",
                data=onus
            )
        except Exception as e:
            logger.error(f"ONU discovery failed: {str(e)}")
            return OperationResult(
                success=False,
                message=f"ONU discovery failed: {str(e)}",
                error_code="ONU_DISCOVERY_ERROR"
            )
    
    async def get_onu_info(self, port_id: int, onu_index: int) -> OperationResult:
        """Get specific ONU information"""
        try:
            cmd = self._get_command('onu_info', port=port_id, onu=onu_index)
            
            onu = ONUInfo(
                id=f"PON{port_id}_ONU{onu_index}",
                port_id=port_id,
                onu_index=onu_index,
                serial_number=f"GPHF{12345000+onu_index:08d}",
                mac_address=f"00:00:5e:00:53:{onu_index:02x}",
                status="ONLINE",
                vendor_name="GPON",
                hardware_version="V1.0.0",
                software_version="V2.2.0",
                optical_power_downstream=-27.2,
                optical_power_upstream=-2.8,
                distance_km=16.2,
                vlan_id=100
            )
            
            return OperationResult(
                success=True,
                message="ONU info retrieved",
                data=onu
            )
        except Exception as e:
            logger.error(f"Failed to get ONU info: {str(e)}")
            return OperationResult(
                success=False,
                message=f"Failed to get ONU info: {str(e)}",
                error_code="GET_ONU_INFO_ERROR"
            )
    
    async def configure_onu(self, port_id: int, onu_index: int, config: Dict) -> OperationResult:
        """Configure ONU"""
        try:
            await asyncio.sleep(1)
            return OperationResult(
                success=True,
                message=f"ONU PON{port_id}_ONU{onu_index} configured",
                data={"configured_params": config}
            )
        except Exception as e:
            logger.error(f"ONU configuration failed: {str(e)}")
            return OperationResult(
                success=False,
                message=f"ONU configuration failed: {str(e)}",
                error_code="ONU_CONFIG_ERROR"
            )
    
    async def reset_onu(self, port_id: int, onu_index: int) -> OperationResult:
        """Reset ONU"""
        try:
            await asyncio.sleep(2)
            return OperationResult(
                success=True,
                message=f"ONU PON{port_id}_ONU{onu_index} reset"
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"ONU reset failed: {str(e)}",
                error_code="ONU_RESET_ERROR"
            )
    
    async def reboot_onu(self, port_id: int, onu_index: int) -> OperationResult:
        """Reboot ONU"""
        try:
            await asyncio.sleep(3)
            return OperationResult(
                success=True,
                message=f"ONU PON{port_id}_ONU{onu_index} rebooting"
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"ONU reboot failed: {str(e)}",
                error_code="ONU_REBOOT_ERROR"
            )
    
    async def enable_port(self, port_id: int, port_type: str = 'PON') -> OperationResult:
        """Enable port"""
        try:
            if port_type == 'PON':
                cmd = self._get_command('enable_pon', port=port_id)
            await asyncio.sleep(1)
            return OperationResult(
                success=True,
                message=f"{port_type} port {port_id} enabled"
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"Enable port failed: {str(e)}",
                error_code="ENABLE_PORT_ERROR"
            )
    
    async def disable_port(self, port_id: int, port_type: str = 'PON') -> OperationResult:
        """Disable port"""
        try:
            if port_type == 'PON':
                cmd = self._get_command('disable_pon', port=port_id)
            await asyncio.sleep(1)
            return OperationResult(
                success=True,
                message=f"{port_type} port {port_id} disabled"
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"Disable port failed: {str(e)}",
                error_code="DISABLE_PORT_ERROR"
            )
    
    async def clear_port(self, port_id: int) -> OperationResult:
        """Clear all ONUs from port"""
        try:
            await asyncio.sleep(2)
            return OperationResult(
                success=True,
                message=f"PON port {port_id} cleared"
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"Clear port failed: {str(e)}",
                error_code="CLEAR_PORT_ERROR"
            )
    
    async def get_port_statistics(self, port_id: int, port_type: str = 'PON') -> OperationResult:
        """Get port statistics"""
        try:
            stats = {
                'rx_packets': 2048000,
                'tx_packets': 1024000,
                'rx_bytes': 2048000000,
                'tx_bytes': 1024000000,
                'rx_errors': 0,
                'tx_errors': 0
            }
            return OperationResult(
                success=True,
                message="Port statistics retrieved",
                data=stats
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"Failed to get port statistics: {str(e)}",
                error_code="GET_STATS_ERROR"
            )
