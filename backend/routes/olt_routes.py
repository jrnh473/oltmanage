from flask import Blueprint, request, jsonify
from flask_socketio import emit
import logging
import uuid
from datetime import datetime
from functools import wraps

from models.olt_models import db, OLTDevice, ONU, PONPort, EthernetPort, DeviceLog
from services.olt_manager import olt_manager, SUPPORTED_OLT_MODELS
from services.database_service import SQLAlchemyDatabaseService

logger = logging.getLogger(__name__)

# Create Blueprint
olt_bp = Blueprint('olt', __name__, url_prefix='/api/olt')

# Initialize database service (will be set when app initializes)
db_service: SQLAlchemyDatabaseService = None

def init_db_service(database):
    """Initialize database service with Flask-SQLAlchemy instance"""
    global db_service
    db_service = SQLAlchemyDatabaseService(database)


def async_handler(f):
    """Decorator to handle async operations"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(f(*args, **kwargs))
        finally:
            loop.close()
    return decorated_function


def log_operation(device_id: str, operation: str, status: str, message: str = ''):
    """Log device operation"""
    log = DeviceLog(
        device_id=device_id,
        operation=operation,
        status=status,
        log_type='INFO' if status == 'SUCCESS' else 'ERROR',
        message=message
    )
    db.session.add(log)
    db.session.commit()


# ==================== Device Management ====================

@olt_bp.route('/devices', methods=['GET'])
def get_devices():
    """Get all registered OLT devices"""
    try:
        devices = db_service.get_all_devices()
        return jsonify({
            'success': True,
            'data': devices
        })
    except Exception as e:
        logger.error(f"Error getting devices: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@olt_bp.route('/devices/<device_id>', methods=['GET'])
def get_device(device_id):
    """Get specific device details"""
    try:
        device = db_service.get_device(device_id)
        if not device:
            return jsonify({
                'success': False,
                'message': 'Device not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': device
        })
    except Exception as e:
        logger.error(f"Error getting device: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@olt_bp.route('/devices', methods=['POST'])
@async_handler
async def register_device():
    """Register new OLT device"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['model', 'vendor', 'ip_address']
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400
        
        # Check if model is supported
        if not olt_manager.is_supported_model(data['model']):
            return jsonify({
                'success': False,
                'message': f"Model {data['model']} is not supported"
            }), 400
        
        # Check if device already exists
        existing_device = db_service.get_device_by_ip(data['ip_address'])
        if existing_device:
            return jsonify({
                'success': False,
                'message': 'Device with this IP already exists'
            }), 409
        
        # Create device
        device_id = str(uuid.uuid4())
        device_data = {
            'id': device_id,
            'model': data['model'],
            'vendor': data['vendor'],
            'ip_address': data['ip_address'],
            'snmp_port': data.get('snmp_port', 161),
            'ssh_port': data.get('ssh_port', 22),
            'snmp_community': data.get('snmp_community', 'public'),
            'username': data.get('username'),
            'password': data.get('password'),
            'connection_method': data.get('connection_method', 'SNMP'),
            'status': 'UNKNOWN'
        }
        
        created_device = db_service.create_device(device_data)
        
        # Try to connect and get device info
        device_config = {
            'id': device_id,
            'model': data['model'],
            'vendor': data['vendor'],
            'ip_address': data['ip_address'],
            'snmp_port': data.get('snmp_port', 161),
            'ssh_port': data.get('ssh_port', 22),
            'snmp_community': data.get('snmp_community', 'public'),
            'username': data.get('username'),
            'password': data.get('password'),
        }
        
        connect_result = await olt_manager.connect_device(device_config)
        
        if connect_result.success:
            # Get device info
            adapter = olt_manager.get_adapter(device_id)
            info_result = await adapter.get_device_info()
            
            if info_result.success:
                info = info_result.data
                device_updates = {
                    'status': 'ONLINE',
                    'cpu_usage': info.cpu_usage,
                    'memory_usage': info.memory_usage,
                    'temperature': info.temperature,
                    'firmware_version': info.firmware_version,
                    'serial_number': info.serial_number,
                    'total_onu_count': info.total_onu_count,
                    'online_onu_count': info.online_onu_count,
                    'last_check_at': datetime.utcnow()
                }
                db_service.update_device(device_id, device_updates)
            
            log_operation(device_id, 'REGISTER', 'SUCCESS', 'Device registered')
        else:
            db_service.update_device(device_id, {'status': 'ERROR'})
            log_operation(device_id, 'REGISTER', 'FAILED', connect_result.message)
        
        # Get updated device
        final_device = db_service.get_device(device_id)
        
        return jsonify({
            'success': True,
            'message': 'Device registered successfully',
            'data': final_device
        }), 201
    
    except Exception as e:
        logger.error(f"Error registering device: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@olt_bp.route('/devices/<device_id>', methods=['PUT'])
@async_handler
async def update_device(device_id):
    """Update device configuration"""
    try:
        device = OLTDevice.query.get(device_id)
        if not device:
            return jsonify({
                'success': False,
                'message': 'Device not found'
            }), 404
        
        data = request.get_json()
        
        # Update fields
        if 'snmp_community' in data:
            device.snmp_community = data['snmp_community']
        if 'username' in data:
            device.username = data['username']
        if 'password' in data:
            device.password = data['password']
        if 'connection_method' in data:
            device.connection_method = data['connection_method']
        
        db.session.commit()
        log_operation(device_id, 'UPDATE', 'SUCCESS', 'Device updated')
        
        return jsonify({
            'success': True,
            'message': 'Device updated',
            'data': device.to_dict()
        })
    
    except Exception as e:
        logger.error(f"Error updating device: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@olt_bp.route('/devices/<device_id>', methods=['DELETE'])
def delete_device(device_id):
    """Delete device"""
    try:
        device = db_service.get_device(device_id)
        if not device:
            return jsonify({
                'success': False,
                'message': 'Device not found'
            }), 404
        
        # Remove adapter
        olt_manager.remove_adapter(device_id)
        
        # Delete device and related data using service
        if db_service.delete_device(device_id):
            log_operation(device_id, 'DELETE', 'SUCCESS', 'Device deleted')
            
            return jsonify({
                'success': True,
                'message': 'Device deleted'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to delete device'
            }), 500
    
    except Exception as e:
        logger.error(f"Error deleting device: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ==================== ONU Management ====================

@olt_bp.route('/devices/<device_id>/onus', methods=['GET'])
def get_onus(device_id):
    """Get ONUs for specific device"""
    try:
        onus = db_service.get_onus_by_device(device_id)
        return jsonify({
            'success': True,
            'data': onus
        })
    except Exception as e:
        logger.error(f"Error getting ONUs: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@olt_bp.route('/devices/<device_id>/onus/discover', methods=['POST'])
@async_handler
async def discover_onus(device_id):
    """Discover ONUs on device"""
    try:
        device = db_service.get_device(device_id)
        if not device:
            return jsonify({
                'success': False,
                'message': 'Device not found'
            }), 404
        
        data = request.get_json() or {}
        port_id = data.get('port_id')
        
        # Execute discovery
        result = await olt_manager.execute_operation(
            device_id,
            'discover_onus',
            port_id=port_id
        )
        
        if result.success:
            # Save ONUs to database using service layer
            onus_data = result.data or []
            for onu_info in onus_data:
                onu_dict = {
                    'id': onu_info.id,
                    'device_id': device_id,
                    'port_id': onu_info.port_id,
                    'onu_index': onu_info.onu_index,
                    'serial_number': onu_info.serial_number,
                    'mac_address': onu_info.mac_address,
                    'ip_address': onu_info.ip_address,
                    'status': onu_info.status,
                    'vendor_name': onu_info.vendor_name,
                    'optical_power_downstream': onu_info.optical_power_downstream,
                    'optical_power_upstream': onu_info.optical_power_upstream,
                    'distance_km': onu_info.distance_km
                }
                
                # Check if ONU exists
                existing_onu = db_service.get_onu(onu_info.id)
                if not existing_onu:
                    db_service.create_onu(onu_dict)
                else:
                    db_service.update_onu(onu_info.id, {
                        'status': onu_info.status,
                        'optical_power_downstream': onu_info.optical_power_downstream,
                        'optical_power_upstream': onu_info.optical_power_upstream,
                        'updated_at': datetime.utcnow()
                    })
            
            # Update device ONU count
            total_onus = len(onus_data)
            online_count = sum(1 for o in onus_data if o.status == 'ONLINE')
            db_service.update_device(device_id, {
                'total_onu_count': total_onus,
                'online_onu_count': online_count
            })
            
            log_operation(device_id, 'DISCOVER_ONU', 'SUCCESS', f'Discovered {len(onus_data)} ONUs')
        
        # Get all ONUs for this device
        all_onus = db_service.get_onus_by_device(device_id)
        
        return jsonify({
            'success': result.success,
            'message': result.message,
            'data': all_onus if result.success else None
        })
    
    except Exception as e:
        logger.error(f"Error discovering ONUs: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@olt_bp.route('/devices/<device_id>/onus/<onu_id>/configure', methods=['POST'])
@async_handler
async def configure_onu(device_id, onu_id):
    """Configure ONU"""
    try:
        onu = ONU.query.get(onu_id)
        if not onu:
            return jsonify({
                'success': False,
                'message': 'ONU not found'
            }), 404
        
        data = request.get_json()
        
        # Execute configuration
        result = await olt_manager.execute_operation(
            device_id,
            'configure_onu',
            port_id=onu.port_id,
            onu_index=onu.onu_index,
            config=data
        )
        
        if result.success:
            # Update ONU with new config
            if 'vlan_id' in data:
                onu.vlan_id = data['vlan_id']
            if 'description' in data:
                onu.description = data['description']
            onu.updated_at = datetime.utcnow()
            
            db.session.commit()
            log_operation(device_id, 'CONFIGURE_ONU', 'SUCCESS', f'Configured {onu_id}')
        
        return jsonify({
            'success': result.success,
            'message': result.message
        })
    
    except Exception as e:
        logger.error(f"Error configuring ONU: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@olt_bp.route('/devices/<device_id>/onus/<onu_id>/reset', methods=['POST'])
@async_handler
async def reset_onu(device_id, onu_id):
    """Reset ONU"""
    try:
        onu = ONU.query.get(onu_id)
        if not onu:
            return jsonify({
                'success': False,
                'message': 'ONU not found'
            }), 404
        
        result = await olt_manager.execute_operation(
            device_id,
            'reset_onu',
            port_id=onu.port_id,
            onu_index=onu.onu_index
        )
        
        if result.success:
            log_operation(device_id, 'RESET_ONU', 'SUCCESS', f'Reset {onu_id}')
        
        return jsonify({
            'success': result.success,
            'message': result.message
        })
    
    except Exception as e:
        logger.error(f"Error resetting ONU: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ==================== Port Management ====================

@olt_bp.route('/ports', methods=['GET'])
def get_ports_query():
    """Get all ports for device (using query parameters)"""
    try:
        device_id = request.args.get('deviceId') or request.args.get('device_id')
        port_type = request.args.get('type', 'all').upper()
        
        if not device_id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_DEVICE_ID',
                    'message': 'deviceId parameter is required'
                }
            }), 400
        
        pon_ports = []
        eth_ports = []
        
        if port_type in ['ALL', 'PON']:
            pon_ports = db_service.get_pon_ports_by_device(device_id)
        
        if port_type in ['ALL', 'ETH']:
            eth_ports = db_service.get_ethernet_ports_by_device(device_id)
        
        return jsonify({
            'success': True,
            'data': {
                'pon_ports': pon_ports,
                'eth_ports': eth_ports
            }
        })
    except Exception as e:
        logger.error(f"Error getting ports: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'DEVICE_NOT_FOUND',
                'message': f'Device {request.args.get("deviceId")} not registered'
            }
        }), 404


@olt_bp.route('/devices/<device_id>/ports', methods=['GET'])
def get_ports(device_id):
    """Get all ports for device"""
    try:
        port_type = request.args.get('type', 'all').upper()
        
        pon_ports = []
        eth_ports = []
        
        if port_type in ['ALL', 'PON']:
            pon_ports = db_service.get_pon_ports_by_device(device_id)
        
        if port_type in ['ALL', 'ETH']:
            eth_ports = db_service.get_ethernet_ports_by_device(device_id)
        
        return jsonify({
            'success': True,
            'data': {
                'pon_ports': pon_ports,
                'eth_ports': eth_ports
            }
        })
    except Exception as e:
        logger.error(f"Error getting ports: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@olt_bp.route('/devices/<device_id>/ports/<port_id>/enable', methods=['POST'])
@async_handler
async def enable_port(device_id, port_id):
    """Enable port"""
    try:
        port_type = request.get_json().get('type', 'PON')
        port_number = int(port_id)
        
        result = await olt_manager.execute_operation(
            device_id,
            'enable_port',
            port_id=port_number,
            port_type=port_type
        )
        
        if result.success:
            log_operation(device_id, 'ENABLE_PORT', 'SUCCESS', f'Enabled {port_type} port {port_id}')
        
        return jsonify({
            'success': result.success,
            'message': result.message
        })
    
    except Exception as e:
        logger.error(f"Error enabling port: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@olt_bp.route('/devices/<device_id>/ports/<port_id>/disable', methods=['POST'])
@async_handler
async def disable_port(device_id, port_id):
    """Disable port"""
    try:
        port_type = request.get_json().get('type', 'PON')
        port_number = int(port_id)
        
        result = await olt_manager.execute_operation(
            device_id,
            'disable_port',
            port_id=port_number,
            port_type=port_type
        )
        
        if result.success:
            log_operation(device_id, 'DISABLE_PORT', 'SUCCESS', f'Disabled {port_type} port {port_id}')
        
        return jsonify({
            'success': result.success,
            'message': result.message
        })
    
    except Exception as e:
        logger.error(f"Error disabling port: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ==================== System Endpoints ====================

@olt_bp.route('/supported-models', methods=['GET'])
def get_supported_models():
    """Get list of supported OLT models"""
    return jsonify({
        'success': True,
        'data': SUPPORTED_OLT_MODELS
    })


@olt_bp.route('/devices/<device_id>/health', methods=['GET'])
@async_handler
async def health_check(device_id):
    """Health check device"""
    try:
        is_healthy = await olt_manager.health_check(device_id)
        
        return jsonify({
            'success': True,
            'data': {
                'device_id': device_id,
                'healthy': is_healthy
            }
        })
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
