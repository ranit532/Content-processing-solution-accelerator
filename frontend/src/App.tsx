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

  const upload = async () =>{
    if(!file) return;
    const fd = new FormData()
    fd.append('file', file)
    const res = await axios.post('/api/ingest', fd, { headers: {'Content-Type': 'multipart/form-data', 'x-api-key': (import.meta.env.VITE_API_KEY || 'dev-key')} })
    setDocId(res.data.doc_id)
    fetchResult(res.data.doc_id)
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
    <div className="p-6">
      <h1 className="text-2xl font-bold">Content Processing POC</h1>
      <div className="mt-4">
        <input type="file" onChange={(e)=> setFile(e.target.files ? e.target.files[0] : null)} />
        <button onClick={upload} className="ml-2 bg-blue-600 text-white px-4 py-2 rounded">Upload</button>
      </div>

      {docId && <div className="mt-4">Uploaded: {docId}</div>}

      {results && (
        <div className="mt-6 border p-4">
          <h2 className="font-semibold">Results</h2>
          <div>Confidence: {results.confidence}</div>
          {results.evaluation && (
            <div>Accuracy: {results.evaluation.accuracy}% - {results.evaluation.rationale}</div>
          )}
          <pre className="mt-2 bg-gray-100 p-2 rounded">{JSON.stringify(results.mapped, null, 2)}</pre>
        </div>
      )}

      <div className="mt-6">
        <h2 className="font-semibold">History</h2>
        <ul>
          {history.map(h=> (
            <li key={h.doc_id} className="border p-2 mt-2">
              <div className="flex justify-between"><div>{h.doc_id}</div><div>{h.confidence}</div></div>
              {h.evaluation && <div>Accuracy: {h.evaluation.accuracy}%</div>}
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
