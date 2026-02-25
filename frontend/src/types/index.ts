export interface User {
  id: number
  name: string
  role: 'dispatcher' | 'master'
}

export interface Request {
  id: number
  clientName: string
  phone: string
  address: string
  problemText: string
  status: 'new' | 'assigned' | 'in_progress' | 'done' | 'canceled'
  assignedTo: number | null
  createdAt: string
  updatedAt: string
}