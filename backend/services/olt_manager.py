import logging
from typing import Dict, Optional, Any
from .olt_adapter_base import BaseOLTAdapter, OperationResult
from .olt_snmp_adapter import SNMPOLTAdapter
from .olt_cli_adapter import CLIOLTAdapter

logger = logging.getLogger(__name__)

# Supported OLT models with their properties
SUPPORTED_OLT_MODELS = {
    # C-DATA
    'FD1104SN': {'vendor': 'C-DATA', 'pon_ports': 4, 'eth_ports': 4},
    'FD1204S': {'vendor': 'C-DATA', 'pon_ports': 4, 'eth_ports': 4},
    'FD1208S': {'vendor': 'C-DATA', 'pon_ports': 8, 'eth_ports': 8},
    'FD1304E': {'vendor': 'C-DATA', 'pon_ports': 4, 'eth_ports': 4},
    # ECOM
    'E08GP': {'vendor': 'ECOM', 'pon_ports': 8, 'eth_ports': 8},
    'E1204ES': {'vendor': 'ECOM', 'pon_ports': 4, 'eth_ports': 4},
    'E1208ES': {'vendor': 'ECOM', 'pon_ports': 8, 'eth_ports': 8},
    # Connect+
    'CPE-804-2S+': {'vendor': 'Connect+', 'pon_ports': 4, 'eth_ports': 4},
    # VSOL
    '1600-G1': {'vendor': 'VSOL', 'pon_ports': 8, 'eth_ports': 8},
    'V1601E04': {'vendor': 'VSOL', 'pon_ports': 4, 'eth_ports': 4},
    'V1600D8': {'vendor': 'VSOL', 'pon_ports': 8, 'eth_ports': 8},
    # BDCOM
    '1608V': {'vendor': 'BDCOM', 'pon_ports': 8, 'eth_ports': 4},
    'P3608B': {'vendor': 'BDCOM', 'pon_ports': 8, 'eth_ports': 4},
    'P3310D': {'vendor': 'BDCOM', 'pon_ports': 4, 'eth_ports': 4},
    # DBC
    '3310-2AC': {'vendor': 'DBC', 'pon_ports': 4, 'eth_ports': 4},
    # AVEIS
    'AV-OLT-E04': {'vendor': 'AVEIS', 'pon_ports': 4, 'eth_ports': 4},
    # HSGQ
    'HSGQ-OLT-E04': {'vendor': 'HSGQ', 'pon_ports': 4, 'eth_ports': 4},
    # PHYHOME
    'FHL-104C': {'vendor': 'PHYHOME', 'pon_ports': 4, 'eth_ports': 4},
}


class OLTManager:
    """Manages OLT device adapters with fallback strategy"""
    
    def __init__(self):
        self.adapters: Dict[str, BaseOLTAdapter] = {}
        self._adapter_instances = {}
    
    @staticmethod
    def is_supported_model(model: str) -> bool:
        """Check if model is supported"""
        return model in SUPPORTED_OLT_MODELS
    
    @staticmethod
    def get_model_info(model: str) -> Optional[Dict]:
        """Get model information"""
        return SUPPORTED_OLT_MODELS.get(model)
    
    def create_adapter(self, device_config: Dict[str, Any]) -> Optional[BaseOLTAdapter]:
        """
        Create appropriate adapter based on device configuration
        
        Primary: SNMP
        Fallback: SSH/Telnet (CLI)
        
        Args:
            device_config: Device configuration dictionary
            
        Returns:
            BaseOLTAdapter instance or None if device is not supported
        """
        model = device_config.get('model')
        
        # Check if model is supported
        if not self.is_supported_model(model):
            logger.warning(f"Unsupported OLT model: {model}")
            return None
        
        device_id = device_config.get('id')
        connection_method = device_config.get('connection_method', 'SNMP')
        
        # Try SNMP first (primary)
        try:
            logger.info(f"Creating SNMP adapter for {model} ({device_id})")
            adapter = SNMPOLTAdapter(device_config)
            self._adapter_instances[device_id] = adapter
            return adapter
        except Exception as e:
            logger.warning(f"Failed to create SNMP adapter: {str(e)}")
        
        # Fallback to CLI (SSH/Telnet)
        try:
            logger.info(f"Creating CLI adapter for {model} ({device_id})")
            adapter = CLIOLTAdapter(device_config)
            self._adapter_instances[device_id] = adapter
            return adapter
        except Exception as e:
            logger.error(f"Failed to create CLI adapter: {str(e)}")
            return None
    
    def get_adapter(self, device_id: str) -> Optional[BaseOLTAdapter]:
        """Get existing adapter instance"""
        return self._adapter_instances.get(device_id)
    
    def remove_adapter(self, device_id: str) -> bool:
        """Remove adapter instance"""
        if device_id in self._adapter_instances:
            del self._adapter_instances[device_id]
            return True
        return False
    
    async def connect_device(self, device_config: Dict[str, Any]) -> OperationResult:
        """
        Connect to device
        
        Args:
            device_config: Device configuration
            
        Returns:
            OperationResult
        """
        adapter = self.create_adapter(device_config)
        
        if not adapter:
            return OperationResult(
                success=False,
                message=f"Failed to create adapter for {device_config.get('model')}",
                error_code="ADAPTER_CREATE_ERROR"
            )
        
        return await adapter.connect()
    
    async def disconnect_device(self, device_id: str) -> OperationResult:
        """Disconnect from device"""
        adapter = self.get_adapter(device_id)
        
        if not adapter:
            return OperationResult(
                success=False,
                message=f"Adapter not found for device {device_id}",
                error_code="ADAPTER_NOT_FOUND"
            )
        
        result = await adapter.disconnect()
        self.remove_adapter(device_id)
        return result
    
    async def health_check(self, device_id: str) -> bool:
        """Check device health"""
        adapter = self.get_adapter(device_id)
        
        if not adapter:
            return False
        
        return await adapter.health_check()
    
    async def execute_operation(
        self,
        device_id: str,
        operation: str,
        **kwargs
    ) -> OperationResult:
        """
        Execute operation on device
        
        Args:
            device_id: Device ID
            operation: Operation name (e.g., 'discover_onus', 'configure_onu')
            **kwargs: Operation parameters
            
        Returns:
            OperationResult
        """
        adapter = self.get_adapter(device_id)
        
        if not adapter:
            return OperationResult(
                success=False,
                message=f"Adapter not found for device {device_id}",
                error_code="ADAPTER_NOT_FOUND"
            )
        
        # Get operation method from adapter
        method = getattr(adapter, operation, None)
        
        if not method or not callable(method):
            return OperationResult(
                success=False,
                message=f"Operation '{operation}' not supported",
                error_code="OPERATION_NOT_SUPPORTED"
            )
        
        try:
            return await method(**kwargs)
        except Exception as e:
            logger.error(f"Operation '{operation}' failed: {str(e)}")
            return OperationResult(
                success=False,
                message=f"Operation failed: {str(e)}",
                error_code="OPERATION_FAILED"
            )


# Global OLT Manager instance
olt_manager = OLTManager()
