import React, { useEffect, useState } from 'react';
import { Activity, Zap, AlertCircle, CheckCircle, Power } from 'lucide-react';
import { useOLTAPI } from '../hooks/useOLTAPI';

interface Port {
  id: string;
  device_id: string;
  port_number: number;
  port_name: string;
  status: string;
  port_type: string;
  updated_at: string;
}

interface PortsData {
  pon_ports: Port[];
  eth_ports: Port[];
}

interface Props {
  deviceId: string;
}

export const OLTPorts: React.FC<Props> = ({ deviceId }) => {
  const { getPorts, loading, error, enablePort, disablePort } = useOLTAPI();
  const [ports, setPorts] = useState<PortsData>({ pon_ports: [], eth_ports: [] });
  const [operatingPort, setOperatingPort] = useState<string | null>(null);

  useEffect(() => {
    fetchPorts();
  }, [deviceId]);

  const fetchPorts = async () => {
    const data = await getPorts(deviceId);
    setPorts(data);
  };

  const handlePortToggle = async (portId: string, portType: string, currentStatus: string) => {
    setOperatingPort(portId);
    try {
      const isEnabled = currentStatus === 'UP';
      const result = isEnabled 
        ? await disablePort(deviceId, portId, portType)
        : await enablePort(deviceId, portId, portType);

      if (result) {
        await fetchPorts();
      }
    } finally {
      setOperatingPort(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-slate-300 border-t-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800 flex gap-3">
        <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
        <div>
          <p className="font-semibold">Error Loading Ports</p>
          <p className="text-sm mt-1">{error}</p>
        </div>
      </div>
    );
  }

  const allPorts = [...ports.pon_ports, ...ports.eth_ports];

  if (allPorts.length === 0) {
    return (
      <div className="text-center py-12">
        <Activity className="w-12 h-12 text-slate-400 mx-auto mb-3" />
        <p className="text-slate-600">No ports discovered yet</p>
        <p className="text-sm text-slate-500 mt-2">Ports will appear once device discovery is complete</p>
      </div>
    );
  }

  const renderPortCard = (port: Port) => {
    const isOnline = port.status === 'UP';
    const isOperating = operatingPort === port.id;

    return (
      <div
        key={port.id}
        className={`rounded-lg p-4 border transition-all ${
          isOnline
            ? 'bg-gradient-to-br from-green-50 to-green-100/50 border-green-200'
            : 'bg-gradient-to-br from-slate-50 to-slate-100/50 border-slate-200'
        }`}
      >
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            {port.port_type === 'PON' ? (
              <Zap className={`w-5 h-5 ${isOnline ? 'text-green-600' : 'text-slate-600'}`} />
            ) : (
              <Activity className={`w-5 h-5 ${isOnline ? 'text-blue-600' : 'text-slate-600'}`} />
            )}
            <div>
              <p className="font-semibold text-gray-900">{port.port_name}</p>
              <p className="text-xs text-slate-600">Port {port.port_number}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {isOnline ? (
              <span className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-full bg-green-200 text-green-700 text-xs font-medium">
                <CheckCircle className="w-3 h-3" />
                Online
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-full bg-slate-200 text-slate-700 text-xs font-medium">
                <AlertCircle className="w-3 h-3" />
                Offline
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center justify-between">
          <p className="text-xs text-slate-600">
            Last updated: {new Date(port.updated_at).toLocaleString()}
          </p>
          <button
            onClick={() => handlePortToggle(port.id, port.port_type, port.status)}
            disabled={isOperating}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
              isOnline
                ? 'bg-red-100 text-red-700 hover:bg-red-200 disabled:opacity-50 disabled:cursor-not-allowed'
                : 'bg-green-100 text-green-700 hover:bg-green-200 disabled:opacity-50 disabled:cursor-not-allowed'
            }`}
          >
            {isOperating ? (
              <>
                <div className="animate-spin rounded-full h-3 w-3 border-2 border-current border-t-transparent"></div>
                {isOnline ? 'Disabling...' : 'Enabling...'}
              </>
            ) : (
              <>
                <Power className="w-3 h-3" />
                {isOnline ? 'Disable' : 'Enable'}
              </>
            )}
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {ports.pon_ports.length > 0 && (
        <div>
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <Zap className="w-5 h-5 text-amber-600" />
            PON Ports ({ports.pon_ports.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {ports.pon_ports.map(renderPortCard)}
          </div>
        </div>
      )}

      {ports.eth_ports.length > 0 && (
        <div>
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <Activity className="w-5 h-5 text-blue-600" />
            Ethernet Ports ({ports.eth_ports.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {ports.eth_ports.map(renderPortCard)}
          </div>
        </div>
      )}
    </div>
  );
};
