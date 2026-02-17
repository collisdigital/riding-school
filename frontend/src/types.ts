export interface User {
  id: string
  first_name: string
  last_name: string
  email: string | null
}

export interface RiderResponse {
  id: string // RiderProfile ID
  user_id: string
  first_name: string
  last_name: string
  email: string | null
  height_cm: number | null
  weight_kg: number | null
  date_of_birth: string | null // ISO Date (YYYY-MM-DD)
  school_id: string
}

export interface RiderCreate {
  first_name: string
  last_name: string
  email?: string
  height_cm?: number
  weight_kg?: number
  date_of_birth?: string
}

export interface RiderUpdate {
  first_name?: string
  last_name?: string
  email?: string
  height_cm?: number
  weight_kg?: number
  date_of_birth?: string
}
