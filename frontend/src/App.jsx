import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Search, Play, CheckCircle2, Image as ImageIcon, Clock, Loader2, Layers, Grid, List, Filter, Sliders, Monitor, Zap, Activity, Cpu } from 'lucide-react';

const API_BASE = "http://127.0.0.1:8000";

export default function App() {
  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState(50);
  const [results, setResults] = useState([]);
  const [groupByVideo, setGroupByVideo] = useState(false);
  const [videoFilter, setVideoFilter] = useState('');
  const [loading, setLoading] = useState(false);
  const [tookMs, setTookMs] = useState(0);
  
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [neighbors, setNeighbors] = useState([]);
  const [loadingNeighbors, setLoadingNeighbors] = useState(false);
  
  const [startTime, setStartTime] = useState(Date.now());
  const searchInputRef = useRef(null);

  const [searchMode, setSearchMode] = useState('visual'); // 'visual', 'qa', 'trake'
  const [apiAnswer, setApiAnswer] = useState('');
  const [trajectory, setTrajectory] = useState([]);

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setApiAnswer('');
    setTrajectory([]);
    try {
      let endpoint = `${API_BASE}/api/v1/search`;
      if (searchMode === 'qa') {
        endpoint = `${API_BASE}/api/v1/search/qa`;
      } else if (searchMode === 'trake') {
        endpoint = `${API_BASE}/api/v1/search/trake`;
      }

      const res = await axios.post(endpoint, {
        query: query,
        top_k: parseInt(topK)
      });
      const data = res.data.results || [];
      setResults(data);
      setTookMs(res.data.took_ms || 0);
      setStartTime(Date.now());
      
      if (res.data.answer) {
        setApiAnswer(res.data.answer);
      }
      if (res.data.trajectory) {
        setTrajectory(res.data.trajectory);
      }
      
      if (data.length > 0) {
        handleSelectCandidate(data[0], 0);
      } else {
        setSelectedCandidate(null);
        setSelectedIndex(-1);
        setNeighbors([]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectCandidate = async (candidate, index) => {
    setSelectedCandidate(candidate);
    setSelectedIndex(index);
    setLoadingNeighbors(true);
    try {
      const res = await axios.get(`${API_BASE}/api/v1/frame/neighbors`, {
        params: {
          video_id: candidate.video_id,
          frame_id: candidate.frame_id
        }
      });
      setNeighbors(res.data.neighbors || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingNeighbors(false);
    }
  };

  const handleSubmitDryRun = async () => {
    if (!selectedCandidate) return;
    const elapsedMs = Date.now() - startTime;
    try {
      const res = await axios.post(`${API_BASE}/api/v1/submit/dry-run`, {
        query_id: `Q_${new Date().toISOString().slice(11, 19).replace(/:/g, '')}`,
        video_id: selectedCandidate.video_id,
        frame_id: selectedCandidate.frame_id,
        answer: query,
        elapsed_ms: elapsedMs
      });
      alert(`🎉 SUBMITTED SUCCESS!\n🎬 Video: ${res.data.data.video_id}\n📸 Frame: ${res.data.data.frame_id}\n⏱️ Time: ${(elapsedMs/1000).toFixed(2)}s`);
    } catch (err) {
      alert("❌ Lỗi kết nối API Submit!");
    }
  };

  // --- PHÍM TẮT ĐIỀU HƯỚNG ---
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (document.activeElement === searchInputRef.current || document.activeElement.tagName === 'INPUT') {
        if (e.key === 'Escape') searchInputRef.current.blur();
        return;
      }
      if (e.key === '/') {
        e.preventDefault();
        searchInputRef.current.focus();
        searchInputRef.current.select();
        return;
      }
      if (results.length === 0) return;

      let nextIndex = selectedIndex;
      let cols = 4;

      switch (e.key) {
        case 'ArrowRight': e.preventDefault(); nextIndex = Math.min(results.length - 1, selectedIndex + 1); break;
        case 'ArrowLeft': e.preventDefault(); nextIndex = Math.max(0, selectedIndex - 1); break;
        case 'ArrowDown': e.preventDefault(); nextIndex = Math.min(results.length - 1, selectedIndex + cols); break;
        case 'ArrowUp': e.preventDefault(); nextIndex = Math.max(0, selectedIndex - cols); break;
        case 'Enter': e.preventDefault(); handleSubmitDryRun(); return;
        default: return;
      }

      if (nextIndex !== selectedIndex && results[nextIndex]) {
        handleSelectCandidate(results[nextIndex], nextIndex);
        const el = document.getElementById(`card-${nextIndex}`);
        if (el) el.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedIndex, results, selectedCandidate]);

  const filteredResults = results.filter(item => 
    item.video_id.toLowerCase().includes(videoFilter.toLowerCase())
  );

  const renderGroupedResults = () => {
    const groups = {};
    filteredResults.forEach((item, index) => {
      if (!groups[item.video_id]) groups[item.video_id] = [];
      groups[item.video_id].push({ ...item, originalIndex: index });
    });

    return Object.entries(groups).map(([videoTitle, frames]) => (
      <div key={videoTitle} className="mb-6 p-4 rounded-2xl border border-[rgba(255,255,255,0.05)] bg-slate-900/20 backdrop-blur-md shadow-lg">
        <div className="flex items-center justify-between border-b border-slate-800/60 pb-2 mb-3">
          <div className="flex items-center gap-2 min-w-0">
            <Monitor className="text-emerald-400 h-4 w-4 shrink-0" />
            <h2 className="text-xs font-mono font-bold text-slate-300 truncate tracking-wide">{videoTitle}</h2>
          </div>
          <span className="text-[10px] font-mono bg-slate-950 border border-slate-800 px-2 py-0.5 rounded text-slate-500 uppercase tracking-widest">
            {frames.length} Keys
          </span>
        </div>
        <div className="flex gap-4 overflow-x-auto pb-1 custom-scrollbar">
          {frames.map((item) => {
            const isSelected = selectedIndex === item.originalIndex;
            return (
              <div
                id={`card-${item.originalIndex}`}
                key={`${item.video_id}_${item.frame_id}`}
                onClick={() => handleSelectCandidate(item, item.originalIndex)}
                className={`w-44 bg-slate-950/80 border rounded-xl overflow-hidden shrink-0 cursor-pointer transition-all duration-200 relative ${
                  isSelected ? 'border-emerald-500 shadow-md shadow-emerald-950/40 bg-slate-900/60' : 'border-slate-800/80 hover:border-slate-700'
                }`}
              >
                <div className="relative aspect-video bg-slate-900">
                  <img src={`${API_BASE}${item.thumb_url}`} alt="" loading="lazy" className="h-full w-full object-cover" />
                  <span className="absolute top-1 left-1 bg-slate-950/90 text-[9px] font-mono px-1.5 py-0.5 rounded border border-slate-800 text-slate-400">#{item.rank}</span>
                  <span className="absolute bottom-1 right-1 bg-slate-950/90 text-[9px] font-mono px-1.5 py-0.5 rounded border border-slate-800 text-amber-400 font-bold">{item.timestamp}s</span>
                </div>
                <div className="p-2.5">
                  <p className="text-[11px] font-mono text-slate-400 font-medium">Frame: {item.frame_id}</p>
                  <div className="mt-1.5 flex items-center justify-between text-[10px] bg-slate-950 px-2 py-1 rounded border border-slate-900 font-mono">
                    <span className="text-slate-600 font-bold">SIM</span>
                    <span className="text-emerald-400 font-black">{item.score.toFixed(4)}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    ));
  };

  return (
    <div className="h-screen w-screen flex flex-col overflow-hidden bg-[#050811] text-slate-200 font-sans select-none antialiased relative">
      
      {/* ─── THANH ĐIỀU HƯỚNG TOP-BAR CHUẨN KÍNH MỜ CỐ ĐỊNH CHIỀU CAO ─── */}
      <header className="h-16 shrink-0 bg-slate-900/40 backdrop-blur-xl border-b border-slate-800/50 px-6 flex items-center justify-between gap-6 z-10 shadow-xl">
        <div className="flex items-center gap-3 shrink-0">
          <div className="bg-emerald-500/10 p-2 rounded-xl border border-emerald-500/20 shadow-inner">
            <Zap className="h-4 w-4 text-emerald-400 fill-current animate-pulse" />
          </div>
          <div>
            <h1 className="text-xs font-black tracking-widest bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent uppercase font-mono">
              THUNDERRETRIEVE
            </h1>
            <p className="text-[9px] font-mono text-slate-500 uppercase font-bold tracking-wider mt-0.5">P0 Workspace Console</p>
          </div>
        </div>
        
        {/* KHUNG SEARCH ĐƯỢC THIẾT KẾ CO GIÃN ĐỘC LẬP CHỐNG ĐÈ CHỮ */}
        <form onSubmit={handleSearch} className="flex-1 max-w-3xl flex items-center gap-3 bg-slate-950/80 border border-slate-800 rounded-xl p-1 shadow-inner focus-within:border-emerald-500/40 transition-all">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-600" />
            <input
              ref={searchInputRef}
              type="text"
              placeholder="Gõ từ khóa tiếng Anh tìm kiếm... (Bấm '/' để gõ nhanh, 'Esc' để thoát ra dùng phím mũi tên)"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full bg-transparent pl-9 pr-4 py-2 text-xs text-slate-200 font-semibold focus:outline-none placeholder-slate-600"
            />
          </div>
          
          <select 
            value={topK} 
            onChange={(e) => setTopK(e.target.value)}
            className="bg-slate-900 border border-slate-800 text-slate-400 text-[10px] font-mono font-bold rounded-lg px-2 py-1.5 focus:outline-none cursor-pointer"
          >
            <option value="10">10 ITEMS</option>
            <option value="50">50 ITEMS</option>
            <option value="100">100 ITEMS</option>
          </select>
          
          <button
            type="submit"
            disabled={loading}
            className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-black text-[10px] tracking-widest uppercase px-5 py-2 rounded-lg transition-all flex items-center gap-2 shrink-0 h-8"
          >
            {loading ? <Loader2 className="h-3 w-3 animate-spin" /> : <Play className="h-2.5 w-2.5 fill-current" />}
            EXECUTE
          </button>
        </form>

        <div className="flex items-center gap-4 shrink-0 text-[10px] font-mono bg-slate-950 border border-slate-800/60 px-3 py-2 rounded-xl shadow-inner">
          <div className="flex items-center gap-1">
            <Cpu className="h-3 w-3 text-slate-600" />
            <span className="text-slate-500">LATENCY:</span>
            <span className="text-amber-400 font-black">{tookMs}ms</span>
          </div>
          <span className="text-slate-800">|</span>
          <div className="flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400"></span>
            <span className="text-emerald-400 font-black uppercase">Qdrant Cloud</span>
          </div>
        </div>
      </header>

      {/* ─── HẠ TẦNG BA KHOANG WORKSPACE CHỐNG TRÀN VÀ ĐÈ NHAU LUYỆN TẬP ─── */}
      <div className="flex-1 flex overflow-hidden w-full relative z-0">
        
        {/* KHOANG 1: SIDEBAR TRÁI QUẢN LÝ PANEL BỘ LỌC */}
        <aside className="w-60 border-r border-slate-800/40 bg-slate-900/10 backdrop-blur-md p-4 flex flex-col gap-5 shrink-0">
          <div>
            <div className="text-[9px] font-black uppercase tracking-widest text-slate-500 mb-3 flex items-center gap-1.5">
              <Zap className="h-3.5 w-3.5 text-slate-400" /> SEARCH MODE
            </div>
            <div className="flex flex-col gap-1.5">
              <button
                onClick={() => setSearchMode('visual')}
                className={`w-full text-left px-3.5 py-2.5 rounded-xl text-xs font-bold flex items-center gap-2 border transition-all duration-300 ${
                  searchMode === 'visual' ? 'bg-gradient-to-r from-emerald-500/10 to-teal-500/5 border-emerald-500/30 text-emerald-400 font-black shadow-inner' : 'bg-slate-950/20 border-slate-800/80 text-slate-500 hover:bg-slate-900/40'
                }`}
              >
                <ImageIcon className="h-3.5 w-3.5" /> Visual KIS Search
              </button>
              <button
                onClick={() => setSearchMode('qa')}
                className={`w-full text-left px-3.5 py-2.5 rounded-xl text-xs font-bold flex items-center gap-2 border transition-all duration-300 ${
                  searchMode === 'qa' ? 'bg-gradient-to-r from-indigo-500/10 to-purple-500/5 border-indigo-500/30 text-indigo-400 font-black shadow-inner' : 'bg-slate-950/20 border-slate-800/80 text-slate-500 hover:bg-slate-900/40'
                }`}
              >
                <Layers className="h-3.5 w-3.5" /> Question Answering
              </button>
              <button
                onClick={() => setSearchMode('trake')}
                className={`w-full text-left px-3.5 py-2.5 rounded-xl text-xs font-bold flex items-center gap-2 border transition-all duration-300 ${
                  searchMode === 'trake' ? 'bg-gradient-to-r from-amber-500/10 to-orange-500/5 border-amber-500/30 text-amber-400 font-black shadow-inner' : 'bg-slate-950/20 border-slate-800/80 text-slate-500 hover:bg-slate-900/40'
                }`}
              >
                <Monitor className="h-3.5 w-3.5" /> Target Tracking
              </button>
            </div>
          </div>

          <div className="border-t border-slate-800/40 pt-4">
            <div className="text-[9px] font-black uppercase tracking-widest text-slate-500 mb-3 flex items-center gap-1.5">
              <Filter className="h-3.5 w-3.5 text-slate-400" /> FACETED FILTER
            </div>
            <div className="flex flex-col gap-1.5">
              <span className="text-[10px] font-mono text-slate-400 font-bold uppercase tracking-wider">Lọc Tên Video</span>
              <input 
                type="text" 
                placeholder="Nhập mã video (vd: L01...)"
                value={videoFilter}
                onChange={(e) => setVideoFilter(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800/80 rounded-xl px-3 py-2 text-xs text-slate-300 font-semibold focus:outline-none focus:border-slate-700/60 transition-colors"
              />
            </div>
          </div>

          <div className="border-t border-slate-800/40 pt-4">
            <div className="text-[9px] font-black uppercase tracking-widest text-slate-500 mb-3 flex items-center gap-1.5">
              <Sliders className="h-3.5 w-3.5 text-slate-400" /> VIEW MODE ENGINE
            </div>
            <div className="flex flex-col gap-2">
              <button
                onClick={() => setGroupByVideo(false)}
                className={`w-full text-left px-3.5 py-2.5 rounded-xl text-xs font-bold flex items-center gap-2 border transition-all duration-300 ${
                  !groupByVideo ? 'bg-gradient-to-r from-emerald-500/10 to-teal-500/5 border-emerald-500/30 text-emerald-400 font-black shadow-inner' : 'bg-slate-950/20 border-slate-800/80 text-slate-500 hover:bg-slate-900/40'
                }`}
              >
                <Grid className="h-3.5 w-3.5" /> Flat Grid Viewer
              </button>
              <button
                onClick={() => setGroupByVideo(true)}
                className={`w-full text-left px-3.5 py-3 rounded-xl text-xs font-bold flex items-center gap-2 border transition-all duration-300 ${
                  groupByVideo ? 'bg-gradient-to-r from-emerald-500/10 to-teal-500/5 border-emerald-500/30 text-emerald-400 font-black shadow-inner' : 'bg-slate-950/20 border-slate-800/80 text-slate-500 hover:bg-slate-900/40'
                }`}
              >
                <List className="h-3.5 w-3.5" /> Temporal Cluster Row
              </button>
            </div>
          </div>

          <div className="mt-auto bg-slate-950/40 border border-slate-800/60 rounded-xl p-3.5 text-[10px] text-slate-500 font-semibold leading-relaxed shadow-inner">
            <div className="text-slate-400 font-bold mb-1.5 flex items-center gap-1 uppercase text-[9px] font-mono">
              <Zap className="h-3.5 w-3.5 text-amber-400 fill-current" /> SYSTEM HOTKEYS
            </div>
            <div className="flex flex-col gap-1.5 font-mono">
              <div className="flex items-center justify-between border-b border-slate-900/50 pb-0.5"><span>Search</span> <span className="text-slate-400 font-bold">[ / ]</span></div>
              <div className="flex items-center justify-between border-b border-slate-900/50 pb-0.5"><span>Exit</span> <span className="text-slate-400 font-bold">[Esc]</span></div>
              <div className="flex items-center justify-between border-b border-slate-900/50 pb-0.5"><span>Move</span> <span className="text-slate-400 font-bold">[←↑↓→]</span></div>
              <div className="flex items-center justify-between text-emerald-500"><span>SUBMIT</span> <span className="text-emerald-400 font-bold">[Enter]</span></div>
            </div>
          </div>
        </aside>

        {/* KHOANG 2: TRUNG TÂM - HIỂN THỊ LƯỚI ẢNH KẾT QUẢ TÌM KIẾM */}
        <main className="flex-1 overflow-y-auto p-5 custom-scrollbar bg-[#05070e]">
          {/* QA Answer Widget */}
          {searchMode === 'qa' && apiAnswer && filteredResults.length > 0 && (
            <div className="mb-5 p-4 rounded-xl border border-indigo-500/30 bg-indigo-950/20 backdrop-blur-md text-indigo-200 font-mono text-xs shadow-lg flex items-start gap-3 animate-fadeIn">
              <span className="bg-indigo-500/20 px-2 py-0.5 rounded font-bold text-indigo-400 border border-indigo-500/30 shrink-0">QA ANSWER</span>
              <span>{apiAnswer}</span>
            </div>
          )}

          {/* TRAKE Trajectory Widget */}
          {searchMode === 'trake' && trajectory && trajectory.length > 0 && filteredResults.length > 0 && (
            <div className="mb-6 p-4 rounded-xl border border-amber-500/30 bg-amber-950/10 backdrop-blur-md shadow-lg animate-fadeIn">
              <div className="text-[10px] font-mono font-black text-amber-400 uppercase tracking-widest mb-3 flex items-center gap-1.5">
                <Zap className="h-3.5 w-3.5 fill-current animate-pulse text-amber-400" /> TRACKED TARGET TRAJECTORY PATH
              </div>
              <div className="flex items-center gap-3 overflow-x-auto pb-2 custom-scrollbar">
                {trajectory.map((item, idx) => (
                  <React.Fragment key={idx}>
                    {idx > 0 && <span className="text-slate-700 font-bold text-xs shrink-0">➔</span>}
                    <div 
                      onClick={() => {
                        const origIndex = results.findIndex(r => r.video_id === item.video_id && r.frame_id === item.frame_id);
                        if (origIndex !== -1) handleSelectCandidate(item, origIndex);
                      }}
                      className="w-36 bg-slate-950 border border-amber-500/20 rounded-xl overflow-hidden shrink-0 cursor-pointer hover:border-amber-400 transition-colors"
                    >
                      <div className="relative aspect-video">
                        <img src={`${API_BASE}${item.thumb_url}`} alt="" loading="lazy" className="h-full w-full object-cover" />
                        <span className="absolute bottom-1 right-1 bg-slate-950/90 text-[8px] font-mono px-1 rounded text-amber-400">{item.timestamp}s</span>
                      </div>
                      <div className="p-2 text-center text-[9px] font-mono text-slate-400 border-t border-slate-900 truncate" title={item.video_id}>
                        {item.frame_id}
                      </div>
                    </div>
                  </React.Fragment>
                ))}
              </div>
            </div>
          )}

          {filteredResults.length === 0 ? (
            <div className="h-full w-full flex flex-col items-center justify-center text-slate-600 gap-2 border border-slate-800/30 bg-slate-900/10 rounded-2xl p-6">
              <ImageIcon className="h-7 w-7 text-slate-700 stroke-[1.5]" />
              <div className="text-center">
                <p className="text-xs font-bold text-slate-500 uppercase tracking-widest">Workspace Idling</p>
                <p className="text-[10px] text-slate-600 mt-0.5 font-medium">Vui lòng nạp câu truy vấn tiếng Anh ở thanh trên để bốc tách vector mây.</p>
              </div>
            </div>
          ) : groupByVideo ? (
            renderGroupedResults()
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-4 animate-fadeIn">
              {filteredResults.map((item, index) => {
                const isSelected = selectedIndex === index;
                return (
                  <div
                    id={`card-${index}`}
                    key={`${item.video_id}_${item.frame_id}`}
                    onClick={() => handleSelectCandidate(item, index)}
                    className={`bg-slate-900/30 backdrop-blur-sm rounded-xl overflow-hidden border cursor-pointer group flex flex-col justify-between transition-all duration-200 ${
                      isSelected 
                        ? 'border-emerald-500 ring-2 ring-emerald-500/20 bg-slate-900/60 shadow-xl shadow-emerald-950/40 transform scale-[1.01]' 
                        : 'border-slate-800/50 hover:border-slate-700 hover:bg-slate-900/20'
                    }`}
                  >
                    <div className="relative aspect-video bg-slate-950 overflow-hidden shadow-inner">
                      <img src={`${API_BASE}${item.thumb_url}`} alt="" loading="lazy" className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                      <div className="absolute top-2 left-2 bg-slate-950/90 text-[9px] font-mono font-black px-2 py-0.5 rounded-md border border-slate-800 text-slate-300 tracking-wider">
                        RANK {item.rank}
                      </div>
                      <div className="absolute bottom-2 right-2 bg-slate-950/90 text-[9px] font-mono px-2 py-0.5 rounded-md border border-slate-800 text-amber-400 font-bold flex items-center gap-1">
                        <Clock className="h-3 w-3 stroke-[2.5]" /> {item.timestamp}s
                      </div>
                    </div>
                    <div className="p-3 flex-1 flex flex-col justify-between gap-2.5">
                      <p className="font-bold text-xs text-slate-300 truncate font-mono tracking-tight" title={item.video_id}>{item.video_id}</p>
                      <div className="flex items-center justify-between text-[10px] bg-slate-950 border border-slate-900/80 px-2.5 py-1.5 rounded-xl font-mono">
                        <span className="text-slate-600 font-bold uppercase tracking-wider">CLIP Score:</span>
                        <span className="text-emerald-400 font-black">{item.score.toFixed(4)}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </main>

        {/* KHOANG 3: SIDEBAR PHẢI - INSPECTION ẢNH CHI TIẾT & CHỐNG PENALTY NỘP BÀI SIÊU CẤP */}
        <aside className="w-[380px] border-l border-slate-800/40 bg-slate-900/40 backdrop-blur-2xl flex flex-col justify-between overflow-hidden shrink-0 shadow-2xl relative">
          {selectedCandidate ? (
            <div className="h-full flex flex-col justify-between overflow-hidden">
              
              <div className="flex-1 overflow-y-auto p-5 flex flex-col gap-5 custom-scrollbar">
                {/* 1. KHUNG INSPECT ẢNH LỚN CHẤT LƯỢNG CAO */}
                <div>
                  <div className="text-[9px] font-black uppercase tracking-widest text-slate-500 mb-2.5 flex items-center gap-2">
                    <ImageIcon className="h-3.5 w-3.5 text-emerald-400" /> SCREEN INSPECTOR
                  </div>
                  <div className="rounded-2xl overflow-hidden border border-slate-800 bg-slate-950 aspect-video relative shadow-inner p-1">
                    <img src={`${API_BASE}${selectedCandidate.frame_url}`} alt="Target" className="w-full h-full object-contain rounded-xl" />
                  </div>
                </div>

                {/* 2. THANH TIMELINE KHUNG HÌNH LÂN CẬN */}
                <div>
                  <div className="text-[9px] font-black uppercase tracking-widest text-slate-500 mb-2.5 flex items-center gap-2">
                    <Clock className="h-3.5 w-3.5 text-amber-400" /> NEIGHBOR TIMELINE (+/- 5s)
                  </div>
                  {loadingNeighbors ? (
                    <div className="flex justify-center items-center py-6 bg-slate-950 rounded-2xl border border-slate-800/80"><Loader2 className="animate-spin text-emerald-400 h-4 w-4" /></div>
                  ) : (
                    <div className="flex gap-2 overflow-x-auto p-2 bg-slate-950 rounded-2xl border border-slate-800/80 custom-scrollbar">
                      {neighbors.map((nb) => (
                        <div
                          key={nb.frame_id}
                          onClick={() => handleSelectCandidate({
                            ...selectedCandidate,
                            frame_id: nb.frame_id,
                            timestamp: nb.timestamp,
                            thumb_url: nb.thumb_url,
                            frame_url: nb.frame_url
                          }, selectedIndex)}
                          className={`flex-shrink-0 w-24 rounded-xl border overflow-hidden cursor-pointer bg-slate-900 transition-all duration-200 relative ${
                            nb.is_current ? 'border-amber-500 ring-2 ring-amber-500/30 transform scale-[0.98]' : 'border-slate-800 hover:border-slate-700'
                          }`}
                        >
                          <img src={`${API_BASE}${nb.thumb_url}`} alt="" loading="lazy" className="h-12 w-full object-cover" />
                          <div className="p-1 text-[9px] font-mono text-center font-bold text-slate-400 bg-slate-950 border-t border-slate-900/60">
                            {nb.frame_id}s
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* 3. THÔNG TIN METADATA BIÊN BẢN */}
                <div>
                  <div className="text-[9px] font-black uppercase tracking-widest text-slate-500 mb-2.5 flex items-center gap-2">
                    <Layers className="h-3.5 w-3.5 text-indigo-400" /> ARTIFACT METADATA
                  </div>
                  <div className="bg-slate-950 border border-slate-800/60 rounded-2xl p-4 text-xs flex flex-col gap-3 font-mono">
                    <div className="border-b border-slate-900 pb-2">
                      <span className="text-slate-600 text-[9px] uppercase font-black tracking-widest block mb-0.5">Video Title</span>
                      <span className="text-slate-300 text-xs block font-bold truncate" title={selectedCandidate.video_id}>{selectedCandidate.video_id}</span>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <span className="text-slate-600 text-[9px] uppercase font-black tracking-widest block mb-0.5">Frame ID</span>
                        <span className="text-slate-400 text-xs font-bold">{selectedCandidate.frame_id}.jpg</span>
                      </div>
                      <div>
                        <span className="text-slate-600 text-[9px] uppercase font-black tracking-widest block mb-0.5">Timestamp</span>
                        <span className="text-amber-400 font-black text-xs">{selectedCandidate.timestamp.toFixed(1)}s</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* 4. KHU VỰC THAO TÁC SUBMIT CỐ ĐỊNH Ở ĐÁY CHỐNG PENALTY CHẮC CHẮN */}
              <div className="p-5 bg-slate-950 border-t border-slate-800/80 shadow-2xl flex flex-col gap-2 relative shrink-0">
                <button
                  onClick={handleSubmitDryRun}
                  className="w-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-black py-3.5 px-4 rounded-xl flex items-center justify-center gap-2 shadow-xl shadow-emerald-950/40 hover:shadow-emerald-900/30 active:scale-[0.99] transition-all text-xs tracking-widest uppercase border border-emerald-500/20"
                >
                  <CheckCircle2 className="h-4 w-4 stroke-[3]" /> TRANSMIT EVIDENCE [ENTER]
                </button>
              </div>

            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-slate-600 text-xs p-6 text-center gap-3">
              <ImageIcon className="h-6 w-6 text-slate-800 stroke-[1.5]" />
              <p className="max-w-[200px] text-slate-500 font-medium leading-relaxed">Vui lòng chọn một khung hình bên khoang kết quả để kích hoạt trạm điều phối bằng chứng.</p>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}