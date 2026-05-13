export default function RobotScene({ status }) {
  const isWorking = status === 'working'

  return (
    <div className="panel p-4 flex flex-col items-center gap-3 select-none">
      <div className={isWorking ? 'robot-working' : ''}>
        <svg
          viewBox="0 0 200 220"
          className={`w-48 h-auto ${isWorking ? '' : 'animate-float'}`}
          xmlns="http://www.w3.org/2000/svg"
          aria-hidden="true"
        >
          <rect x="10" y="185" width="180" height="12" rx="4" fill="#1e293b" stroke="#334155" strokeWidth="1.5" />
          <rect x="0" y="193" width="200" height="8" rx="3" fill="#0f172a" stroke="#1e293b" strokeWidth="1" />
          <rect x="55" y="155" width="90" height="32" rx="4" fill="#1e293b" stroke="#334155" strokeWidth="1.5" />
          <rect x="60" y="110" width="80" height="50" rx="5" fill="#0f172a" stroke="#334155" strokeWidth="1.5" />
          <rect
            className="robot-screen"
            x="65"
            y="115"
            width="70"
            height="40"
            rx="3"
            fill={isWorking ? '#1d4ed8' : '#172554'}
          />
          <rect x="70" y="120" width={isWorking ? '40' : '45'} height="3" rx="1" fill="#60a5fa" opacity="0.8" />
          <rect x="70" y="128" width={isWorking ? '55' : '36'} height="3" rx="1" fill="#34d399" opacity="0.7" />
          <rect x="70" y="136" width={isWorking ? '30' : '52'} height="3" rx="1" fill="#60a5fa" opacity="0.5" />
          <rect x="90" y="158" width="20" height="3" rx="1" fill="#334155" />

          <rect x="65" y="65" width="70" height="50" rx="10" fill="#1e3a5f" stroke="#3b82f6" strokeWidth="1.5" />
          <rect x="75" y="75" width="50" height="2" rx="1" fill="#3b82f6" opacity="0.3" />
          <rect x="75" y="81" width="38" height="2" rx="1" fill="#3b82f6" opacity="0.2" />
          <circle cx="100" cy="95" r="6" fill={isWorking ? '#10b981' : '#334155'} />
          <circle cx="100" cy="95" r="3" fill={isWorking ? '#34d399' : '#475569'} />

          <rect x="38" y="72" width="28" height="12" rx="6" fill="#1e3a5f" stroke="#334155" strokeWidth="1.5" transform={isWorking ? 'rotate(-8 52 78)' : 'rotate(0 52 78)'} />
          <circle cx="40" cy="78" r="7" fill="#1e293b" stroke="#334155" strokeWidth="1.5" />
          <rect x="134" y="72" width="28" height="12" rx="6" fill="#1e3a5f" stroke="#334155" strokeWidth="1.5" transform={isWorking ? 'rotate(8 148 78)' : 'rotate(0 148 78)'} />
          <circle cx="160" cy="78" r="7" fill="#1e293b" stroke="#334155" strokeWidth="1.5" />

          <rect x="68" y="18" width="64" height="52" rx="14" fill="#1e3a5f" stroke="#3b82f6" strokeWidth="1.5" />
          <rect className="robot-eye" x="78" y="30" width="18" height="14" rx="5" fill={isWorking ? '#60a5fa' : '#3b82f6'} />
          <rect className="robot-eye" x="104" y="30" width="18" height="14" rx="5" fill={isWorking ? '#60a5fa' : '#3b82f6'} />
          <circle cx="87" cy="37" r="4" fill={isWorking ? '#bfdbfe' : '#93c5fd'} />
          <circle cx="113" cy="37" r="4" fill={isWorking ? '#bfdbfe' : '#93c5fd'} />
          <rect x="82" y="52" width="36" height="6" rx="3" fill="#0f172a" />
          <rect x="84" y="54" width={isWorking ? '24' : '32'} height="2.5" rx="1" fill="#3b82f6" opacity="0.5" />

          <rect x="98" y="5" width="4" height="16" rx="2" fill="#334155" />
          <circle cx="100" cy="5" r="5" fill={isWorking ? '#f59e0b' : '#3b82f6'} />
          {isWorking && <circle cx="100" cy="5" r="3" fill="#fde68a" className="animate-pulse" />}
          <circle cx="68" cy="44" r="5" fill="#0f172a" stroke="#334155" strokeWidth="1.5" />
          <circle cx="132" cy="44" r="5" fill="#0f172a" stroke="#334155" strokeWidth="1.5" />
        </svg>
      </div>

      <div className="text-center">
        <p className="text-sm font-semibold text-slate-300">
          {status === 'idle' && 'Ready to analyze'}
          {status === 'working' && 'Thinking...'}
          {status === 'done' && 'Analysis complete'}
        </p>
        <p className="text-xs text-slate-600 font-mono mt-0.5">
          {status === 'idle' && 'Upload a statement to begin'}
          {status === 'working' && 'Claude AI is categorizing transactions'}
          {status === 'done' && 'All transactions categorized'}
        </p>
      </div>
    </div>
  )
}
