import React, { useEffect, useState } from 'react';
import { Activity, Zap, Gauge, X, Monitor, Server, Clock } from 'lucide-react';
import { useOLTAPI } from '../hooks/useOLTAPI';
import { useOLTWebSocket } from '../hooks/useOLTWebSocket';
import { OLTPorts } from './OLTPorts';

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

interface Props {
  deviceId: string;
  onClose: () => void;
}

export const OLTDeviceDetails: React.FC<Props> = ({ deviceId, onClose }) => {
  const { getDevice, loading, error } = useOLTAPI();
  const { deviceUpdates, subscribeToDevice, unsubscribeFromDevice } = useOLTWebSocket();
  const [device, setDevice] = useState<Device | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'onus' | 'ports'>('overview');

  useEffect(() => {
    fetchDevice();
    subscribeToDevice(deviceId);
    return () => unsubscribeFromDevice(deviceId);
  }, [deviceId]);

  useEffect(() => {
    if (deviceUpdates[deviceId]) {
      setDevice((prev) => prev ? { ...prev, ...deviceUpdates[deviceId] } : null);
    }
  }, [deviceUpdates, deviceId]);

  const fetchDevice = async () => {
    const data = await getDevice(deviceId);
    setDevice(data);
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-md flex items-center justify-center z-[100]">
        <div className="flex flex-col items-center gap-4">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          <p className="text-slate-400 font-medium animate-pulse">Loading Device Core...</p>
        </div>
      </div>
    );
  }

  if (!device) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[100] p-4">
      <div className="bg-slate-900 border border-white/10 rounded-[2rem] max-w-4xl w-full max-h-[90vh] overflow-hidden shadow-[0_0_50px_rgba(0,0,0,0.5)]">
        
        {/* Header - Dark Gradient */}
        <div className="px-8 py-6 bg-gradient-to-r from-slate-800 to-slate-900 border-b border-white/5 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-600/20 rounded-2xl border border-blue-500/30">
              <Gauge className="w-6 h-6 text-blue-400" />
            </div>
            <div>
              <h2 className="text-2xl font-black text-white tracking-tight">{device.model}</h2>
              <p className="text-xs text-slate-500 uppercase tracking-widest font-bold">Node Hardware Identity</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-red-500/20 text-slate-400 hover:text-red-400 transition-all rounded-xl border border-white/5"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-8 overflow-y-auto max-h-[calc(90vh-100px)] custom-scrollbar">
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 text-red-400 mb-6 flex items-center gap-3">
              <Activity className="w-5 h-5" /> {error}
            </div>
          )}

          {/* Styled Tabs */}
          <div className="flex gap-2 p-1 bg-black/20 rounded-2xl mb-8 border border-white/5 w-fit">
            {(['overview', 'onus', 'ports'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-6 py-2.5 rounded-xl text-sm font-bold transition-all flex items-center gap-2 ${
                  activeTab === tab
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20'
                    : 'text-slate-500 hover:text-slate-300'
                }`}
              >
                {tab === 'overview' && <Activity className="w-4 h-4" />}
                {tab === 'onus' && <Zap className="w-4 h-4" />}
                <span className="capitalize">{tab}</span>
              </button>
            ))}
          </div>

          {/* Overview Content */}
          {activeTab === 'overview' && (
            <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
              
              {/* Info Cards Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <InfoCard icon={<Server className="w-4 h-4 text-blue-400" />} label="Vendor" value={device.vendor} />
                <InfoCard 
                  label="Status" 
                  value={device.status} 
                  color={device.status === 'ONLINE' ? 'text-emerald-400' : 'text-red-400'} 
                />
                <InfoCard icon={<Monitor className="w-4 h-4 text-slate-400" />} label="IP Address" value={device.ip_address} />
                <InfoCard icon={<Clock className="w-4 h-4 text-purple-400" />} label="Model" value={device.model} />
              </div>

              {/* Performance Section */}
              <div className="bg-black/20 rounded-[2rem] p-8 border border-white/5">
                <h3 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
                  <Activity className="w-5 h-5 text-blue-500" />
                  Hardware Performance
                </h3>
                
                <div className="grid gap-8">
                  <ProgressMetric label="CPU Execution" value={device.cpu_usage} color="bg-blue-500" />
                  <ProgressMetric label="Memory Allocation" value={device.memory_usage} color="bg-emerald-500" />
                  
                  <div className="flex items-center justify-between p-4 bg-orange-500/5 rounded-2xl border border-orange-500/10 mt-2">
                    <span className="text-sm font-bold text-slate-400 uppercase tracking-wider">Operational Temperature</span>
                    <span className="text-2xl font-black text-orange-500">{device.temperature.toFixed(1)}°C</span>
                  </div>
                </div>
              </div>

              {/* ONU Statistics */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-gradient-to-br from-blue-600 to-blue-700 rounded-[2rem] p-6 shadow-xl relative overflow-hidden group">
                  <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:scale-110 transition-transform">
                    <Zap className="w-24 h-24" />
                  </div>
                  <p className="text-blue-100/80 font-bold text-xs uppercase tracking-[0.2em] mb-2">Capacity</p>
                  <p className="text-4xl font-black text-white">{device.total_onu_count}</p>
                  <p className="text-blue-200 text-sm mt-1">Total ONU Provisioned</p>
                </div>

                <div className="bg-gradient-to-br from-emerald-600 to-emerald-700 rounded-[2rem] p-6 shadow-xl relative overflow-hidden group">
                  <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:scale-110 transition-transform">
                    <Activity className="w-24 h-24" />
                  </div>
                  <p className="text-emerald-100/80 font-bold text-xs uppercase tracking-[0.2em] mb-2">Live Nodes</p>
                  <p className="text-4xl font-black text-white">{device.online_onu_count}</p>
                  <p className="text-emerald-200 text-sm mt-1">ONUs Currently Reachable</p>
                </div>
              </div>

              <div className="text-center pt-4">
                <p className="text-[10px] text-slate-600 uppercase tracking-[0.3em] font-bold">
                  Last Sync: {new Date(device.created_at).toLocaleString()}
                </p>
              </div>
            </div>
          )}

          {activeTab === 'ports' && <OLTPorts deviceId={deviceId} />}
          
          {activeTab === 'onus' && (
            <div className="flex flex-col items-center justify-center py-20 bg-black/20 rounded-[2rem] border border-dashed border-white/10">
               <Zap className="w-12 h-12 text-slate-700 mb-4" />
               <p className="text-slate-500 font-medium">ONU Management context active</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Helper Components
const InfoCard = ({ icon, label, value, color = "text-white" }: any) => (
  <div className="bg-white/5 border border-white/5 p-4 rounded-2xl">
    <div className="flex items-center gap-2 mb-1.5 opacity-50">
      {icon}
      <span className="text-[10px] font-black uppercase tracking-wider">{label}</span>
    </div>
    <p className={`font-bold truncate ${color}`}>{value}</p>
  </div>
);

const ProgressMetric = ({ label, value, color }: any) => (
  <div className="space-y-3">
    <div className="flex justify-between items-end">
      <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">{label}</span>
      <span className="text-lg font-black text-white">{value.toFixed(1)}%</span>
    </div>
    <div className="w-full bg-white/5 h-2 rounded-full overflow-hidden border border-white/5 p-0.5">
      <div 
        className={`${color} h-full rounded-full transition-all duration-1000 ease-out shadow-[0_0_10px_rgba(59,130,246,0.5)]`}
        style={{ width: `${Math.min(value, 100)}%` }}
      />
    </div>
  </div>
);
