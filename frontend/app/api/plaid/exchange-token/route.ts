import { NextRequest, NextResponse } from 'next/server'

const PLAID_CLIENT_ID = process.env.PLAID_CLIENT_ID
const PLAID_SECRET = process.env.PLAID_SECRET
const PLAID_ENV = process.env.PLAID_ENV || 'sandbox'
const PLAID_API_VERSION = '2020-09-14'

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
    const { public_token, profile_id } = body

    if (!public_token || !profile_id) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      )
    }

    // Step 1: Exchange public token for access token
    const exchangeResponse = await fetch(`${PLAID_BASE_URL}/item/public_token/exchange`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Plaid-Version': PLAID_API_VERSION,
      },
      body: JSON.stringify({
        client_id: PLAID_CLIENT_ID,
        secret: PLAID_SECRET,
        public_token: public_token,
      }),
    })

    if (!exchangeResponse.ok) {
      const error = await exchangeResponse.json()
      console.error('Plaid exchange error:', error)
      return NextResponse.json(error, { status: exchangeResponse.status })
    }

    const exchangeData = await exchangeResponse.json()
    const accessToken = exchangeData.access_token

    // Step 2: Get accounts using access token
    const accountsResponse = await fetch(`${PLAID_BASE_URL}/accounts/get`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Plaid-Version': PLAID_API_VERSION,
      },
      body: JSON.stringify({
        client_id: PLAID_CLIENT_ID,
        secret: PLAID_SECRET,
        access_token: accessToken,
      }),
    })

    if (!accountsResponse.ok) {
      const error = await accountsResponse.json()
      console.error('Plaid accounts error:', error)
      return NextResponse.json(error, { status: accountsResponse.status })
    }

    const accountsData = await accountsResponse.json()

    // Step 3: Format accounts for GhostScore
    const formattedAccounts = accountsData.accounts.map((account: any) => ({
      id: account.account_id,
      name: account.name,
      subtype: account.subtype,
      type: account.type,
      balances: account.balances,
      mask: account.mask, // Last 4 digits for display
      official_name: account.official_name,
    }))

    // TODO: Store access token securely for future sync (e.g., in database)
    // For now, just return the accounts

    return NextResponse.json({
      accounts: formattedAccounts,
      message: `Successfully imported ${formattedAccounts.length} account(s)`,
    })
  } catch (error) {
    console.error('Error exchanging token:', error)
    return NextResponse.json(
      { error: 'Failed to exchange token' },
      { status: 500 }
    )
  }
}
