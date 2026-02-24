import { NextRequest, NextResponse } from 'next/server'

const PLAID_CLIENT_ID = process.env.PLAID_CLIENT_ID
const PLAID_SECRET = process.env.PLAID_SECRET
const PLAID_ENV = process.env.PLAID_ENV || 'sandbox'
const PLAID_API_VERSION = '2020-09-14'

// Plaid API base URL based on environment
const PLAID_BASE_URL = PLAID_ENV === 'production'
  ? 'https://api.plaid.com'
  : 'https://sandbox.plaid.com'

export async function POST(request: NextRequest) {
  try {
    if (!PLAID_CLIENT_ID || !PLAID_SECRET) {
      return NextResponse.json(
        { error: 'Plaid credentials not configured' },
        { status: 500 }
      )
    }

    const body = await request.json()
    const { profile_id, user_id } = body

    if (!profile_id || !user_id) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      )
    }

    // Create Plaid Link Token
    const response = await fetch(`${PLAID_BASE_URL}/link/token/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Plaid-Version': PLAID_API_VERSION,
      },
      body: JSON.stringify({
        client_id: PLAID_CLIENT_ID,
        secret: PLAID_SECRET,
        client_name: 'GhostScore',
        user: {
          client_user_id: user_id,
        },
        country_codes: ['US'],
        language: 'en',
        products: ['auth'], // Use 'auth' product to get account details
      }),
    })

    if (!response.ok) {
      const error = await response.json()
      console.error('Plaid error:', error)
      return NextResponse.json(error, { status: response.status })
    }

    const data = await response.json()
    return NextResponse.json({
      link_token: data.link_token,
      expiration: data.expiration,
    })
  } catch (error) {
    console.error('Error creating link token:', error)
    return NextResponse.json(
      { error: 'Failed to create link token' },
      { status: 500 }
    )
  }
}
