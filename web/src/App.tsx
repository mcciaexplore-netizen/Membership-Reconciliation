import { useState } from 'react';
import axios from 'axios';
import { UploadCloud, Building, AlertTriangle, RefreshCcw, Download } from 'lucide-react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

function App() {
  const [bankFile, setBankFile] = useState<File | null>(null);
  const [backendFile, setBackendFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('matched');

  const handleRun = async () => {
    if (!bankFile || !backendFile) {
      setError("Please upload both files.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append('bank_file', bankFile);
      formData.append('backend_file', backendFile);

      // In production, this will hit /api/reconcile due to Vercel rewrites.
      // During dev, Vite proxy must be configured.
      const res = await axios.post('/api/reconcile', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResult(res.data);
    } catch (err: any) {
      console.error(err);
      if (err.response) {
        setError(`Server Error (${err.response.status}): ${err.response.data?.detail || typeof err.response.data === 'string' ? err.response.data.substring(0, 100) : "Unknown error"}`);
      } else if (err.request) {
        setError("Network error: Could not reach the server.");
      } else {
        setError(`Error: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!result || !result.excel_base64) return;
    const link = document.createElement('a');
    link.href = `data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,${result.excel_base64}`;
    link.download = "reconciliation_report.xlsx";
    link.click();
  };

  return (
    <div className="flex h-screen w-full bg-slate-50 overflow-hidden text-slate-900 font-sans">
      {/* Sidebar */}
      <div className="w-80 bg-slate-900 text-slate-100 flex flex-col p-6 flex-shrink-0">
        <div className="flex items-center gap-3 mb-2">
          <Building className="w-6 h-6 text-blue-400" />
          <h1 className="text-xl font-bold tracking-tight">MCCIA</h1>
        </div>
        <p className="text-slate-400 text-sm font-medium mb-8">Membership Reconciliation</p>

        <div className="flex items-center gap-2 text-xs font-bold text-slate-400 tracking-wider mb-4">
          <UploadCloud className="w-4 h-4 text-amber-400" />
          UPLOAD FILES
        </div>

        {/* Bank File Upload */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-slate-300 mb-2">Bank Statement (CSV / Excel)</label>
          <div className="border border-dashed border-slate-600 rounded-xl bg-slate-800 p-6 flex flex-col items-center justify-center transition-colors hover:border-blue-500 hover:bg-slate-750 relative overflow-hidden group">
            <input type="file" className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" onChange={(e) => setBankFile(e.target.files?.[0] || null)} />
            <span className="text-white font-semibold text-[15px] mb-2 flex items-center gap-2">
              <UploadCloud className="w-5 h-5" /> Upload
            </span>
            <span className="text-slate-400 text-[11px] text-center">
              {bankFile ? <span className="text-emerald-400 font-semibold">{bankFile.name}</span> : "Limit 200MB per file"}
            </span>
          </div>
        </div>

        {/* Backend File Upload */}
        <div className="mb-8">
          <label className="block text-sm font-medium text-slate-300 mb-2">Backend Membership Data (CSV / Excel)</label>
          <div className="border border-dashed border-slate-600 rounded-xl bg-slate-800 p-6 flex flex-col items-center justify-center transition-colors hover:border-blue-500 hover:bg-slate-750 relative overflow-hidden group">
            <input type="file" className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" onChange={(e) => setBackendFile(e.target.files?.[0] || null)} />
            <span className="text-white font-semibold text-[15px] mb-2 flex items-center gap-2">
              <UploadCloud className="w-5 h-5" /> Upload
            </span>
            <span className="text-slate-400 text-[11px] text-center">
              {backendFile ? <span className="text-emerald-400 font-semibold">{backendFile.name}</span> : "Limit 200MB per file"}
            </span>
          </div>
        </div>

        <button 
          onClick={handleRun}
          disabled={loading}
          className="w-full py-3 px-6 rounded-lg font-semibold text-white bg-gradient-to-r from-blue-500 to-blue-600 hover:translate-y-[-1px] hover:shadow-lg transition-all disabled:opacity-70 flex justify-center items-center gap-2"
        >
          {loading ? <RefreshCcw className="w-5 h-5 animate-spin" /> : null}
          {loading ? "Reconciling..." : "Run Reconciliation"}
        </button>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-8">
        <h2 className="text-3xl font-bold mb-2">Membership Reconciliation</h2>
        <p className="text-slate-500 mb-8 max-w-2xl">Compare bank collections against backend membership invoices. Identify matched, unmatched, and discrepant records.</p>
        
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-8 flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-bold">Error</p>
              <p className="text-sm">{error}</p>
            </div>
          </div>
        )}

        {!result && !loading && !error && (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="text-6xl mb-6">📁</div>
            <h3 className="text-xl font-bold mb-3 text-slate-800">Ready to Reconcile</h3>
            <p className="text-slate-500 text-center max-w-sm">Upload your <b>Bank Statement</b> and <b>Backend Membership Data</b> in the sidebar, then click <b>Run Reconciliation</b> to see the magic happen.</p>
          </div>
        )}

        {result && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* KPI Cards Grid */}
            <div className="grid grid-cols-4 gap-4 mb-8">
              <KpiCard icon="💰" title="TOTAL INVOICED (₹)" value={result.summary.total_backend_amount} color="border-blue-500" />
              <KpiCard icon="💳" title="TOTAL COLLECTED (₹)" value={result.summary.total_bank_amount} color="border-emerald-500" />
              <KpiCard icon="⚖️" title="VARIANCE (₹)" value={result.summary.variance} color={result.summary.variance < 0 ? 'border-red-500' : 'border-emerald-500'} />
              <KpiCard icon="🎯" title="MATCH RATE %" value={`${(result.summary.total_bank_amount > 0 ? (result.summary.matched_amount / result.summary.total_bank_amount) * 100 : 0).toFixed(1)}%`} color="border-amber-500" />
              
              <KpiCard icon="✅" title="MATCHED RECORDS" value={result.summary.matched_count} color="border-emerald-500" />
              <KpiCard icon="🏦" title="UNMATCHED BANK" value={result.summary.unmatched_bank_count} color="border-red-500" />
              <KpiCard icon="📋" title="UNMATCHED BACKEND" value={result.summary.unmatched_backend_count} color="border-amber-500" />
              <KpiCard icon="⚠️" title="PARTIAL / DISCREPANT" value={result.summary.partial_count} color="border-amber-400" />
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-2 gap-6 mb-8 h-[360px]">
              <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex flex-col">
                <h3 className="font-bold text-slate-800 mb-6 flex items-center gap-2"><span className="text-xl">🎯</span> Match Status Distribution</h3>
                <div className="flex-1 min-h-0 relative">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={[
                          { name: 'Matched', value: result.summary.matched_count, color: '#10b981' },
                          { name: 'Unmatched Bank', value: result.summary.unmatched_bank_count, color: '#ef4444' },
                          { name: 'Unmatched Backend', value: result.summary.unmatched_backend_count, color: '#f59e0b' },
                          { name: 'Partial', value: result.summary.partial_count, color: '#eab308' }
                        ].filter(d => d.value > 0)}
                        cx="50%" cy="50%" innerRadius={80} outerRadius={110} paddingAngle={2} dataKey="value"
                      >
                        {
                          [
                            { name: 'Matched', value: result.summary.matched_records, color: '#10b981' },
                            { name: 'Unmatched Bank', value: result.summary.unmatched_bank, color: '#ef4444' },
                            { name: 'Unmatched Backend', value: result.summary.unmatched_backend, color: '#f59e0b' },
                            { name: 'Partial', value: result.summary.partial_discrepant, color: '#eab308' }
                          ].filter(d => d.value > 0).map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))
                        }
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                    <span className="text-4xl font-bold text-slate-800">{result.summary.total_records_processed}</span>
                    <span className="text-xs font-semibold text-slate-500 uppercase tracking-widest mt-1">Total Records</span>
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex flex-col">
                <h3 className="font-bold text-slate-800 mb-6 flex items-center gap-2"><span className="text-xl">📈</span> Match Quality Breakdown</h3>
                <div className="flex-1 min-h-0">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart layout="vertical" data={getReasonData(result.data.matched)} margin={{ top: 0, right: 30, left: 30, bottom: 0 }}>
                      <XAxis type="number" hide />
                      <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{fill: '#475569', fontSize: 12, fontWeight: 500}} width={120} />
                      <Tooltip cursor={{fill: '#f8fafc'}} />
                      <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={24}>
                        {
                          getReasonData(result.data.matched).map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))
                        }
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            <div className="flex justify-between items-center mb-6 pt-6 border-t border-slate-200">
              <button onClick={handleDownload} className="px-6 py-2.5 bg-white border border-slate-200 shadow-sm rounded-lg font-semibold text-slate-700 hover:bg-slate-50 flex items-center gap-2 transition-colors">
                <Download className="w-4 h-4" /> Download Excel Report
              </button>
            </div>

            {/* Data Tables */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
              <div className="flex border-b border-slate-100 bg-slate-50 px-2 pt-2">
                <TabButton active={activeTab==='matched'} onClick={() => setActiveTab('matched')} icon="🟢" label="Matched" count={result.data.matched.length} />
                <TabButton active={activeTab==='unmatched_bank'} onClick={() => setActiveTab('unmatched_bank')} icon="🔴" label="Unmatched Bank" count={result.data.unmatched_bank.length} />
                <TabButton active={activeTab==='unmatched_backend'} onClick={() => setActiveTab('unmatched_backend')} icon="🟠" label="Unmatched Backend" count={result.data.unmatched_backend.length} />
                <TabButton active={activeTab==='partial'} onClick={() => setActiveTab('partial')} icon="🟡" label="Partial" count={result.data.partial.length} />
              </div>
              <div className="p-0">
                <div className="overflow-x-auto max-h-[500px]">
                  <table className="w-full text-sm text-left">
                    <thead className="text-xs text-slate-500 uppercase bg-slate-50 sticky top-0 z-10">
                      <tr>
                        {Object.keys(result.data[activeTab][0] || {}).map(key => (
                          <th key={key} className="px-6 py-4 font-semibold whitespace-nowrap">{key.replace(/_/g, ' ')}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {result.data[activeTab].map((row: any, i: number) => (
                        <tr key={i} className="border-b border-slate-100 hover:bg-slate-50/50">
                          {Object.values(row).map((val: any, j: number) => (
                            <td key={j} className="px-6 py-3 whitespace-nowrap text-slate-700">{val?.toString() || '-'}</td>
                          ))}
                        </tr>
                      ))}
                      {result.data[activeTab].length === 0 && (
                        <tr><td colSpan={10} className="px-6 py-12 text-center text-slate-400">No records found.</td></tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

          </div>
        )}
      </div>
    </div>
  );
}

function KpiCard({ icon, title, value, color }: { icon: string, title: string, value: string|number, color: string }) {
  return (
    <div className={`bg-white rounded-xl shadow-sm border-l-4 ${color} border-y border-r border-slate-100 p-5 flex flex-col justify-center`}>
      <div className="flex items-center gap-3 mb-2">
        <div className="text-xl">{icon}</div>
        <p className="text-[11px] font-bold text-slate-500 uppercase tracking-widest">{title}</p>
      </div>
      <p className="text-3xl font-extrabold text-slate-900 tracking-tight ml-8">{typeof value === 'number' && title.includes('TOTAL') ? value.toLocaleString() : value}</p>
    </div>
  );
}

function TabButton({ active, onClick, icon, label, count }: any) {
  return (
    <button 
      onClick={onClick}
      className={`px-5 py-3 text-sm font-semibold rounded-t-lg transition-colors flex items-center gap-2 mr-1 ${active ? 'bg-white text-slate-900 border-x border-t border-slate-100 -mb-[1px]' : 'text-slate-500 hover:bg-slate-100 hover:text-slate-700'}`}
    >
      <span>{icon}</span> {label} <span className={`ml-1 px-2 py-0.5 rounded-full text-xs ${active ? 'bg-slate-100 text-slate-700' : 'bg-slate-200/50 text-slate-500'}`}>{count}</span>
    </button>
  );
}

// Helper to calculate reason data for bar chart
function getReasonData(matched: any[]) {
  const counts: Record<string, number> = {};
  matched.forEach(m => {
    const r = m.reason_code || 'Unknown';
    counts[r] = (counts[r] || 0) + 1;
  });
  
  const labels: Record<string, {name: string, color: string}> = {
    "MATCHED_EXACT_REF": { name: "Exact Reference", color: "#10b981" }, // emerald
    "MATCHED_AMOUNT_DATE": { name: "Amount + Date", color: "#3b82f6" }, // blue
    "MATCHED_FUZZY_REF": { name: "Fuzzy Reference", color: "#8b5cf6" }, // violet
    "MATCHED_DATE_WINDOW": { name: "Date Window", color: "#eab308" }, // yellow
    "MATCHED_OFFLINE_WINDOW": { name: "Offline Window", color: "#ec4899" }, // pink
    "MATCHED_NAME_FUZZY": { name: "Name Fuzzy", color: "#14b8a6" } // teal
  };

  return Object.entries(counts)
    .map(([key, value]) => ({
      name: labels[key]?.name || key,
      value,
      color: labels[key]?.color || '#94a3b8'
    }))
    .sort((a, b) => a.value - b.value); // Sort ascending so largest is on top in horizontal bar
}

export default App;
