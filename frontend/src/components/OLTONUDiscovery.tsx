import React, { useEffect, useState } from 'react';
import { Search, Zap, RefreshCw, AlertCircle } from 'lucide-react';
import { useOLTAPI } from '../hooks/useOLTAPI';
import { useOLTWebSocket } from '../hooks/useOLTWebSocket';

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

interface Props {
  deviceId: string;
}

export const OLTONUDiscovery: React.FC<Props> = ({ deviceId }) => {
  const { getONUs, discoverONUs, resetONU, loading, error } = useOLTAPI();
  const { isConnected, discoverONUs: socketDiscoverONUs } = useOLTWebSocket();
  const [onus, setONUs] = useState<ONU[]>([]);
  const [discovering, setDiscovering] = useState(false);
  const [selectedPort, setSelectedPort] = useState<number | undefined>();

  useEffect(() => {
    loadONUs();
  }, [deviceId]);

  const loadONUs = async () => {
    const data = await getONUs(deviceId);
    setONUs(data);
  };

  const handleDiscover = async () => {
    setDiscovering(true);
    if (isConnected) {
      socketDiscoverONUs(deviceId, selectedPort);
    } else {
      const data = await discoverONUs(deviceId, selectedPort);
      setONUs(data);
    }
    setDiscovering(false);
  };

  const handleReset = async (onuId: string) => {
    const success = await resetONU(deviceId, onuId);
    if (success) {
      loadONUs();
    }
  };

  return (
    <div className="space-y-5">
      <div className="bg-gradient-to-br from-slate-700 to-slate-800 border border-slate-600 rounded-lg p-4">
        <h3 className="font-semibold mb-4 text-white flex items-center gap-2">
          <Search className="w-5 h-5 text-cyan-400" />
          ONU Discovery
        </h3>
        
        <div className="flex gap-3 items-end">
          <div className="flex-1 max-w-xs">
            <label className="block text-sm text-slate-300 mb-2 font-medium">
              Port (leave empty for all)
            </label>
            <input
              type="number"
              value={selectedPort || ''}
              onChange={(e) => setSelectedPort(e.target.value ? parseInt(e.target.value) : undefined)}
              placeholder="Port number"
              className="w-full border border-slate-500 rounded-lg px-3 py-2 bg-slate-600 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-400 transition-all"
            />
          </div>
          <button
            onClick={handleDiscover}
            disabled={discovering || loading}
            className="bg-gradient-to-r from-blue-600 to-cyan-600 text-white px-4 py-2 rounded-lg hover:from-blue-700 hover:to-cyan-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-all flex items-center gap-2"
          >
            {discovering ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Discovering...
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                Start Discovery
              </>
            )}
          </button>
        </div>

        {error && (
          <div className="mt-4 bg-red-500/20 border border-red-500/50 rounded-lg p-3 text-red-200 text-sm flex items-start gap-2">
            <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
            {error}
          </div>
        )}
      </div>

      <div>
        <h3 className="font-semibold mb-4 text-white flex items-center gap-2">
          <Zap className="w-5 h-5 text-yellow-400" />
          Discovered ONUs ({onus.length})
        </h3>
        
        {onus.length === 0 ? (
          <div className="bg-gradient-to-br from-slate-700/50 to-slate-800/50 border border-slate-600 rounded-lg p-8 text-center">
            <Search className="w-12 h-12 text-slate-500 mx-auto mb-3 opacity-50" />
            <p className="text-slate-400">No ONUs discovered yet</p>
          </div>
        ) : (
          <div className="space-y-3">
            {onus.map((onu) => (
              <div key={onu.id} className="bg-gradient-to-br from-slate-700 to-slate-800 border border-slate-600 rounded-lg p-4 hover:border-cyan-500 transition-all">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h4 className="font-semibold text-white">
                      PON {onu.port_id} / ONU {onu.onu_index}
                    </h4>
                    <p className="text-sm text-slate-400 mt-1">
                      Serial: {onu.serial_number}
                    </p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    onu.status === 'ONLINE'
                      ? 'bg-green-500/30 text-green-200 border border-green-500/50'
                      : 'bg-red-500/30 text-red-200 border border-red-500/50'
                  }`}>
                    {onu.status}
                  </span>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm mb-4">
                  <div>
                    <span className="text-slate-400">MAC:</span>
                    <p className="font-mono text-xs text-white mt-1">{onu.mac_address}</p>
                  </div>
                  <div>
                    <span className="text-slate-400">Distance:</span>
                    <p className="font-semibold text-white mt-1">{onu.distance_km.toFixed(2)} km</p>
                  </div>
                  <div>
                    <span className="text-slate-400">Power (DS):</span>
                    <p className="font-semibold text-white mt-1">{onu.optical_power_downstream.toFixed(1)} dBm</p>
                  </div>
                  <div>
                    <span className="text-slate-400">Power (US):</span>
                    <p className="font-semibold text-white mt-1">{onu.optical_power_upstream.toFixed(1)} dBm</p>
                  </div>
                </div>

                <button
                  onClick={() => handleReset(onu.id)}
                  className="bg-orange-600 hover:bg-orange-700 text-white px-3 py-1.5 rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
                >
                  <RefreshCw className="w-3 h-3" />
                  Reset ONU
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
