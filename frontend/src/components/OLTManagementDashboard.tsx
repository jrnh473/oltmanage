import React, { useState } from 'react';
import { Network, Plus, Settings, RefreshCcw, LayoutGrid, List } from 'lucide-react';
import { OLTDeviceList } from './OLTDeviceList';
import { OLTRegisterDevice } from './OLTRegisterDevice';

export const OLTManagementDashboard: React.FC = () => {
  const [selectedDeviceId, setSelectedDeviceId] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
    // এখানে আপনার API কল রিস্টার্ট করার লজিক থাকবে
  };

  return (
    <div className="min-h-screen bg-[#0f172a] text-slate-200">
      {/* Top Navigation */}
      <nav className="sticky top-0 z-50 border-b border-white/5 bg-[#0f172a]/80 backdrop-blur-md">
        <div className="max-w-[1600px] mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="p-2.5 bg-blue-600 rounded-xl shadow-lg shadow-blue-500/20">
              <Network className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
                OLT Nexus Core
              </h1>
              <p className="text-[10px] uppercase tracking-[0.2em] text-emerald-500 font-bold">System Online</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button 
              onClick={handleRefresh}
              className="p-2.5 hover:bg-white/5 rounded-xl border border-white/10 transition-all active:rotate-180 duration-500"
            >
              <RefreshCcw className="w-5 h-5 text-slate-400" />
            </button>
            <OLTRegisterDevice onSuccess={() => setRefreshKey(k => k + 1)} />
          </div>
        </div>
      </nav>

      <main className="max-w-[1600px] mx-auto p-6">
        {/* Dashboard Actions/Filters */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
          <div>
            <h2 className="text-2xl font-bold text-white">Device Inventory</h2>
            <p className="text-slate-500 text-sm font-medium">Manage and monitor your OLT infrastructure in real-time.</p>
          </div>
          <div className="flex bg-slate-900/50 p-1 rounded-xl border border-white/10">
            <button className="p-2 bg-blue-600 rounded-lg text-white shadow-lg"><LayoutGrid className="w-4 h-4" /></button>
            <button className="p-2 text-slate-500 hover:text-slate-300"><List className="w-4 h-4" /></button>
          </div>
        </div>

        {/* Device List Section */}
        <div className="bg-white/[0.02] border border-white/5 rounded-3xl min-h-[600px]">
           <OLTDeviceList key={refreshKey} />
        </div>
      </main>
    </div>
  );
};