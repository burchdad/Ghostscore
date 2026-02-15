'use client'

interface Account {
  id: string
  type: string
  name: string
  balance: number
  limit?: number
  status: string
}

interface AccountsListProps {
  accounts: Account[]
}

export default function AccountsList({ accounts }: AccountsListProps) {
  const getAccountTypeIcon = (type: string) => {
    switch (type) {
      case 'credit_card':
        return '💳'
      case 'loan':
        return '📄'
      case 'mortgage':
        return '🏠'
      case 'auto_loan':
        return '🚗'
      case 'student_loan':
        return '🎓'
      default:
        return '📋'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-900 text-green-200'
      case 'closed':
        return 'bg-slate-600 text-slate-300'
      case 'charged_off':
        return 'bg-red-900 text-red-200'
      default:
        return 'bg-slate-600 text-slate-300'
    }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {accounts.map((account) => (
        <div key={account.id} className="bg-slate-700 rounded-lg p-4 text-white">
          <div className="flex items-start justify-between mb-3">
            <div>
              <div className="text-2xl mb-2">{getAccountTypeIcon(account.type)}</div>
              <h4 className="font-semibold text-lg">{account.name}</h4>
              <p className="text-sm text-slate-400 capitalize">{account.type.replace('_', ' ')}</p>
            </div>
            <span className={`text-xs px-2 py-1 rounded ${getStatusColor(account.status)}`}>
              {account.status}
            </span>
          </div>

          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-slate-300">Balance</span>
              <span className="font-semibold">${account.balance.toFixed(2)}</span>
            </div>
            {account.limit && (
              <>
                <div className="flex justify-between">
                  <span className="text-slate-300">Limit</span>
                  <span className="font-semibold">${account.limit.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-300">Utilization</span>
                  <span className="font-semibold">
                    {account.limit > 0
                      ? ((account.balance / account.limit) * 100).toFixed(1)
                      : '0'}
                    %
                  </span>
                </div>
              </>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
