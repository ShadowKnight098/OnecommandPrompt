import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL || 'https://sohmmvanrnrnwwrjedan.supabase.co';
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNvaG1tdmFucm5ybnd3cmplZGFuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODgxNzU5OTAsImV4cCI6MjEwMzc1MTk5MH0.dT4PFLY87nJXD5wBktOr9SFgr22JyN6U5semogacU2o';

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
