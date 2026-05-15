import { useState, useCallback } from 'react';
import axios, { AxiosError } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://10.100.93.129:5000/api';

interface APIResponse<T> {
  success: boolean;
  message?: string;
  data?: T;
  error_code?: string;
}

interface Device {
  id: string;
  model: string;
  vendor: string;
  ip_address: string;
  status: string;
  cpu_usage: number;
  memory_usage: number;
  temperature: number;
  total_onu_count: number;
  online_onu_count: number;
  created_at: string;
}

interface ONU {
  id: string;
  device_id: string;
  port_id: number;
  onu_index: number;
  serial_number: string;
  mac_address: string;
  status: string;
  optical_power_downstream: number;
  optical_power_upstream: number;
  distance_km: number;
  updated_at: string;
}

interface Port {
  id: string;
  device_id: string;
  port_number: number;
  port_name: string;
  status: string;
  port_type: string;
  updated_at: string;
}

export const useOLTAPI = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleError = (err: unknown) => {
    if (axios.isAxiosError(err)) {
      const axiosError = err as AxiosError<APIResponse<any>>;
      const message = axiosError.response?.data?.message || axiosError.message;
      setError(String(message));
      console.error('[OLT API Error]', message);
    } else {
      setError(String(err));
      console.error('[OLT API Error]', err);
    }
  };

  // Get all devices
  const getDevices = useCallback(async (): Promise<Device[]> => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get<APIResponse<Device[]>>(
        `${API_BASE_URL}/olt/devices`
      );
      return response.data.data || [];
    } catch (err) {
      handleError(err);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  // Get device by ID
  const getDevice = useCallback(async (deviceId: string): Promise<Device | null> => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get<APIResponse<Device>>(
        `${API_BASE_URL}/olt/devices/${deviceId}`
      );
      return response.data.data || null;
    } catch (err) {
      handleError(err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Register new device
  const registerDevice = useCallback(async (deviceData: {
    model: string;
    vendor: string;
    ip_address: string;
    snmp_port?: number;
    ssh_port?: number;
    snmp_community?: string;
    username?: string;
    password?: string;
    connection_method?: string;
  }): Promise<Device | null> => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post<APIResponse<Device>>(
        `${API_BASE_URL}/olt/devices`,
        deviceData
      );
      return response.data.data || null;
    } catch (err) {
      handleError(err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Update device
  const updateDevice = useCallback(async (deviceId: string, data: Partial<Device>): Promise<Device | null> => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.put<APIResponse<Device>>(
        `${API_BASE_URL}/olt/devices/${deviceId}`,
        data
      );
      return response.data.data || null;
    } catch (err) {
      handleError(err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Delete device
  const deleteDevice = useCallback(async (deviceId: string): Promise<boolean> => {
    setLoading(true);
    setError(null);
    try {
      await axios.delete<APIResponse<any>>(
        `${API_BASE_URL}/olt/devices/${deviceId}`
      );
      return true;
    } catch (err) {
      handleError(err);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  // Get ONUs
  const getONUs = useCallback(async (deviceId: string): Promise<ONU[]> => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get<APIResponse<ONU[]>>(
        `${API_BASE_URL}/olt/devices/${deviceId}/onus`
      );
      return response.data.data || [];
    } catch (err) {
      handleError(err);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  // Discover ONUs
  const discoverONUs = useCallback(async (deviceId: string, portId?: number): Promise<ONU[]> => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post<APIResponse<ONU[]>>(
        `${API_BASE_URL}/olt/devices/${deviceId}/onus/discover`,
        { port_id: portId }
      );
      return response.data.data || [];
    } catch (err) {
      handleError(err);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  // Configure ONU
  const configureONU = useCallback(async (
    deviceId: string,
    onuId: string,
    config: Record<string, any>
  ): Promise<boolean> => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post<APIResponse<any>>(
        `${API_BASE_URL}/olt/devices/${deviceId}/onus/${onuId}/configure`,
        config
      );
      return response.data.success;
    } catch (err) {
      handleError(err);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  // Reset ONU
  const resetONU = useCallback(async (deviceId: string, onuId: string): Promise<boolean> => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post<APIResponse<any>>(
        `${API_BASE_URL}/olt/devices/${deviceId}/onus/${onuId}/reset`
      );
      return response.data.success;
    } catch (err) {
      handleError(err);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  // Get ports
  const getPorts = useCallback(async (deviceId: string, type: string = 'all'): Promise<{
    pon_ports: Port[];
    eth_ports: Port[];
  }> => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get<APIResponse<{
        pon_ports: Port[];
        eth_ports: Port[];
      }>>(
        `${API_BASE_URL}/olt/devices/${deviceId}/ports`,
        { params: { type } }
      );
      return response.data.data || { pon_ports: [], eth_ports: [] };
    } catch (err) {
      handleError(err);
      return { pon_ports: [], eth_ports: [] };
    } finally {
      setLoading(false);
    }
  }, []);

  // Enable port
  const enablePort = useCallback(async (
    deviceId: string,
    portId: string,
    portType: string = 'PON'
  ): Promise<boolean> => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post<APIResponse<any>>(
        `${API_BASE_URL}/olt/devices/${deviceId}/ports/${portId}/enable`,
        { type: portType }
      );
      return response.data.success;
    } catch (err) {
      handleError(err);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  // Disable port
  const disablePort = useCallback(async (
    deviceId: string,
    portId: string,
    portType: string = 'PON'
  ): Promise<boolean> => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post<APIResponse<any>>(
        `${API_BASE_URL}/olt/devices/${deviceId}/ports/${portId}/disable`,
        { type: portType }
      );
      return response.data.success;
    } catch (err) {
      handleError(err);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  // Get supported models
  const getSupportedModels = useCallback(async (): Promise<Record<string, any>> => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get<APIResponse<Record<string, any>>>(
        `${API_BASE_URL}/olt/supported-models`
      );
      return response.data.data || {};
    } catch (err) {
      handleError(err);
      return {};
    } finally {
      setLoading(false);
    }
  }, []);

  // Health check
  const healthCheck = useCallback(async (deviceId: string): Promise<boolean> => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get<APIResponse<{ healthy: boolean }>>(
        `${API_BASE_URL}/olt/devices/${deviceId}/health`
      );
      return response.data.data?.healthy || false;
    } catch (err) {
      handleError(err);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    getDevices,
    getDevice,
    registerDevice,
    updateDevice,
    deleteDevice,
    getONUs,
    discoverONUs,
    configureONU,
    resetONU,
    getPorts,
    enablePort,
    disablePort,
    getSupportedModels,
    healthCheck
  };
};
