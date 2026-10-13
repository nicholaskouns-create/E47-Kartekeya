-- Execute only after the Observatory route has been published and verified.
-- Additive registration only; no policies, scopes, or schema changes.
BEGIN;
SELECT pg_advisory_xact_lock(hashtext('CITY-OBSERVATORY-1.0'));
UPDATE public.city_interactive_surfaces
SET title = 'Mathematical City Observatory',
    route = 'https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/observatory/',
    active = true,
    updated_at = now()
WHERE surface_code = 'CITY-OBSERVATORY-1.0';
INSERT INTO public.city_interactive_surfaces
  (surface_code, title, surface_type, route, lay_guide, egghead_reference,
   noise_profile, recursive_generation_enabled, active)
SELECT 'CITY-OBSERVATORY-1.0', 'Mathematical City Observatory', template.surface_type,
  'https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/observatory/',
  '{"what":"Explore existing instruments, compare experiments, and inspect scope boundaries."}'::jsonb,
  '{"evidence_boundary":"Static public navigation and replay interface; no privileged database access."}'::jsonb,
  template.noise_profile, false, true
FROM (SELECT surface_type, noise_profile FROM public.city_interactive_surfaces WHERE active = true ORDER BY created_at LIMIT 1) template
WHERE NOT EXISTS (
  SELECT 1 FROM public.city_interactive_surfaces WHERE surface_code = 'CITY-OBSERVATORY-1.0'
);
COMMIT;
-- Verify registration:
SELECT surface_code, title, route, active FROM public.city_interactive_surfaces
WHERE surface_code = 'CITY-OBSERVATORY-1.0';
