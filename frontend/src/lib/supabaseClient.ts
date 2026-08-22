import { createClient, SupabaseClient } from '@supabase/supabase-js'

const rawUrl = (import.meta.env.VITE_SUPABASE_URL as string) || 'https://sarvaflow-demo.supabase.co'
// Sanitize URL: strip accidental /rest/v1, /rest/v1/, or trailing slashes copied from Supabase API settings
const supabaseUrl = rawUrl.replace(/\/rest\/v1\/?$/, '').replace(/\/+$/, '')
const supabaseAnonKey = (import.meta.env.VITE_SUPABASE_ANON_KEY as string) || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.dummy_anon_key'

export const supabase: SupabaseClient = createClient(supabaseUrl, supabaseAnonKey)

