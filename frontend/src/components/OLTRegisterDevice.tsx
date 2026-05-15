import React, { useEffect, useState, useMemo } from 'react';
import { Plus, ArrowLeft, Shield, Globe, Cpu, Lock, X, ChevronRight } from 'lucide-react';
import { useOLTAPI } from '../hooks/useOLTAPI';

interface Props {
  onSuccess: () => void;
}

export const OLTRegisterDevice: React.FC<Props> = ({ onSuccess }) => {
  const { registerDevice, getSupportedModels, loading, error } = useOLTAPI();
  const [modelsData, setModelsData] = useState<Record<string, any>>({});
  const [selectedVendor, setSelectedVendor] = useState('');
  const [formData, setFormData] = useState({
    model: '',
    vendor: '',
    ip_address: '',
    snmp_port: 161,
    ssh_port: 22,
    snmp_community: 'public',
    username: '',
    password: '',
    connection_method: 'SNMP'
  });
  const [showForm, setShowForm] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    const data = await getSupportedModels();
    setModelsData(data);
  };

  // ইউনিক ভেন্ডর লিস্ট বের করা
  const vendors = useMemo(() => {
    const vSet = new Set<string>();
    Object.values(modelsData).forEach((m: any) => vSet.add(m.vendor));
    return Array.from(vSet);
  }, [modelsData]);

  // সিলেক্টেড ভেন্ডরের মডেল ফিল্টার করা
  const filteredModels = useMemo(() => {
    return Object.keys(modelsData).filter(
      (mKey) => modelsData[mKey].vendor === selectedVendor
    );
  }, [selectedVendor, modelsData]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name.includes('port') ? parseInt(value) || 0 : value
    }));
  };

  const handleVendorChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const vendor = e.target.value;
    setSelectedVendor(vendor);
    setFormData(prev => ({ ...prev, vendor: vendor, model: '' })); // ভেন্ডর বদলালে মডেল রিসেট
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError(null);
    const result = await registerDevice(formData);
    if (result) {
      setShowForm(false);
      resetForm();
      onSuccess();
    } else {
      setSubmitError(error || 'Failed to register device');
    }
  };

  const resetForm = () => {
    setFormData({
      model: '', vendor: '', ip_address: '', snmp_port: 161, ssh_port: 22,
      snmp_community: 'public', username: '', password: '', connection_method: 'SNMP'
    });
    setSelectedVendor('');
  };

  if (!showForm) {
    return (
      <button
        onClick={() => setShowForm(true)}
        className="group relative flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-5 py-2.5 rounded-xl font-bold transition-all shadow-lg shadow-blue-600/20 active:scale-95"
      >
        <Plus className="w-5 h-5 group-hover:rotate-90 transition-transform" />
        <span>Register New OLT</span>
      </button>
    );
  }

  return (
    <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-md flex items-center justify-center z-[100] p-4">
      <div className="bg-[#0f172a] border border-white/10 rounded-[2.5rem] max-w-2xl w-full max-h-[95vh] overflow-hidden shadow-[0_0_50px_rgba(0,0,0,0.5)]">
        
        {/* Header */}
        <div className="px-8 py-6 bg-gradient-to-r from-blue-600/10 to-transparent border-b border-white/5 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-600 rounded-2xl shadow-lg shadow-blue-600/20">
              <Cpu className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-black text-white tracking-tight">Provision OLT Node</h2>
              <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Hardware Configuration</p>
            </div>
          </div>
          <button onClick={() => setShowForm(false)} className="p-2 hover:bg-white/5 text-slate-400 rounded-full transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-8 space-y-6 overflow-y-auto max-h-[calc(95vh-100px)] custom-scrollbar">
          {submitError && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-4 text-red-400 text-sm flex items-center gap-3">
              <Shield className="w-5 h-5" /> {submitError}
            </div>
          )}

          {/* Vendor & Model Row */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-500 uppercase ml-1">Hardware Vendor</label>
              <select
                value={selectedVendor}
                onChange={handleVendorChange}
                required
                className="w-full bg-slate-800/50 border border-white/10 rounded-2xl px-4 py-3.5 text-white focus:ring-2 focus:ring-blue-500 outline-none transition-all"
              >
                <option value="">Select Vendor...</option>
                {vendors.map(v => <option key={v} value={v}>{v}</option>)}
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-500 uppercase ml-1">Device Model</label>
              <select
                name="model"
                value={formData.model}
                onChange={handleChange}
                required
                disabled={!selectedVendor}
                className="w-full bg-slate-800/50 border border-white/10 rounded-2xl px-4 py-3.5 text-white focus:ring-2 focus:ring-blue-500 outline-none transition-all disabled:opacity-30 disabled:cursor-not-allowed"
              >
                <option value="">Select Model...</option>
                {filteredModels.map(m => <option key={m} value={m}>{m}</option>)}
              </select>
            </div>
          </div>

          {/* IP Address */}
          <div className="space-y-2">
            <label className="text-xs font-bold text-slate-500 uppercase ml-1 flex items-center gap-2">
              <Globe className="w-3 h-3" /> Management IP Address
            </label>
            <input
              type="text"
              name="ip_address"
              value={formData.ip_address}
              onChange={handleChange}
              placeholder="e.g. 10.10.20.50"
              required
              className="w-full bg-slate-800/50 border border-white/10 rounded-2xl px-4 py-3.5 text-white focus:ring-2 focus:ring-blue-500 outline-none transition-all font-mono"
            />
          </div>

          {/* Ports & Community Row */}
          <div className="grid grid-cols-3 gap-4">
            <InputField label="SNMP Port" name="snmp_port" value={formData.snmp_port} type="number" onChange={handleChange} />
            <InputField label="SSH Port" name="ssh_port" value={formData.ssh_port} type="number" onChange={handleChange} />
            <div className="space-y-2">
              <label className="text-[10px] font-bold text-slate-500 uppercase ml-1">Auth Method</label>
              <select name="connection_method" value={formData.connection_method} onChange={handleChange} className="w-full bg-slate-800/50 border border-white/10 rounded-2xl px-3 py-3 text-sm text-white outline-none">
                <option value="SNMP">SNMP</option>
                <option value="SSH">SSH</option>
              </select>
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-bold text-slate-500 uppercase ml-1">SNMP Read Community</label>
            <input
              type="text"
              name="snmp_community"
              value={formData.snmp_community}
              onChange={handleChange}
              className="w-full bg-slate-800/50 border border-white/10 rounded-2xl px-4 py-3.5 text-white focus:ring-2 focus:ring-blue-500 outline-none transition-all"
            />
          </div>

          {/* Credentials */}
          <div className="bg-blue-600/5 p-6 rounded-[2rem] border border-blue-600/10 space-y-4">
            <div className="flex items-center gap-2 mb-2">
              <Lock className="w-4 h-4 text-blue-500" />
              <span className="text-xs font-black text-blue-500 uppercase tracking-widest">Access Credentials</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InputField label="Admin Username" name="username" value={formData.username} onChange={handleChange} />
              <InputField label="Password" name="password" value={formData.password} type="password" onChange={handleChange} />
            </div>
          </div>

          {/* Actions */}
          <div className="flex flex-col sm:flex-row gap-4 pt-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-[2] bg-blue-600 hover:bg-blue-500 text-white px-8 py-4 rounded-[1.5rem] font-black uppercase tracking-widest disabled:opacity-50 transition-all flex items-center justify-center gap-3 shadow-xl shadow-blue-600/20"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>Deploy Device <ChevronRight className="w-5 h-5" /></>
              )}
            </button>
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-300 px-6 py-4 rounded-[1.5rem] font-bold transition-all"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};


const InputField = ({ label, name, value, type = "text", onChange }: any) => (
  <div className="space-y-2">
    <label className="text-[10px] font-bold text-slate-500 uppercase ml-1 tracking-wider">{label}</label>
    <input
      type={type}
      name={name}
      value={value}
      onChange={onChange}
      className="w-full bg-slate-800/50 border border-white/10 rounded-2xl px-4 py-3 text-white focus:ring-2 focus:ring-blue-500 outline-none transition-all text-sm"
    />
  </div>
);