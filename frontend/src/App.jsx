import { useState, useCallback } from 'react'
import axios from 'axios'
import DropZone from './components/DropZone'
import FileQueue from './components/FileQueue'
import RobotScene from './components/RobotScene'
import AnalyzeButton from './components/AnalyzeButton'
import CategoryTabs from './components/CategoryTabs'
import SummaryCards from './components/SummaryCards'
import TransactionTable from './components/TransactionTable'
import { computeSummary } from './data/mockData'

export default function App() {
  const [files, setFiles] = useState([])
  const [status, setStatus] = useState('idle')
  const [workingStep, setWorkingStep] = useState('')
  const [apiError, setApiError] = useState('')
  const [activeCategory, setActiveCategory] = useState('all')
  const [transactions, setTransactions] = useState([])
  const [sortConfig, setSortConfig] = useState({ key: 'date', dir: 'desc' })

  const handleFilesAdded = useCallback((newFiles) => {
    setFiles((prev) => [
      ...prev,
      ...newFiles.map((file) => ({
        file,
        id: crypto.randomUUID(),
        uploadStatus: 'queued',
      })),
    ])
  }, [])

  const handleRemoveFile = useCallback((id) => {
    setFiles((prev) => prev.filter((f) => f.id !== id))
  }, [])

  const setFileUploadStatus = (id, uploadStatus) =>
    setFiles((prev) => prev.map((f) => (f.id === id ? { ...f, uploadStatus } : f)))

  const handleAnalyze = async () => {
    if (!files.length) return

    setStatus('working')
    setTransactions([])
    setApiError('')

    const allRawTransactions = []
    const uploadErrors = []

    for (const { id, file } of files) {
      setWorkingStep(`Uploading ${file.name}...`)
      setFileUploadStatus(id, 'uploading')

      try {
        const formData = new FormData()
        formData.append('files', file)
        const { data } = await axios.post('/api/upload', formData)
        allRawTransactions.push(...data)
        setFileUploadStatus(id, 'done')
      } catch (err) {
        setFileUploadStatus(id, 'error')
        const detail = err.response?.data?.detail ?? err.message ?? 'upload failed'
        uploadErrors.push(`${file.name}: ${detail}`)
      }
    }

    if (!allRawTransactions.length) {
      setApiError(
        uploadErrors.length
          ? uploadErrors.join('\n\n')
          : 'No transactions could be parsed from the uploaded files. Check that your PDF or CSV contains standard bank transaction rows.',
      )
      setStatus('error')
      return
    }

    try {
      setWorkingStep(`Categorizing ${allRawTransactions.length} transactions with Claude AI...`)
      const { data: enriched } = await axios.post('/api/analyze', allRawTransactions)
      setTransactions(enriched.map((transaction, index) => ({ id: index, ...transaction })))
      setStatus('done')
    } catch (err) {
      const detail = err.response?.data?.detail ?? 'Analysis failed. Is the backend running?'
      setApiError(detail)
      setStatus('error')
    }
  }

  const filteredTransactions =
    activeCategory === 'all'
      ? transactions
      : transactions.filter((t) => t.category === activeCategory)

  const sortedTransactions = [...filteredTransactions].sort((a, b) => {
    const { key, dir } = sortConfig
    const aVal = a[key]
    const bVal = b[key]
    if (aVal < bVal) return dir === 'asc' ? -1 : 1
    if (aVal > bVal) return dir === 'asc' ? 1 : -1
    return 0
  })

  const summary = transactions.length ? computeSummary(transactions) : null

  return (
    <div className="min-h-screen bg-navy-950 flex flex-col">
      <header className="border-b border-navy-700 bg-navy-900/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-[1400px] mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-accent-blue flex items-center justify-center text-sm font-bold">
              AI
            </div>
            <span className="font-bold text-xl tracking-tight text-white">
              FinBot<span className="text-accent-blue">.AI</span>
            </span>
            <span className="text-xs font-mono text-navy-600 border border-navy-700 px-2 py-0.5 rounded-full ml-1">
              v0.1 beta
            </span>
          </div>
          <p className="text-slate-400 text-sm hidden md:block">
            AI-powered bank and credit card statement analyzer
          </p>
        </div>
      </header>

      <main className="flex-1 max-w-[1400px] mx-auto w-full px-4 sm:px-6 py-6 sm:py-8 grid grid-cols-1 lg:grid-cols-[360px_minmax(0,1fr)] xl:grid-cols-[420px_minmax(0,1fr)] gap-6">
        <aside className="flex flex-col gap-4">
          <DropZone onFilesAdded={handleFilesAdded} disabled={status === 'working'} />
          <FileQueue files={files} onRemove={handleRemoveFile} disabled={status === 'working'} />
          <RobotScene status={status} />
          <AnalyzeButton
            onClick={handleAnalyze}
            disabled={!files.length || status === 'working'}
            status={status}
          />
        </aside>

        <section className="flex flex-col gap-4 min-w-0">
          {status === 'idle' && transactions.length === 0 && <EmptyState />}
          {status === 'working' && <WorkingState step={workingStep} />}
          {status === 'error' && <ErrorState message={apiError} onRetry={() => setStatus('idle')} />}

          {transactions.length > 0 && (
            <>
              <SummaryCards summary={summary} />
              <div className="panel p-4 flex flex-col gap-4 flex-1">
                <CategoryTabs
                  active={activeCategory}
                  onChange={setActiveCategory}
                  transactions={transactions}
                />
                <TransactionTable
                  transactions={sortedTransactions}
                  sortConfig={sortConfig}
                  onSort={(key) =>
                    setSortConfig((prev) => ({
                      key,
                      dir: prev.key === key && prev.dir === 'asc' ? 'desc' : 'asc',
                    }))
                  }
                />
              </div>
            </>
          )}
        </section>
      </main>
    </div>
  )
}

function EmptyState() {
  return (
    <div className="panel flex-1 flex flex-col items-center justify-center gap-4 py-20 px-6 text-center">
      <div className="w-16 h-16 rounded-lg bg-navy-800 border border-navy-700 flex items-center justify-center text-2xl font-mono text-slate-500">
        CSV
      </div>
      <p className="text-slate-300 font-medium">Upload a bank or credit card statement to get started.</p>
      <p className="text-slate-500 text-sm font-mono">Supports PDF and CSV formats</p>
    </div>
  )
}

function WorkingState({ step }) {
  return (
    <div className="panel flex-1 flex flex-col items-center justify-center gap-6 py-20 px-6">
      <div className="relative">
        <div className="w-16 h-16 rounded-full border-4 border-navy-700 border-t-accent-blue animate-spin" />
        <div className="absolute inset-0 flex items-center justify-center text-sm font-bold text-accent-blue">
          AI
        </div>
      </div>
      <div className="text-center">
        <p className="text-white font-semibold text-lg">Analyzing your statements...</p>
        <p className="text-slate-400 text-sm mt-1 font-mono">
          {step || 'Claude AI is reading and categorizing transactions'}
        </p>
      </div>
      <div className="flex gap-1">
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="w-2 h-2 rounded-full bg-accent-blue animate-bounce"
            style={{ animationDelay: `${i * 0.15}s` }}
          />
        ))}
      </div>
    </div>
  )
}

function ErrorState({ message, onRetry }) {
  return (
    <div className="panel flex-1 flex flex-col items-center justify-center gap-4 py-20 px-6 text-center">
      <div className="w-14 h-14 rounded-lg bg-red-500/10 border border-red-500/30 flex items-center justify-center text-red-300 font-bold">
        !
      </div>
      <div className="max-w-2xl w-full">
        <p className="text-white font-semibold text-lg">Something went wrong</p>
        <p className="text-slate-400 text-sm mt-2 font-mono whitespace-pre-wrap text-left bg-navy-900 rounded-lg p-4 border border-navy-700">
          {message}
        </p>
      </div>
      <button onClick={onRetry} className="btn-primary mt-2">
        Try again
      </button>
    </div>
  )
}
