import React, { useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import { 
  Play, 
  Save, 
  Search, 
  Clock, 
  ExternalLink, 
  History,
  LayoutDashboard,
  Copy
} from 'lucide-react';
import { problemApi } from './services/api';

// --- Types ---
interface Version {
  name: string;
  path: string;
  status: string;
  lastModified: string;
}

interface Problem {
  problemId: string;
  title: string;
  rating: string;
  tags: string[];
  difficulty: string;
  versions: Version[];
}

interface TestResult {
  id: number;
  status: string;
  stdout: string;
  stderr: string;
  duration: number;
  exitCode: number;
}

const App: React.FC = () => {
  const [view, setView] = useState<'dashboard' | 'editor'>('dashboard');
  const [history, setHistory] = useState<Problem[]>([]);
  const [currentProblem, setCurrentProblem] = useState<Problem | null>(null);
  const [currentVersion, setCurrentVersion] = useState<string>('v1');
  const [code, setCode] = useState<string>('');
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [searchId, setSearchId] = useState('');
  const [loading, setLoading] = useState(false);
  const [isRunning, setIsRunning] = useState(false);

  // Load History on Mount
  useEffect(() => {
    loadHistory();
    resumeSession();
  }, []);

  const loadHistory = async () => {
    try {
      const res = await problemApi.getHistory();
      setHistory(res.data);
    } catch (err) {
      console.error("Failed to load history", err);
    }
  };

  const resumeSession = async () => {
    try {
      const res = await problemApi.resumeSession();
      if (res.data.session) {
        const { problemId, difficulty, version } = res.data.session;
        openProblem(problemId, difficulty, version);
      }
    } catch (err) {
      console.error("Failed to resume session", err);
    }
  };

  const handleSearch = async (id?: string) => {
    const pid = id || searchId;
    if (!pid) return;
    setLoading(true);
    try {
      const res = await problemApi.initProblem(pid);
      const data = res.data.data;
      setCurrentProblem({
        problemId: data.problemId,
        title: data.title,
        rating: data.rating,
        tags: data.tags,
        difficulty: data.difficulty,
        versions: [] // Will be populated by loadHistory if needed
      });
      setCode(data.content);
      setCurrentVersion('v1');
      setView('editor');
      loadHistory();
    } catch (err) {
      alert("Failed to fetch problem from Codeforces");
    } finally {
      setLoading(false);
    }
  };

  const openProblem = async (problemId: string, difficulty: string, version: string) => {
    setLoading(true);
    try {
      const res = await problemApi.getProblemVersion(difficulty, problemId, version);
      const prob = history.find(h => h.problemId === problemId);
      if (prob) setCurrentProblem(prob);
      setCode(res.data.content);
      setCurrentVersion(version);
      setView('editor');
    } catch (err) {
      console.error("Failed to open problem", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (silent = false) => {
    if (!currentProblem) return;
    try {
      await problemApi.saveCode({
        problemId: currentProblem.problemId,
        version: currentVersion,
        difficulty: currentProblem.difficulty,
        content: code
      });
      if (!silent) {
        // Show brief toast or success indicator
        console.log("Saved");
        loadHistory();
      }
    } catch (err) {
      console.error("Failed to save", err);
    }
  };

  const handleRun = async () => {
    if (!currentProblem) return;
    setIsRunning(true);
    setTestResults([]);
    try {
      const res = await problemApi.runTest({
        code,
        problemId: currentProblem.problemId,
        difficulty: currentProblem.difficulty
      });
      setTestResults(res.data.results || []);
    } catch (err) {
      console.error("Failed to run tests", err);
    } finally {
      setIsRunning(false);
    }
  };

  const handleCopyForSubmit = async () => {
    if (!currentProblem) return;
    try {
      const res = await problemApi.cleanCode({
        code,
        problemId: currentProblem.problemId,
        difficulty: currentProblem.difficulty
      });
      await navigator.clipboard.writeText(res.data.cleanedCode);
      alert("Cleaned code copied to clipboard!");
      window.open(`https://codeforces.com/problemset/submit`, '_blank');
    } catch (err) {
      console.error("Failed to clean code", err);
    }
  };

  // Dashboard View
  const Dashboard = () => (
    <div className="max-w-6xl mx-auto p-8 text-gray-200">
      <div className="flex justify-between items-center mb-12">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
          My Codeforces
        </h1>
        <div className="flex gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input 
              className="bg-gray-800 border border-gray-700 rounded-lg pl-10 pr-4 py-2 w-64 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter Problem ID (e.g. 78A)"
              value={searchId}
              onChange={(e) => setSearchId(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
          </div>
          <button 
            onClick={() => handleSearch()}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors"
          >
            Go
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
        <div className="bg-gray-800 p-6 rounded-2xl border border-gray-700">
          <div className="flex items-center gap-3 text-blue-400 mb-2">
            <LayoutDashboard className="w-5 h-5" />
            <span className="font-semibold uppercase tracking-wider text-xs">Total Solved</span>
          </div>
          <div className="text-3xl font-bold">{history.length}</div>
        </div>
        {/* Add more stat cards if needed */}
      </div>

      <div className="bg-gray-800 rounded-2xl border border-gray-700 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-700 bg-gray-800/50 flex justify-between items-center">
          <h2 className="text-xl font-bold flex items-center gap-2">
            <History className="w-5 h-5 text-purple-400" />
            Recent Problems
          </h2>
        </div>
        <div className="divide-y divide-gray-700">
          {history.length === 0 ? (
            <div className="p-12 text-center text-gray-500">No problems solved yet. Start by searching!</div>
          ) : history.map((prob) => (
            <div 
              key={prob.problemId} 
              className="px-6 py-4 hover:bg-gray-700/50 transition-colors flex items-center justify-between group"
            >
              <div className="flex items-center gap-6">
                <div className="w-16 text-center">
                  <span className="px-2 py-1 bg-gray-700 rounded text-xs font-mono text-gray-400">{prob.rating}</span>
                </div>
                <div>
                  <div className="text-lg font-semibold group-hover:text-blue-400 transition-colors">{prob.problemId} - {prob.title}</div>
                  <div className="flex gap-2 mt-1">
                    {prob.tags.map(t => (
                      <span key={t} className="text-[10px] bg-gray-900 text-gray-500 px-1.5 py-0.5 rounded uppercase">{t}</span>
                    ))}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-sm text-gray-500 flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  {prob.versions[0]?.lastModified.split(' ')[0]}
                </div>
                <button 
                  onClick={() => openProblem(prob.problemId, prob.difficulty, prob.versions[0]?.name || 'v1')}
                  className="p-2 hover:bg-blue-500/20 hover:text-blue-400 rounded-lg transition-all"
                >
                  <ExternalLink className="w-5 h-5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  // Editor View
  const EditorView = () => (
    <div className="flex flex-col h-screen bg-[#1e1e1e] text-gray-300">
      {/* Header */}
      <header className="h-14 border-b border-gray-800 flex items-center justify-between px-4 bg-[#252526]">
        <div className="flex items-center gap-4">
          <button 
            onClick={() => setView('dashboard')}
            className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
          >
            <LayoutDashboard className="w-5 h-5" />
          </button>
          <div className="h-6 w-[1px] bg-gray-700"></div>
          <div>
            <h2 className="font-bold flex items-center gap-2">
              <span className="text-blue-400">{currentProblem?.problemId}</span>
              <span className="text-gray-500">/</span>
              <span>{currentProblem?.title}</span>
            </h2>
          </div>
          <select 
            value={currentVersion}
            onChange={(e) => openProblem(currentProblem!.problemId, currentProblem!.difficulty, e.target.value)}
            className="bg-gray-800 text-sm px-2 py-1 rounded border border-gray-700 focus:outline-none"
          >
            {currentProblem?.versions.map(v => (
              <option key={v.name} value={v.name}>{v.name}</option>
            ))}
            <option value="new">+ New Version</option>
          </select>
        </div>

        <div className="flex items-center gap-2">
          <button 
            onClick={() => handleSave()}
            className="flex items-center gap-2 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 rounded text-sm font-medium transition-colors"
          >
            <Save className="w-4 h-4" /> Save
          </button>
          <button 
            onClick={handleRun}
            disabled={isRunning}
            className="flex items-center gap-2 px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white rounded text-sm font-medium transition-colors disabled:opacity-50"
          >
            <Play className="w-4 h-4" /> {isRunning ? 'Running...' : 'Run Test'}
          </button>
          <button 
            onClick={handleCopyForSubmit}
            className="flex items-center gap-2 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm font-medium transition-colors"
          >
            <Copy className="w-4 h-4" /> Submit
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex overflow-hidden">
        {/* Editor Side */}
        <div className="flex-1 border-r border-gray-800">
          <Editor
            height="100%"
            defaultLanguage="python"
            theme="vs-dark"
            value={code}
            onChange={(val) => setCode(val || '')}
            options={{
              fontSize: 14,
              minimap: { enabled: false },
              automaticLayout: true,
              scrollBeyondLastLine: false,
              padding: { top: 16 }
            }}
          />
        </div>

        {/* Results Side */}
        <div className="w-1/3 flex flex-col bg-[#1e1e1e]">
          <div className="px-4 py-3 border-b border-gray-800 font-semibold flex items-center justify-between">
            Test Results
            <div className="flex gap-2">
              {testResults.map(r => (
                <div key={r.id} className={`w-2 h-2 rounded-full ${r.status === 'AC' ? 'bg-green-500' : 'bg-red-500'}`}></div>
              ))}
            </div>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {testResults.length === 0 ? (
              <div className="text-center text-gray-500 mt-20">
                {isRunning ? 'Running tests...' : 'Click "Run Test" to see results'}
              </div>
            ) : testResults.map((res) => (
              <div key={res.id} className="bg-gray-800/50 rounded-lg border border-gray-800 overflow-hidden">
                <div className="px-3 py-2 bg-gray-800 flex justify-between items-center">
                  <span className="font-mono text-xs text-gray-400">Case #{res.id}</span>
                  <span className={`text-xs font-bold px-1.5 py-0.5 rounded ${
                    res.status === 'AC' ? 'bg-green-500/20 text-green-500' : 'bg-red-500/20 text-red-500'
                  }`}>
                    {res.status}
                  </span>
                </div>
                <div className="p-3 space-y-2">
                  <div>
                    <div className="text-[10px] text-gray-500 uppercase font-bold mb-1">Stdout</div>
                    <pre className="text-xs bg-black/30 p-2 rounded overflow-x-auto whitespace-pre-wrap font-mono">
                      {res.stdout || <span className="italic opacity-30">No output</span>}
                    </pre>
                  </div>
                  {res.stderr && (
                    <div>
                      <div className="text-[10px] text-red-400/70 uppercase font-bold mb-1">Stderr</div>
                      <pre className="text-xs bg-red-900/10 p-2 rounded overflow-x-auto whitespace-pre-wrap font-mono text-red-400">
                        {res.stderr}
                      </pre>
                    </div>
                  )}
                  <div className="text-[10px] text-gray-600">Duration: {res.duration}ms</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );

  return (
    <div className="min-h-screen bg-[#1e1e1e]">
      {view === 'dashboard' ? <Dashboard /> : <EditorView />}
      
      {/* Loading Overlay */}
      {loading && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-gray-800 p-8 rounded-2xl flex flex-col items-center gap-4">
            <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-blue-400 font-medium">Fetching Codeforces data...</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
