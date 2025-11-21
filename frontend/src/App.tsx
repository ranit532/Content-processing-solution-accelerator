import React, { useState, useEffect } from 'react'
import axios from 'axios'

type Result = {
  doc_id: string
  confidence: number
  mapped: any
  evaluation?: { accuracy: number, rationale: string }
}

export default function App(){
  const [file, setFile] = useState<File | null>(null)
  const [docId, setDocId] = useState<string | null>(null)
  const [results, setResults] = useState<Result | null>(null)
  const [history, setHistory] = useState<Result[]>([])
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)

  const upload = async () =>{
    if(!file) return;
    setUploading(true)
    setProgress(10)
    const fd = new FormData()
    fd.append('file', file)
    try{
      const res = await axios.post('/api/ingest', fd, { headers: {'Content-Type': 'multipart/form-data', 'x-api-key': (import.meta.env.VITE_API_KEY || 'dev-key')} })
      setDocId(res.data.doc_id)
      setProgress(40)
      fetchResult(res.data.doc_id)
      setProgress(80)
      await fetchHistory()
      setProgress(100)
      setTimeout(()=> setProgress(0), 500)
    }catch(e){
      console.error(e)
    }finally{
      setUploading(false)
    }
  }

  const fetchResult = async (id: string) =>{
    try{
      const res = await axios.get(`/api/results/${id}`, { headers: {'x-api-key': (import.meta.env.VITE_API_KEY || 'dev-key')} })
      setResults(res.data)
    }catch(e){
      // not ready yet
    }
  }

  const fetchHistory = async ()=>{
    const res = await axios.get('/api/results', { headers: {'x-api-key': (import.meta.env.VITE_API_KEY || 'dev-key')} })
    setHistory(res.data || [])
  }

  useEffect(()=>{ fetchHistory() }, [])

  return (
    <div className="container p-8">
      <header className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-semibold">Content Processing POC</h1>
          <p className="text-sm text-gray-300 mt-1">Upload documents and inspect AI-extracted structured data with confidence and evaluation.</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-sm text-gray-300">Connected: <span className="text-white font-medium">Local Dev</span></div>
          <button className="px-4 py-2 rounded bg-white bg-opacity-6 border border-white/6 text-white text-sm">Help</button>
        </div>
      </header>

      <main className="grid grid-cols-3 gap-6">
        <section className="col-span-2 app-card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-medium">Upload Document</h2>
            <div className="text-sm text-gray-300">Tip: Use clear invoices or receipts for best extraction</div>
          </div>

          <div className="dropzone p-6 flex items-center justify-between">
            <div>
              <div className="text-gray-300">Drag & drop or select a file</div>
              <div className="mt-2 text-sm text-gray-400">Supported: PDF, PNG, JPG</div>
            </div>

            <div className="flex items-center gap-3">
              <input id="file-input" type="file" className="hidden" onChange={(e)=> setFile(e.target.files ? e.target.files[0] : null)} />
              <label htmlFor="file-input" className="px-4 py-2 rounded bg-violet-600 hover:bg-violet-700 text-white text-sm">Choose File</label>
              <button onClick={upload} disabled={uploading || !file} className="px-4 py-2 rounded bg-white bg-opacity-8 text-white text-sm">{uploading ? 'Uploading...' : 'Upload'}</button>
            </div>
          </div>

          {progress > 0 && (
            <div className="mt-4">
              <div className="progress-bar"><i style={{width: `${progress}%`}} /></div>
            </div>
          )}

          {results && (
            <div className="mt-6">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Latest Result</h3>
                <div className="text-sm text-gray-300">Confidence: <span className="font-medium text-white">{(results.confidence * 100).toFixed(0)}%</span></div>
              </div>

              <div className="mt-3 grid grid-cols-2 gap-4">
                <div className="p-4 app-card">
                  <h4 className="text-sm text-gray-300">Structured Data</h4>
                  <pre className="mt-2 text-sm bg-transparent p-0 overflow-auto">{JSON.stringify(results.mapped, null, 2)}</pre>
                </div>

                <div className="p-4 app-card">
                  <h4 className="text-sm text-gray-300">Evaluation</h4>
                  {results.evaluation ? (
                    <div className="mt-2">
                      <div className="text-4xl font-bold" style={{color: 'white'}}>{results.evaluation.accuracy}%</div>
                      <div className="text-sm text-gray-300 mt-2">{results.evaluation.rationale}</div>
                    </div>
                  ) : (
                    <div className="text-sm text-gray-400 mt-2">Evaluation not available yet</div>
                  )}
                </div>
              </div>
            </div>
          )}

        </section>

        <aside className="app-card p-4">
          <h3 className="text-lg font-medium mb-3">History</h3>
          <div className="space-y-3 max-h-[60vh] overflow-auto">
            {history.map(h=> (
              <div key={h.doc_id} className="p-3 border rounded flex items-center justify-between hover:bg-white/2">
                <div>
                  <div className="text-sm text-gray-300">{h.doc_id}</div>
                  <div className="text-xs text-gray-400">Confidence: {(h.confidence * 100).toFixed(0)}%</div>
                </div>
                <div>
                  {h.evaluation ? <div className="text-xs font-medium">{h.evaluation.accuracy}%</div> : <div className="text-xs text-gray-400">Pending</div>}
                </div>
              </div>
            ))}
          </div>
        </aside>
      </main>

      <footer className="mt-8 text-center text-xs text-gray-400">Built with ❤️ — Content Processing POC</footer>
    </div>
  )
}
