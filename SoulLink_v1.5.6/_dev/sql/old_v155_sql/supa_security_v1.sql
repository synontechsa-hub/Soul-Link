-- SoulLink Arise v1.5.4: Supabase Security Lockdown SQL
-- This script enables RLS and defines policies for core tables.

-- 1. USERS TABLE
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own profile" 
ON public.users FOR SELECT 
USING (auth.uid()::text = user_id);

CREATE POLICY "Users can update their own profile" 
ON public.users FOR UPDATE 
USING (auth.uid()::text = user_id)
WITH CHECK (auth.uid()::text = user_id);

-- 2. SOULS TABLE (Public Read, Protected Write)
ALTER TABLE public.souls ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view souls" 
ON public.souls FOR SELECT 
USING (true);

-- 3. LOCATIONS TABLE (Public Read, Protected Write)
ALTER TABLE public.locations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view locations" 
ON public.locations FOR SELECT 
USING (true);

-- 4. USER_SOUL_RELATIONSHIPS TABLE (Data Isolation)
ALTER TABLE public.user_soul_relationships ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own relationships" 
ON public.user_soul_relationships FOR SELECT 
USING (auth.uid()::text = user_id);

CREATE POLICY "Users can create their own relationships" 
ON public.user_soul_relationships FOR INSERT 
WITH CHECK (auth.uid()::text = user_id);

CREATE POLICY "Users can update their own relationships" 
ON public.user_soul_relationships FOR UPDATE 
USING (auth.uid()::text = user_id)
WITH CHECK (auth.uid()::text = user_id);

-- 5. CONVERSATIONS TABLE (Chat Isolation)
ALTER TABLE public.conversations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own conversations" 
ON public.conversations FOR SELECT 
USING (auth.uid()::text = user_id);

CREATE POLICY "Users can insert their own messages" 
ON public.conversations FOR INSERT 
WITH CHECK (auth.uid()::text = user_id);

-- 6. ARCHITECT "GOD-MODE" OVERRIDES
-- These allow the Architect (via custom claim) to bypass RLS for maintenance.

CREATE POLICY "Architect bypass for users" 
ON public.users FOR ALL TO authenticated 
USING ((auth.jwt() -> 'app_metadata' ->> 'role') = 'architect');

CREATE POLICY "Architect bypass for souls" 
ON public.souls FOR ALL TO authenticated 
USING ((auth.jwt() -> 'app_metadata' ->> 'role') = 'architect');

CREATE POLICY "Architect bypass for locations" 
ON public.locations FOR ALL TO authenticated 
USING ((auth.jwt() -> 'app_metadata' ->> 'role') = 'architect');

CREATE POLICY "Architect bypass for relationships" 
ON public.user_soul_relationships FOR ALL TO authenticated 
USING ((auth.jwt() -> 'app_metadata' ->> 'role') = 'architect');

CREATE POLICY "Architect bypass for conversations" 
ON public.conversations FOR ALL TO authenticated 
USING ((auth.jwt() -> 'app_metadata' ->> 'role') = 'architect');
