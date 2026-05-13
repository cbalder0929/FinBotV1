export default function AnalyzeButton({ onClick, disabled, status }) {
  const isWorking = status === 'working'

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={[
        'w-full rounded-lg py-3.5 font-semibold text-base transition-all duration-200',
        'flex items-center justify-center gap-2.5',
        isWorking
          ? 'bg-navy-800 text-slate-400 cursor-not-allowed border border-navy-600'
          : disabled
          ? 'bg-navy-800 text-slate-600 cursor-not-allowed border border-navy-700'
          : 'bg-accent-blue hover:bg-blue-500 active:scale-95 text-white shadow-lg shadow-blue-500/20',
      ].join(' ')}
    >
      {isWorking ? (
        <>
          <span className="w-4 h-4 border-2 border-slate-500 border-t-slate-300 rounded-full animate-spin" />
          Analyzing...
        </>
      ) : status === 'done' ? (
        <>
          <span>OK</span>
          Re-analyze
        </>
      ) : (
        <>
          <span>AI</span>
          Analyze with Claude AI
        </>
      )}
    </button>
  )
}
