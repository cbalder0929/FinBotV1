import { useRef, useState, useCallback } from 'react'

const ACCEPTED = '.pdf,.csv'
const MAX_MB = 10

export default function DropZone({ onFilesAdded, disabled }) {
  const inputRef = useRef(null)
  const [dragOver, setDragOver] = useState(false)
  const [error, setError] = useState('')

  const validate = (fileList) => {
    const valid = []
    const errs = []

    Array.from(fileList).forEach((file) => {
      const ext = file.name.split('.').pop().toLowerCase()
      if (!['pdf', 'csv'].includes(ext)) {
        errs.push(`${file.name}: unsupported format`)
      } else if (file.size > MAX_MB * 1024 * 1024) {
        errs.push(`${file.name}: exceeds ${MAX_MB} MB limit`)
      } else {
        valid.push(file)
      }
    })

    setError(errs[0] ?? '')
    return valid
  }

  const handleDrop = useCallback(
    (event) => {
      event.preventDefault()
      setDragOver(false)
      if (disabled) return

      const valid = validate(event.dataTransfer.files)
      if (valid.length) onFilesAdded(valid)
    },
    [disabled, onFilesAdded],
  )

  const handleDragOver = (event) => {
    event.preventDefault()
    if (!disabled) setDragOver(true)
  }

  const handleFileInput = (event) => {
    const valid = validate(event.target.files)
    if (valid.length) onFilesAdded(valid)
    event.target.value = ''
  }

  return (
    <div
      role="button"
      tabIndex={disabled ? -1 : 0}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={() => setDragOver(false)}
      onClick={() => !disabled && inputRef.current?.click()}
      onKeyDown={(event) => event.key === 'Enter' && !disabled && inputRef.current?.click()}
      className={[
        'panel border-2 border-dashed cursor-pointer select-none',
        'flex flex-col items-center justify-center gap-3 px-6 py-8',
        'transition-all duration-200',
        dragOver ? 'border-accent-blue bg-blue-500/10' : 'border-navy-600 hover:border-navy-500',
        disabled ? 'opacity-40 cursor-not-allowed' : '',
      ].join(' ')}
    >
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED}
        multiple
        className="hidden"
        onChange={handleFileInput}
      />

      <div className="w-14 h-14 rounded-lg bg-navy-800 border border-navy-600 flex items-center justify-center text-sm font-mono text-slate-300">
        {dragOver ? 'ADD' : 'PDF'}
      </div>

      <div className="text-center">
        <p className="font-semibold text-slate-200">
          {dragOver ? 'Drop files here' : 'Drop statements here'}
        </p>
        <p className="text-slate-500 text-sm mt-0.5">
          or <span className="text-accent-blue">browse files</span>
        </p>
      </div>

      <div className="flex gap-2 mt-1 flex-wrap justify-center">
        <span className="badge bg-navy-700 text-slate-400">PDF</span>
        <span className="badge bg-navy-700 text-slate-400">CSV</span>
        <span className="badge bg-navy-700 text-slate-400">Max {MAX_MB} MB</span>
      </div>

      {error && <p className="text-red-400 text-xs font-mono text-center mt-1">{error}</p>}
    </div>
  )
}
