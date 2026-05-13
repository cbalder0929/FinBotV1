const fmt = (bytes) => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 ** 2) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 ** 2).toFixed(1)} MB`
}

const extIcon = (name) => name.split('.').pop().toLowerCase().toUpperCase()

function StatusBadge({ uploadStatus }) {
  if (uploadStatus === 'uploading') {
    return (
      <span className="w-4 h-4 border-2 border-navy-600 border-t-accent-blue rounded-full animate-spin shrink-0" />
    )
  }
  if (uploadStatus === 'done') {
    return <span className="text-emerald-400 text-sm shrink-0">OK</span>
  }
  if (uploadStatus === 'error') {
    return <span className="text-red-400 text-sm shrink-0" title="Upload failed">ERR</span>
  }
  return null
}

export default function FileQueue({ files, onRemove, disabled }) {
  if (!files.length) return null

  const doneCount = files.filter((file) => file.uploadStatus === 'done').length
  const hasStarted = files.some((file) => file.uploadStatus !== 'queued')

  return (
    <div className="panel p-3 flex flex-col gap-2">
      <div className="flex items-center justify-between px-1">
        <p className="text-xs font-mono text-slate-500">
          {files.length} file{files.length !== 1 ? 's' : ''} queued
        </p>
        {hasStarted && (
          <p className="text-xs font-mono text-slate-500">
            {doneCount}/{files.length} uploaded
          </p>
        )}
      </div>
      <ul className="flex flex-col gap-1.5 max-h-48 overflow-y-auto pr-1">
        {files.map(({ id, file, uploadStatus = 'queued' }) => (
          <li
            key={id}
            className="flex items-center gap-3 bg-navy-800 rounded-lg px-3 py-2 group"
          >
            <span className="text-[10px] font-mono text-slate-400 shrink-0 w-8">
              {extIcon(file.name)}
            </span>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-slate-200 truncate">{file.name}</p>
              <p className="text-xs font-mono text-slate-500">{fmt(file.size)}</p>
            </div>
            <StatusBadge uploadStatus={uploadStatus} />
            {uploadStatus === 'queued' && (
              <button
                disabled={disabled}
                onClick={() => onRemove(id)}
                aria-label={`Remove ${file.name}`}
                className="opacity-100 sm:opacity-0 group-hover:opacity-100 transition-opacity text-slate-500 hover:text-red-400 text-lg leading-none disabled:cursor-not-allowed"
              >
                x
              </button>
            )}
          </li>
        ))}
      </ul>
    </div>
  )
}
