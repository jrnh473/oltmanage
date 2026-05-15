import React, { useState, useEffect } from 'react';
import { Edit2, Trash2, Globe, Cpu, HardDrive, Thermometer, Loader2, RefreshCcw } from 'lucide-react';
import axios from 'axios';

interface Device {
  id: string;
  model: string;
  vendor: string;
  ip_address: string;
  status: string;
  cpu_usage: number;
  memory_usage: number;
  temperature: number;
  online_onu_count: number;
  total_onu_count: number;
}

export const OLTDeviceList: React.FC = () => {
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDevices = async () => {
    try {
      const response = await axios.get('http://10.100.93.129:5000/api/olt/devices');
      
      if (response.data.success) {
        setDevices(response.data.data);
      }
      setError(null);
    } catch (err) {
      setError('Backend connection failed!');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDevices();
    const interval = setInterval(fetchDevices, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleDelete = async (id: string) => {
    if (window.confirm('Delete this OLT device?')) {
      try {
        await axios.delete(`http://10.100.93.129:5000/api/olt/devices/${id}`);
        fetchDevices();
      } catch (err) {
        alert('Delete failed!');
      }
    }
  };

  if (loading && devices.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <Loader2 className="w-12 h-12 animate-spin text-blue-500 mb-4" />
        <p className="text-slate-500 animate-pulse">Connecting to OLT Nodes...</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 p-6">
      {devices.map((device) => (
        <div key={device.id} className="relative group bg-slate-800/40 backdrop-blur-xl border border-white/10 rounded-3xl p-6 hover:border-blue-500/50 transition-all duration-500">
          
          {/* Status & Actions */}
          <div className="flex justify-between items-start mb-6">
            <div className="flex items-center gap-4">
              <div className={`w-3.5 h-3.5 rounded-full shadow-[0_0_12px] ${
                device.status === 'ONLINE' ? 'bg-emerald-500 shadow-emerald-500/50 animate-pulse' : 
                device.status === 'OFFLINE' ? 'bg-red-500 shadow-red-500/50' : 'bg-slate-500 shadow-slate-500/50'
              }`} />
              <div>
                <h3 className="text-2xl font-black text-white tracking-tight">{device.model}</h3>
                <p className="text-xs font-bold text-slate-500 uppercase tracking-widest">{device.vendor} • {device.ip_address}</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <button className="p-2.5 bg-white/5 hover:bg-blue-600/20 rounded-xl text-slate-400 hover:text-blue-400 transition-all">
                <Edit2 className="w-4 h-4" />
              </button>
              <button 
                onClick={() => handleDelete(device.id)}
                className="p-2.5 bg-white/5 hover:bg-red-600/20 rounded-xl text-slate-400 hover:text-red-400 transition-all"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Real-time Metrics Grid */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            <MetricCard 
              icon={<Cpu className="w-4 h-4 text-cyan-400" />} 
              label="CPU Load" 
              value={`${device.cpu_usage.toFixed(1)}%`} 
              percent={device.cpu_usage} 
              barColor="bg-cyan-500" 
            />
            <MetricCard 
              icon={<HardDrive className="w-4 h-4 text-purple-400" />} 
              label="Memory" 
              value={`${device.memory_usage.toFixed(1)}%`} 
              percent={device.memory_usage} 
              barColor="bg-purple-500" 
            />
            <MetricCard 
              icon={<Thermometer className="w-4 h-4 text-orange-400" />} 
              label="Temp" 
              value={`${device.temperature.toFixed(1)}°C`} 
              percent={device.temperature > 100 ? 100 : device.temperature} 
              barColor="bg-orange-500" 
            />
          </div>

          {/* Footer Info */}
          <div className="flex items-center justify-between pt-5 border-t border-white/5">
            <div className="flex items-center gap-3">
              <div className="flex -space-x-2">
                <div className="w-8 h-8 rounded-full bg-blue-600/20 border border-blue-500/30 flex items-center justify-center">
                  <Globe className="w-4 h-4 text-blue-400" />
                </div>
              </div>
              <span className="text-sm font-medium text-slate-400">
                Connected ONUs: <span className="text-white font-bold">{device.online_onu_count}/{device.total_onu_count}</span>
              </span>
            </div>
            <button className="text-[10px] font-black uppercase tracking-widest text-blue-500 hover:text-cyan-400 transition-colors">
              Node Details ➜
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

const MetricCard = ({ icon, label, value, percent, barColor }: any) => (
  <div className="bg-black/20 border border-white/5 p-3 rounded-2xl">
    <div className="flex items-center gap-2 mb-2">
      {icon}
      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-tighter">{label}</span>
    </div>
    <div className="text-lg font-black text-white">{value}</div>
    <div className="w-full bg-white/5 h-1.5 rounded-full mt-2 overflow-hidden">
      <div className={`${barColor} h-full transition-all duration-1000 ease-out`} style={{ width: `${percent}%` }} />
    </div>
  </div>
);