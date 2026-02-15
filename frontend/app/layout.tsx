import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'GhostScore - FICO Simulator & Optimizer',
  description: 'AI-powered FICO score simulator, optimizer, and credit strategy engine',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
