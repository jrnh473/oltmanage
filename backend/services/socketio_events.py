import logging
from flask import request
from flask_socketio import emit, join_room, leave_room
from models.olt_models import OLTDevice, ONU, PONPort, EthernetPort
from services.olt_manager import olt_manager
import asyncio

logger = logging.getLogger(__name__)


def setup_socketio_events(socketio):
    """Register all Socket.IO event handlers"""
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""

        logger.info(f"Client connected: {request.sid}")

        emit('connection_response', {
            'data': 'Connected to OLT management server'
        })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        logger.info(f"Client disconnected: {request.sid}")
    
    # ==================== Device Monitoring ====================
    
    @socketio.on('subscribe_device')
    def handle_subscribe_device(data):
        """Subscribe to device real-time updates"""
        device_id = data.get('device_id')
        room = f"device_{device_id}"
        join_room(room)
        
        logger.info(f"Client subscribed to device {device_id}")
        emit('subscribe_response', {
            'success': True,
            'device_id': device_id,
            'message': f'Subscribed to device {device_id}'
        })
    
    @socketio.on('unsubscribe_device')
    def handle_unsubscribe_device(data):
        """Unsubscribe from device real-time updates"""
        device_id = data.get('device_id')
        room = f"device_{device_id}"
        leave_room(room)
        
        logger.info(f"Client unsubscribed from device {device_id}")
        emit('unsubscribe_response', {
            'success': True,
            'device_id': device_id
        })
    
    @socketio.on('get_device_status')
    def handle_get_device_status(data):
        """Get real-time device status"""
        device_id = data.get('device_id')
        
        try:
            device = OLTDevice.query.get(device_id)
            if not device:
                emit('device_status', {
                    'success': False,
                    'message': 'Device not found'
                })
                return
            
            emit('device_status', {
                'success': True,
                'data': {
                    'id': device.id,
                    'status': device.status,
                    'cpu_usage': device.cpu_usage,
                    'memory_usage': device.memory_usage,
                    'temperature': device.temperature,
                    'uptime_seconds': device.uptime_seconds,
                    'online_onu_count': device.online_onu_count,
                    'total_onu_count': device.total_onu_count,
                    'last_check_at': device.last_check_at.isoformat() if device.last_check_at else None
                }
            })
        except Exception as e:
            logger.error(f"Error getting device status: {str(e)}")
            emit('device_status', {
                'success': False,
                'message': str(e)
            })
    
    @socketio.on('discover_onus_start')
    def handle_discover_onus_start(data):
        """Start ONU discovery (async operation)"""
        device_id = data.get('device_id')
        port_id = data.get('port_id')
        
        def discover_async():
            """Run discovery in background"""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                async def discover():
                    # Emit progress
                    socketio.emit('discovery_progress', {
                        'device_id': device_id,
                        'status': 'STARTING',
                        'progress': 0
                    }, room=f"device_{device_id}")
                    
                    # Execute discovery
                    result = await olt_manager.execute_operation(
                        device_id,
                        'discover_onus',
                        port_id=port_id
                    )
                    
                    if result.success:
                        onus = ONU.query.filter_by(device_id=device_id).all()
                        socketio.emit('discovery_complete', {
                            'device_id': device_id,
                            'success': True,
                            'onu_count': len(onus),
                            'onus': [o.to_dict() for o in onus]
                        }, room=f"device_{device_id}")
                    else:
                        socketio.emit('discovery_error', {
                            'device_id': device_id,
                            'message': result.message,
                            'error_code': result.error_code
                        }, room=f"device_{device_id}")
                
                loop.run_until_complete(discover())
            except Exception as e:
                logger.error(f"Discovery error: {str(e)}")
                socketio.emit('discovery_error', {
                    'device_id': device_id,
                    'message': str(e)
                }, room=f"device_{device_id}")
            finally:
                loop.close()
        
        # Start async discovery in background
        import threading
        thread = threading.Thread(target=discover_async)
        thread.daemon = True
        thread.start()
        
        emit('discovery_started', {
            'device_id': device_id,
            'port_id': port_id,
            'message': 'ONU discovery started'
        })
    
    # ==================== ONU Management ====================
    
    @socketio.on('configure_onu')
    def handle_configure_onu(data):
        """Configure ONU (async operation)"""
        device_id = data.get('device_id')
        onu_id = data.get('onu_id')
        config = data.get('config', {})
        
        def configure_async():
            """Run configuration in background"""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                async def configure():
                    onu = ONU.query.get(onu_id)
                    if not onu:
                        socketio.emit('configure_error', {
                            'onu_id': onu_id,
                            'message': 'ONU not found'
                        }, room=f"device_{device_id}")
                        return
                    
                    result = await olt_manager.execute_operation(
                        device_id,
                        'configure_onu',
                        port_id=onu.port_id,
                        onu_index=onu.onu_index,
                        config=config
                    )
                    
                    if result.success:
                        socketio.emit('configure_complete', {
                            'onu_id': onu_id,
                            'success': True,
                            'message': result.message
                        }, room=f"device_{device_id}")
                    else:
                        socketio.emit('configure_error', {
                            'onu_id': onu_id,
                            'message': result.message
                        }, room=f"device_{device_id}")
                
                loop.run_until_complete(configure())
            except Exception as e:
                logger.error(f"Configuration error: {str(e)}")
                socketio.emit('configure_error', {
                    'onu_id': onu_id,
                    'message': str(e)
                }, room=f"device_{device_id}")
            finally:
                loop.close()
        
        # Start async configuration
        import threading
        thread = threading.Thread(target=configure_async)
        thread.daemon = True
        thread.start()
        
        emit('configure_started', {
            'onu_id': onu_id,
            'message': 'ONU configuration started'
        })
    
    @socketio.on('reset_onu')
    def handle_reset_onu(data):
        """Reset ONU"""
        device_id = data.get('device_id')
        onu_id = data.get('onu_id')
        
        def reset_async():
            """Run reset in background"""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                async def reset():
                    onu = ONU.query.get(onu_id)
                    if not onu:
                        socketio.emit('reset_error', {
                            'onu_id': onu_id,
                            'message': 'ONU not found'
                        }, room=f"device_{device_id}")
                        return
                    
                    result = await olt_manager.execute_operation(
                        device_id,
                        'reset_onu',
                        port_id=onu.port_id,
                        onu_index=onu.onu_index
                    )
                    
                    if result.success:
                        socketio.emit('reset_complete', {
                            'onu_id': onu_id,
                            'success': True,
                            'message': result.message
                        }, room=f"device_{device_id}")
                    else:
                        socketio.emit('reset_error', {
                            'onu_id': onu_id,
                            'message': result.message
                        }, room=f"device_{device_id}")
                
                loop.run_until_complete(reset())
            except Exception as e:
                logger.error(f"Reset error: {str(e)}")
                socketio.emit('reset_error', {
                    'onu_id': onu_id,
                    'message': str(e)
                }, room=f"device_{device_id}")
            finally:
                loop.close()
        
        # Start async reset
        import threading
        thread = threading.Thread(target=reset_async)
        thread.daemon = True
        thread.start()
        
        emit('reset_started', {
            'onu_id': onu_id,
            'message': 'ONU reset started'
        })
    
    # ==================== Port Management ====================
    
    @socketio.on('get_port_info')
    def handle_get_port_info(data):
        """Get real-time port information"""
        device_id = data.get('device_id')
        port_id = data.get('port_id')
        port_type = data.get('port_type', 'PON')
        
        try:
            if port_type == 'PON':
                port = PONPort.query.filter_by(id=port_id, device_id=device_id).first()
            else:
                port = EthernetPort.query.filter_by(id=port_id, device_id=device_id).first()
            
            if not port:
                emit('port_info', {
                    'success': False,
                    'message': 'Port not found'
                })
                return
            
            emit('port_info', {
                'success': True,
                'data': port.to_dict()
            })
        except Exception as e:
            logger.error(f"Error getting port info: {str(e)}")
            emit('port_info', {
                'success': False,
                'message': str(e)
            })
    
    # ==================== Broadcasting Functions ====================
    
    def broadcast_device_update(device_id, update_data):
        """Broadcast device status update to all subscribers"""
        socketio.emit('device_update', {
            'device_id': device_id,
            'data': update_data
        }, room=f"device_{device_id}")
    
    def broadcast_onu_status(device_id, onu_id, status):
        """Broadcast ONU status change"""
        socketio.emit('onu_status_change', {
            'device_id': device_id,
            'onu_id': onu_id,
            'status': status
        }, room=f"device_{device_id}")
    
    def broadcast_port_status(device_id, port_id, status, port_type='PON'):
        """Broadcast port status change"""
        socketio.emit('port_status_change', {
            'device_id': device_id,
            'port_id': port_id,
            'port_type': port_type,
            'status': status
        }, room=f"device_{device_id}")
    
    # Export broadcasting functions
    socketio.broadcast_device_update = broadcast_device_update
    socketio.broadcast_onu_status = broadcast_onu_status
    socketio.broadcast_port_status = broadcast_port_status
