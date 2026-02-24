'use client'

import { useState, useEffect } from 'react'

export default function TestPage() {
  const [result, setResult] = useState<string>('init')
  
  useEffect(() => {
    console.log('UseEffect running')
    setResult('effect ran')
  }, [])
  
  return (
    <div className="p-8 bg-white">
      <h1 className="text-2xl font-bold mb-4">Test</h1>
      <p>Result: {result}</p>
    </div>
  )
}

