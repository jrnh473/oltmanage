import { useEffect, useRef, useState, useCallback } from 'react';
import io, { Socket } from 'socket.io-client';

interface UseOLTWebSocketProps {
  url?: string;
  enabled?: boolean;
}

export const useOLTWebSocket = ({
  url = 'http://10.100.93.129:5000',
  enabled = true
}: UseOLTWebSocketProps = {}) => {
  const socketRef = useRef<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [deviceUpdates, setDeviceUpdates] = useState<Record<string, any>>({});
  const [onuStatusChanges, setOnuStatusChanges] = useState<Record<string, string>>({});
  const [portStatusChanges, setPortStatusChanges] = useState<Record<string, any>>({});

  // Connect to Socket.IO server
  useEffect(() => {
    if (!enabled) return;

    if (!socketRef.current) {
      socketRef.current = io(url, {
        transports: ['websocket', 'polling'],
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionDelayMax: 5000,
        reconnectionAttempts: 5,
        autoConnect: true
      });

      // Connection events
      socketRef.current.on('connect', () => {
        console.log('[Socket.IO] Connected to server');
        setIsConnected(true);
      });

      socketRef.current.on('disconnect', () => {
        console.log('[Socket.IO] Disconnected from server');
        setIsConnected(false);
      });

      socketRef.current.on('connection_response', (data) => {
        console.log('[Socket.IO] Connection response:', data);
      });

      // Device update events
      socketRef.current.on('device_update', (data) => {
        console.log('[Socket.IO] Device update:', data);
        setDeviceUpdates((prev) => ({
          ...prev,
          [data.device_id]: data.data
        }));
      });

      socketRef.current.on('device_status', (data) => {
        console.log('[Socket.IO] Device status:', data);
        if (data.success) {
          setDeviceUpdates((prev) => ({
            ...prev,
            [data.data.id]: data.data
          }));
        }
      });

      // ONU discovery events
      socketRef.current.on('discovery_started', (data) => {
        console.log('[Socket.IO] Discovery started:', data);
      });

      socketRef.current.on('discovery_progress', (data) => {
        console.log('[Socket.IO] Discovery progress:', data);
      });

      socketRef.current.on('discovery_complete', (data) => {
        console.log('[Socket.IO] Discovery complete:', data);
      });

      socketRef.current.on('discovery_error', (data) => {
        console.error('[Socket.IO] Discovery error:', data);
      });

      // ONU status events
      socketRef.current.on('onu_status_change', (data) => {
        console.log('[Socket.IO] ONU status change:', data);
        setOnuStatusChanges((prev) => ({
          ...prev,
          [data.onu_id]: data.status
        }));
      });

      // ONU configuration events
      socketRef.current.on('configure_started', (data) => {
        console.log('[Socket.IO] Configuration started:', data);
      });

      socketRef.current.on('configure_complete', (data) => {
        console.log('[Socket.IO] Configuration complete:', data);
      });

      socketRef.current.on('configure_error', (data) => {
        console.error('[Socket.IO] Configuration error:', data);
      });

      // ONU reset events
      socketRef.current.on('reset_started', (data) => {
        console.log('[Socket.IO] Reset started:', data);
      });

      socketRef.current.on('reset_complete', (data) => {
        console.log('[Socket.IO] Reset complete:', data);
      });

      socketRef.current.on('reset_error', (data) => {
        console.error('[Socket.IO] Reset error:', data);
      });

      // Port status events
      socketRef.current.on('port_status_change', (data) => {
        console.log('[Socket.IO] Port status change:', data);
        setPortStatusChanges((prev) => ({
          ...prev,
          [data.port_id]: { status: data.status, port_type: data.port_type }
        }));
      });

      // Port info events
      socketRef.current.on('port_info', (data) => {
        console.log('[Socket.IO] Port info:', data);
      });

      // Connection response
      socketRef.current.on('subscribe_response', (data) => {
        console.log('[Socket.IO] Subscribed:', data);
      });

      socketRef.current.on('unsubscribe_response', (data) => {
        console.log('[Socket.IO] Unsubscribed:', data);
      });
    }

    return () => {
      // Note: Don't disconnect on unmount to maintain connection across components
      // Only disconnect when app unmounts or connection is explicitly disabled
    };
  }, [enabled, url]);

  // Subscribe to device
  const subscribeToDevice = useCallback((deviceId: string) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('subscribe_device', { device_id: deviceId });
    }
  }, []);

  // Unsubscribe from device
  const unsubscribeFromDevice = useCallback((deviceId: string) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('unsubscribe_device', { device_id: deviceId });
    }
  }, []);

  // Get device status
  const getDeviceStatus = useCallback((deviceId: string) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('get_device_status', { device_id: deviceId });
    }
  }, []);

  // Start ONU discovery
  const discoverONUs = useCallback((deviceId: string, portId?: number) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('discover_onus_start', {
        device_id: deviceId,
        port_id: portId
      });
    }
  }, []);

  // Configure ONU
  const configureONU = useCallback((deviceId: string, onuId: string, config: Record<string, any>) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('configure_onu', {
        device_id: deviceId,
        onu_id: onuId,
        config
      });
    }
  }, []);

  // Reset ONU
  const resetONU = useCallback((deviceId: string, onuId: string) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('reset_onu', {
        device_id: deviceId,
        onu_id: onuId
      });
    }
  }, []);

  // Get port info
  const getPortInfo = useCallback((deviceId: string, portId: string, portType: string = 'PON') => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('get_port_info', {
        device_id: deviceId,
        port_id: portId,
        port_type: portType
      });
    }
  }, []);

  // Disconnect socket
  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.disconnect();
      socketRef.current = null;
      setIsConnected(false);
    }
  }, []);

  return {
    socket: socketRef.current,
    isConnected,
    deviceUpdates,
    onuStatusChanges,
    portStatusChanges,
    subscribeToDevice,
    unsubscribeFromDevice,
    getDeviceStatus,
    discoverONUs,
    configureONU,
    resetONU,
    getPortInfo,
    disconnect
  };
};
