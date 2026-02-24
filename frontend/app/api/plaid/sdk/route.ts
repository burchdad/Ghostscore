import { NextResponse } from 'next/server'

/**
 * Proxy endpoint for Plaid SDK
 * Fetches the Plaid Link SDK from CDN and serves it through the backend
 * This bypasses devcontainer network restrictions
 */
export async function GET() {
  try {
    // Try multiple CDN sources for the Plaid SDK
    const sdkUrls = [
      'https://cdn.plaid.com/link/v1/stable/link.js',
      'https://cdn.jsdelivr.net/gh/plaid/plaid-link/plaid-link.min.js',
    ]

    let lastError: Error | null = null

    for (const url of sdkUrls) {
      try {
        console.log(`[Plaid SDK Proxy] Fetching from: ${url}`)
        const response = await fetch(url, {
          headers: {
            'User-Agent': 'Mozilla/5.0 (Compatible; GhostScore/1.0)',
          },
        })

        if (response.ok) {
          const sdkContent = await response.text()
          console.log(`[Plaid SDK Proxy] ✓ Successfully fetched from ${url}`)

          // Return with appropriate headers
          return new NextResponse(sdkContent, {
            status: 200,
            headers: {
              'Content-Type': 'application/javascript; charset=utf-8',
              'Cache-Control': 'public, max-age=86400', // Cache for 24 hours
              'Access-Control-Allow-Origin': '*',
            },
          })
        }
      } catch (error) {
        console.warn(`[Plaid SDK Proxy] ✗ Failed from ${url}:`, error)
        lastError = error as Error
        continue
      }
    }

    // If all sources failed
    throw new Error(
      `Could not fetch Plaid SDK from any source. Last error: ${lastError?.message}`
    )
  } catch (error) {
    console.error('[Plaid SDK Proxy] Error:', error)
    return new NextResponse(
      JSON.stringify({
        error: 'Failed to load Plaid SDK',
        message: error instanceof Error ? error.message : 'Unknown error',
      }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    )
  }
}
