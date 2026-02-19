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

export interface Skill {
  id: string
  grade_id: string
  name: string
  description?: string
}

export interface Grade {
  id: string
  name: string
  description?: string
  sequence_order: number
  skills: Skill[]
}

export interface GradeCreate {
  name: string
  description?: string
}

export interface SkillCreate {
  name: string
  description?: string
}

export interface GradeReorder {
  ordered_ids: string[]
}
