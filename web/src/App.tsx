import { useEffect, useRef, useState, type RefObject } from 'react';
import axios from 'axios';
import {
  UploadCloud,
  AlertTriangle,
  RefreshCcw,
  Download,
  IndianRupee,
  CreditCard,
  Scale,
  Target,
  CheckCircle2,
  Landmark,
  ClipboardList,
  TrendingUp,
  FolderOpen,
  Circle,
} from 'lucide-react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const PRIMARY = '#003F8A';
const GREEN = '#10B981';
const DANGER = '#EF4444';
const AMBER = '#F59E0B';
const PURPLE = '#8B5CF6';
const YELLOW = '#EAB308';
const TEAL = '#14B8A6';
const PINK = '#EC4899';
const SLATE = '#94A3B8';

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
        const data = err.response.data;
        const msg = data?.detail || data?.message || (typeof data === 'string' ? data.substring(0, 100) : JSON.stringify(data));
        setError(`Server Error (${err.response.status}): ${msg}`);
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
    <div className="flex h-screen w-full overflow-hidden text-[#0F172A] font-sans">
      {/* Sidebar */}
      <div className="w-80 bg-white/90 backdrop-blur-xl border-r border-slate-200/70 flex flex-col p-6 flex-shrink-0 shadow-[var(--shadow-card)]">
        <div className="mb-4">
          <img src="/mccia-logo.png" alt="MCCIA" className="h-11 w-auto object-contain" />
          <h1 className="font-heading text-xl font-extrabold tracking-tight text-[#003F8A] sr-only">MCCIA</h1>
        </div>
        <p className="text-[#64748B] text-sm font-medium mb-8">
          Membership Reconciliation{' '}
          <span className="text-[0.68rem] font-bold uppercase tracking-wider ml-1 bg-[rgba(0,63,138,0.06)] text-[#003F8A] border border-[rgba(0,63,138,0.14)] px-2 py-0.5 rounded-full">v2</span>
        </p>

        <div className="flex items-center gap-2 text-[0.7rem] font-bold text-[#64748B] uppercase tracking-[0.1em] mb-4">
          <UploadCloud className="w-4 h-4 text-[#003F8A]" />
          Upload Files
        </div>

        {/* Bank File Upload */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-[#475569] mb-2">Bank Statement (CSV / Excel)</label>
          <div className="border border-dashed border-slate-300 rounded-xl bg-white/70 p-6 flex flex-col items-center justify-center transition-colors duration-300 ease-[var(--ease-standard)] hover:border-[rgba(0,63,138,0.4)] hover:bg-[rgba(0,63,138,0.03)] relative overflow-hidden group">
            <input type="file" accept=".csv, .xls, .xlsx, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel" className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" onChange={(e) => setBankFile(e.target.files?.[0] || null)} />
            <span className="text-[#0F172A] font-semibold text-[15px] mb-2 flex items-center gap-2">
              <UploadCloud className="w-5 h-5 text-[#003F8A]" /> Upload
            </span>
            <span className="text-[#64748B] text-[11px] text-center">
              {bankFile ? <span className="text-[#059669] font-semibold">{bankFile.name}</span> : "Limit 200MB per file"}
            </span>
          </div>
        </div>

        {/* Backend File Upload */}
        <div className="mb-8">
          <label className="block text-sm font-medium text-[#475569] mb-2">Backend Membership Data (CSV / Excel)</label>
          <div className="border border-dashed border-slate-300 rounded-xl bg-white/70 p-6 flex flex-col items-center justify-center transition-colors duration-300 ease-[var(--ease-standard)] hover:border-[rgba(0,63,138,0.4)] hover:bg-[rgba(0,63,138,0.03)] relative overflow-hidden group">
            <input type="file" accept=".csv, .xls, .xlsx, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel" className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" onChange={(e) => setBackendFile(e.target.files?.[0] || null)} />
            <span className="text-[#0F172A] font-semibold text-[15px] mb-2 flex items-center gap-2">
              <UploadCloud className="w-5 h-5 text-[#003F8A]" /> Upload
            </span>
            <span className="text-[#64748B] text-[11px] text-center">
              {backendFile ? <span className="text-[#059669] font-semibold">{backendFile.name}</span> : "Limit 200MB per file"}
            </span>
          </div>
        </div>

        <button
          onClick={handleRun}
          disabled={loading}
          className="w-full py-3 px-6 rounded-[10px] font-semibold text-white bg-[linear-gradient(135deg,#003F8A_0%,#0056B3_100%)] shadow-[var(--shadow-btn)] hover:-translate-y-0.5 hover:shadow-[var(--shadow-btn-hover)] transition-all duration-300 ease-[var(--ease-standard)] disabled:opacity-70 disabled:translate-y-0 flex justify-center items-center gap-2"
        >
          {loading ? <RefreshCcw className="w-5 h-5 animate-spin" /> : null}
          {loading ? "Reconciling..." : "Run Reconciliation"}
        </button>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-8">
        <h2 className="font-heading text-3xl font-extrabold tracking-tight mb-2">Membership Reconciliation</h2>
        <p className="text-[#475569] mb-8 max-w-2xl leading-relaxed">Compare bank collections against backend membership invoices. Identify matched, unmatched, and discrepant records.</p>

        {error && (
          <div className="bg-[rgba(239,68,68,0.06)] border border-[rgba(239,68,68,0.15)] text-[#EF4444] px-4 py-3 rounded-xl mb-8 flex items-start gap-3 animate-fade-in-up">
            <AlertTriangle className="w-5 h-5 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-bold">Error</p>
              <p className="text-sm">{error}</p>
            </div>
          </div>
        )}

        {!result && !loading && !error && (
          <div className="flex flex-col items-center justify-center py-20 animate-fade-in-up">
            <IconTile color="blue" size={64}>
              <FolderOpen className="w-7 h-7" />
            </IconTile>
            <h3 className="font-heading text-xl font-bold mb-3 mt-6 text-[#0F172A]">Ready to Reconcile</h3>
            <p className="text-[#64748B] text-center max-w-sm leading-relaxed">Upload your <b>Bank Statement</b> and <b>Backend Membership Data</b> in the sidebar, then click <b>Run Reconciliation</b> to see the magic happen.</p>
          </div>
        )}

        {result && (
          <div className="animate-fade-in-up">
            {/* KPI Cards Grid */}
            <div className="grid grid-cols-4 gap-4 mb-8">
              <KpiCard icon={<IndianRupee className="w-[18px] h-[18px]" />} title="TOTAL INVOICED (₹)" value={result.summary.total_backend_amount} tint="blue" delay={0} />
              <KpiCard icon={<CreditCard className="w-[18px] h-[18px]" />} title="TOTAL COLLECTED (₹)" value={result.summary.total_bank_amount} tint="green" delay={80} />
              <KpiCard icon={<Scale className="w-[18px] h-[18px]" />} title="VARIANCE (₹)" value={result.summary.variance} tint={result.summary.variance < 0 ? 'red' : 'green'} delay={160} />
              <KpiCard icon={<Target className="w-[18px] h-[18px]" />} title="MATCH RATE %" value={`${(result.summary.total_bank_amount > 0 ? (result.summary.matched_amount / result.summary.total_bank_amount) * 100 : 0).toFixed(1)}%`} tint="amber" delay={240} />

              <KpiCard icon={<CheckCircle2 className="w-[18px] h-[18px]" />} title="MATCHED RECORDS" value={result.summary.matched_count} tint="green" delay={320} />
              <KpiCard icon={<Landmark className="w-[18px] h-[18px]" />} title="UNMATCHED BANK" value={result.summary.unmatched_bank_count} tint="red" delay={400} />
              <KpiCard icon={<ClipboardList className="w-[18px] h-[18px]" />} title="UNMATCHED BACKEND" value={result.summary.unmatched_backend_count} tint="amber" delay={480} />
              <KpiCard icon={<AlertTriangle className="w-[18px] h-[18px]" />} title="PARTIAL / DISCREPANT" value={result.summary.partial_count} tint="amber" delay={560} />
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-2 gap-6 mb-8 h-[360px]">
              <div className="bg-white/70 backdrop-blur-md p-6 rounded-[20px] shadow-[var(--shadow-card)] border border-slate-200/70 flex flex-col transition-shadow duration-300 ease-[var(--ease-standard)] hover:shadow-[var(--shadow-card-hover)]">
                <h3 className="font-heading font-bold text-[#0F172A] mb-6 flex items-center gap-2">
                  <Target className="w-5 h-5 text-[#003F8A]" /> Match Status Distribution
                </h3>
                <div className="flex-1 min-h-0 relative">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={[
                          { name: 'Matched', value: result.summary.matched_count, color: GREEN },
                          { name: 'Unmatched Bank', value: result.summary.unmatched_bank_count, color: DANGER },
                          { name: 'Unmatched Backend', value: result.summary.unmatched_backend_count, color: AMBER },
                          { name: 'Partial', value: result.summary.partial_count, color: YELLOW }
                        ].filter(d => d.value > 0)}
                        cx="50%" cy="50%" innerRadius={80} outerRadius={110} paddingAngle={2} dataKey="value"
                      >
                        {
                          [
                            { name: 'Matched', value: result.summary.matched_count, color: GREEN },
                            { name: 'Unmatched Bank', value: result.summary.unmatched_bank_count, color: DANGER },
                            { name: 'Unmatched Backend', value: result.summary.unmatched_backend_count, color: AMBER },
                            { name: 'Partial', value: result.summary.partial_count, color: YELLOW }
                          ].filter(d => d.value > 0).map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))
                        }
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                    <span className="font-heading text-4xl font-extrabold text-[#0F172A]">{result.summary.total_records_processed}</span>
                    <span className="text-[0.7rem] font-bold text-[#64748B] uppercase tracking-[0.1em] mt-1">Total Records</span>
                  </div>
                </div>
              </div>

              <div className="bg-white/70 backdrop-blur-md p-6 rounded-[20px] shadow-[var(--shadow-card)] border border-slate-200/70 flex flex-col transition-shadow duration-300 ease-[var(--ease-standard)] hover:shadow-[var(--shadow-card-hover)]">
                <h3 className="font-heading font-bold text-[#0F172A] mb-6 flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-[#003F8A]" /> Match Quality Breakdown
                </h3>
                <div className="flex-1 min-h-0">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart layout="vertical" data={getReasonData(result.data.matched)} margin={{ top: 0, right: 30, left: 30, bottom: 0 }}>
                      <XAxis type="number" hide />
                      <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{fill: '#475569', fontSize: 12, fontWeight: 500}} width={120} />
                      <Tooltip cursor={{fill: '#F8FAFC'}} />
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
              <button onClick={handleDownload} className="px-6 py-2.5 bg-white/60 backdrop-blur-sm border border-slate-200 shadow-[var(--shadow-card)] rounded-[10px] font-semibold text-[#475569] hover:border-[#003F8A] hover:text-[#003F8A] hover:-translate-y-0.5 flex items-center gap-2 transition-all duration-300 ease-[var(--ease-standard)]">
                <Download className="w-4 h-4" /> Download Excel Report
              </button>
            </div>

            {/* Data Tables */}
            <div className="bg-white/80 backdrop-blur-md rounded-[20px] shadow-[var(--shadow-card)] border border-slate-200/70 overflow-hidden">
              <div className="flex border-b border-slate-200/70 bg-[#F8FAFC] px-2 pt-2">
                <TabButton active={activeTab==='matched'} onClick={() => setActiveTab('matched')} dotColor={GREEN} label="Matched" count={result.data.matched.length} />
                <TabButton active={activeTab==='unmatched_bank'} onClick={() => setActiveTab('unmatched_bank')} dotColor={DANGER} label="Unmatched Bank" count={result.data.unmatched_bank.length} />
                <TabButton active={activeTab==='unmatched_backend'} onClick={() => setActiveTab('unmatched_backend')} dotColor={AMBER} label="Unmatched Backend" count={result.data.unmatched_backend.length} />
                <TabButton active={activeTab==='partial'} onClick={() => setActiveTab('partial')} dotColor={YELLOW} label="Partial" count={result.data.partial.length} />
              </div>
              <div className="p-0">
                <div className="overflow-x-auto max-h-[500px]">
                  <table className="w-full text-sm text-left">
                    <thead className="text-[0.7rem] text-[#64748B] uppercase tracking-wider bg-[#F8FAFC] sticky top-0 z-10">
                      <tr>
                        {Object.keys(result.data[activeTab][0] || {}).map(key => (
                          <th key={key} className="px-6 py-4 font-bold whitespace-nowrap">{key.replace(/_/g, ' ')}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {result.data[activeTab].map((row: any, i: number) => (
                        <tr key={i} className="border-b border-slate-100 hover:bg-[rgba(0,63,138,0.02)] transition-colors duration-200">
                          {Object.values(row).map((val: any, j: number) => (
                            <td key={j} className="px-6 py-3 whitespace-nowrap text-[#0F172A]">{val?.toString() || '-'}</td>
                          ))}
                        </tr>
                      ))}
                      {result.data[activeTab].length === 0 && (
                        <tr><td colSpan={10} className="px-6 py-12 text-center text-[#94A3B8]">No records found.</td></tr>
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

type Tint = 'blue' | 'green' | 'red' | 'amber';

const TINT_STYLES: Record<Tint, { bg: string; border: string; text: string; accent: string }> = {
  blue: { bg: 'rgba(0,63,138,0.06)', border: 'rgba(0,63,138,0.14)', text: '#003F8A', accent: '#003F8A' },
  green: { bg: 'rgba(16,185,129,0.07)', border: 'rgba(16,185,129,0.14)', text: '#059669', accent: GREEN },
  red: { bg: 'rgba(239,68,68,0.06)', border: 'rgba(239,68,68,0.14)', text: '#EF4444', accent: DANGER },
  amber: { bg: 'rgba(245,158,11,0.07)', border: 'rgba(245,158,11,0.16)', text: '#B45309', accent: AMBER },
};

function IconTile({ color, children, size = 44 }: { color: Tint; children: React.ReactNode; size?: number }) {
  const s = TINT_STYLES[color];
  return (
    <div
      className="flex items-center justify-center rounded-[10px] border flex-shrink-0 transition-transform duration-300 ease-[var(--ease-standard)] hover:scale-110 hover:rotate-[5deg]"
      style={{ width: size, height: size, backgroundColor: s.bg, borderColor: s.border, color: s.text }}
    >
      {children}
    </div>
  );
}

function useCountUp(end: number, ref: RefObject<HTMLElement | null>) {
  const [value, setValue] = useState(0);
  const hasRun = useRef(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) {
      setValue(end);
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !hasRun.current) {
            hasRun.current = true;
            const duration = 1800;
            const start = performance.now();
            const step = (now: number) => {
              const elapsed = now - start;
              const progress = Math.min(elapsed / duration, 1);
              const eased = 1 - Math.pow(1 - progress, 3);
              setValue(end * eased);
              if (progress < 1) {
                requestAnimationFrame(step);
              } else {
                setValue(end);
              }
            };
            requestAnimationFrame(step);
            observer.disconnect();
          }
        });
      },
      { threshold: 0.1 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [end, ref]);

  return value;
}

function KpiCard({ icon, title, value, tint, delay }: { icon: React.ReactNode, title: string, value: string | number, tint: Tint, delay: number }) {
  const ref = useRef<HTMLDivElement | null>(null);
  const isNumeric = typeof value === 'number';
  const animated = useCountUp(isNumeric ? value : 0, ref);

  const displayValue = isNumeric ? Math.round(animated).toLocaleString('en-IN') : value;

  return (
    <div
      ref={ref}
      className="bg-white/70 backdrop-blur-md rounded-xl shadow-[var(--shadow-card)] border border-slate-200/70 p-5 flex flex-col justify-center transition-all duration-300 ease-[var(--ease-standard)] hover:-translate-y-1 hover:bg-white/95 hover:border-[rgba(0,63,138,0.2)] hover:shadow-[var(--shadow-card-hover)] animate-fade-in-up"
      style={{ borderLeft: `4px solid ${TINT_STYLES[tint].accent}`, animationDelay: `${delay}ms` }}
    >
      <div className="flex items-center gap-3 mb-2">
        <IconTile color={tint} size={36}>{icon}</IconTile>
        <p className="text-[0.68rem] font-bold text-[#64748B] uppercase tracking-[0.1em]">{title}</p>
      </div>
      <p className="font-heading text-[2.2rem] font-extrabold tracking-tight ml-[52px]" style={{ color: tint === 'green' ? '#059669' : '#0F172A' }}>
        {displayValue}
      </p>
    </div>
  );
}

function TabButton({ active, onClick, dotColor, label, count }: { active: boolean, onClick: () => void, dotColor: string, label: string, count: number }) {
  return (
    <button
      onClick={onClick}
      className={`px-5 py-3 text-sm font-semibold rounded-t-lg transition-colors duration-300 ease-[var(--ease-standard)] flex items-center gap-2 mr-1 ${active ? 'bg-white text-[#0F172A] border-x border-t border-slate-200/70 -mb-[1px]' : 'text-[#64748B] hover:bg-white/60 hover:text-[#003F8A]'}`}
    >
      <Circle className="w-2 h-2" fill={dotColor} stroke="none" />
      {label}
      <span className={`ml-1 px-2 py-0.5 rounded-full text-xs font-bold ${active ? 'bg-[rgba(0,63,138,0.08)] text-[#003F8A]' : 'bg-slate-200/50 text-[#64748B]'}`}>{count}</span>
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
    "MATCHED_EXACT_REF": { name: "Exact Reference", color: GREEN },
    "MATCHED_AMOUNT_DATE": { name: "Amount + Date", color: PRIMARY },
    "MATCHED_FUZZY_REF": { name: "Fuzzy Reference", color: PURPLE },
    "MATCHED_DATE_WINDOW": { name: "Date Window", color: YELLOW },
    "MATCHED_OFFLINE_WINDOW": { name: "Offline Window", color: PINK },
    "MATCHED_NAME_FUZZY": { name: "Name Fuzzy", color: TEAL }
  };

  return Object.entries(counts)
    .map(([key, value]) => ({
      name: labels[key]?.name || key,
      value,
      color: labels[key]?.color || SLATE
    }))
    .sort((a, b) => a.value - b.value); // Sort ascending so largest is on top in horizontal bar
}

export default App;
