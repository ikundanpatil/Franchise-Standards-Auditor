-- ===========================================================================
-- FranchiseGuard AI — seed data for a fresh database created by schema.sql.
--
--   psql "$DATABASE_URL" -f schema.sql
--   psql "$DATABASE_URL" -f seed.sql
--
-- Idempotent: every row has a fixed UUID and uses ON CONFLICT DO NOTHING, so
-- re-running is harmless. Passwords: admin = "Admin12345!", everyone else =
-- "Demo1234!" (bcrypt hashes below).
--
-- Focus: 10 sample stores across Mumbai, Pune and Nashik, plus the users they
-- reference and a small set of inspections / violations / complaints / reports
-- so every table is exercised.
-- ===========================================================================

begin;

-- --- users ---------------------------------------------------------------
insert into users (id, email, hashed_password, full_name, role, region, phone) values
  ('11111111-1111-1111-1111-111111111111', 'admin@franchiseguard.ai',
   '$2b$12$fxKbVtf0EZB6G5.D.Oy1c.FVx/4BlzfIZoxyvSMlt300.hxvD3NmO',
   'FranchiseGuard Admin', 'admin', null, null),
  ('22222222-2222-2222-2222-222222222222', 'priya.nair@franchiseguard.ai',
   '$2b$12$uqoI2UiupiCctti.EyVG6uHsTkiv.27Wl5LyZ6N3P9QUz8PcUomza',
   'Priya Nair', 'area_manager', 'Mumbai', '+91 98200 11111'),
  ('33333333-3333-3333-3333-333333333333', 'rohan.deshpande@franchiseguard.ai',
   '$2b$12$uqoI2UiupiCctti.EyVG6uHsTkiv.27Wl5LyZ6N3P9QUz8PcUomza',
   'Rohan Deshpande', 'area_manager', 'Pune', '+91 98220 22222'),
  ('44444444-4444-4444-4444-444444444444', 'imran.shaikh@franchiseguard.ai',
   '$2b$12$uqoI2UiupiCctti.EyVG6uHsTkiv.27Wl5LyZ6N3P9QUz8PcUomza',
   'Imran Shaikh', 'inspector', 'Maharashtra', '+91 90000 33333'),
  ('55555555-5555-5555-5555-555555555555', 'meera.kulkarni@franchiseguard.ai',
   '$2b$12$uqoI2UiupiCctti.EyVG6uHsTkiv.27Wl5LyZ6N3P9QUz8PcUomza',
   'Meera Kulkarni', 'franchise_owner', 'Maharashtra', '+91 91111 44444')
on conflict (id) do nothing;

-- --- stores : 10 across Mumbai / Pune / Nashik --------------------------
insert into stores
  (id, code, name, brand, region, address, city, country, latitude, longitude,
   status, risk_level, compliance_score, open_violation_count, opened_on,
   next_inspection_due, manager_id, owner_id, tags)
values
  ('10000000-0000-0000-0000-000000000001', 'MUM-01', 'StarBrew Cafe', 'FranchiseGuard',
   'Mumbai', 'Linking Road, Bandra West', 'Mumbai', 'IN', 19.0596, 72.8295,
   'active', 'low', 94, 0, date '2022-03-14', current_date + 21,
   '22222222-2222-2222-2222-222222222222', null, '["Flagship","Drive-thru"]'::jsonb),
  ('10000000-0000-0000-0000-000000000002', 'MUM-02', 'Pizza Planet', 'FranchiseGuard',
   'Mumbai', 'Chakala, Andheri East', 'Mumbai', 'IN', 19.1136, 72.8697,
   'active', 'high', 66, 4, date '2021-08-02', current_date + 3,
   '22222222-2222-2222-2222-222222222222', '55555555-5555-5555-5555-555555555555',
   '["Watch list","High footfall"]'::jsonb),
  ('10000000-0000-0000-0000-000000000003', 'MUM-03', 'FreshBowl Kitchen', 'FranchiseGuard',
   'Mumbai', 'Senapati Bapat Marg, Lower Parel', 'Mumbai', 'IN', 18.9975, 72.8300,
   'active', 'medium', 80, 2, date '2023-01-19', current_date + 10,
   '22222222-2222-2222-2222-222222222222', null, '["Mall unit"]'::jsonb),
  ('10000000-0000-0000-0000-000000000004', 'MUM-04', 'Burger Hub', 'FranchiseGuard',
   'Mumbai', 'Hiranandani Gardens, Powai', 'Mumbai', 'IN', 19.1176, 72.9060,
   'active', 'critical', 58, 6, date '2020-11-05', current_date + 1,
   '22222222-2222-2222-2222-222222222222', null, '["Escalated","24/7"]'::jsonb),
  ('10000000-0000-0000-0000-000000000005', 'PUN-01', 'Urban Coffee', 'FranchiseGuard',
   'Pune', 'North Main Road, Koregaon Park', 'Pune', 'IN', 18.5362, 73.8931,
   'active', 'low', 91, 1, date '2022-06-30', current_date + 18,
   '33333333-3333-3333-3333-333333333333', null, '["Kiosk"]'::jsonb),
  ('10000000-0000-0000-0000-000000000006', 'PUN-02', 'Green Fork Deli', 'FranchiseGuard',
   'Pune', 'Baner Road, Baner', 'Pune', 'IN', 18.5590, 73.7868,
   'active', 'medium', 83, 3, date '2023-02-11', current_date + 12,
   '33333333-3333-3333-3333-333333333333', null, '["Seasonal patio"]'::jsonb),
  ('10000000-0000-0000-0000-000000000007', 'PUN-03', 'Noodle Bar 9', 'FranchiseGuard',
   'Pune', 'Nagar Road, Viman Nagar', 'Pune', 'IN', 18.5679, 73.9143,
   'active', 'low', 88, 1, date '2022-09-08', current_date + 16,
   '33333333-3333-3333-3333-333333333333', null, '["Late night"]'::jsonb),
  ('10000000-0000-0000-0000-000000000008', 'PUN-04', 'The Roasted Bean', 'FranchiseGuard',
   'Pune', 'Phase 1, Hinjewadi', 'Pune', 'IN', 18.5912, 73.7389,
   'active', 'high', 72, 4, date '2023-05-22', current_date + 4,
   '33333333-3333-3333-3333-333333333333', '55555555-5555-5555-5555-555555555555',
   '["New franchisee"]'::jsonb),
  ('10000000-0000-0000-0000-000000000009', 'NSK-01', 'Taco Junction', 'FranchiseGuard',
   'Nashik', 'College Road, Nashik', 'Nashik', 'IN', 20.0110, 73.7690,
   'active', 'low', 90, 0, date '2022-12-01', current_date + 15,
   '22222222-2222-2222-2222-222222222222', null, '["Drive-thru"]'::jsonb),
  ('10000000-0000-0000-0000-000000000010', 'NSK-02', 'Grill House 12', 'FranchiseGuard',
   'Nashik', 'Gangapur Road, Nashik', 'Nashik', 'IN', 19.9975, 73.7539,
   'active', 'medium', 76, 4, date '2023-03-27', current_date + 6,
   '22222222-2222-2222-2222-222222222222', null, '["Waterfront"]'::jsonb)
on conflict (id) do nothing;

-- --- inspections : one per riskier store -------------------------------
insert into inspections
  (id, store_id, inspector_id, status, method, source, scheduled_for, started_at,
   completed_at, checklist, image_label, frame_count, risk_score, risk_level,
   compliance_score, summary, model_version)
values
  ('20000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000002',
   '44444444-4444-4444-4444-444444444444', 'completed', 'ai_photo', 'scheduled',
   now() - interval '2 days', now() - interval '2 days',
   now() - interval '2 days' + interval '20 minutes',
   '[{"area":"Kitchen Cleanliness","ok":true},{"area":"Staff Hygiene","ok":false,"note":"Gloves not worn on the line"},{"area":"Food Storage","ok":false,"note":"Open trays on the counter"},{"area":"Branding Compliance","ok":true},{"area":"Pest Control","ok":true}]'::jsonb,
   'Kitchen line - station 2', 2, 68, 'high', 32,
   'Two staff-hygiene findings and an open-storage finding at Pizza Planet. Correct this week.',
   'fg-vision-2.4'),
  ('20000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000004',
   '44444444-4444-4444-4444-444444444444', 'completed', 'ai_photo', 'complaint_followup',
   now() - interval '1 day', now() - interval '1 day',
   now() - interval '1 day' + interval '25 minutes',
   '[{"area":"Kitchen Cleanliness","ok":false,"note":"Standing water near fryer"},{"area":"Staff Hygiene","ok":false},{"area":"Food Storage","ok":false,"note":"Cold well reading 9C"},{"area":"Branding Compliance","ok":true},{"area":"Pest Control","ok":false,"note":"Gap under rear door"}]'::jsonb,
   'Prep line + cold well', 3, 84, 'critical', 16,
   'Four findings including a critical cold-hold breach at Burger Hub. Manager intervention required today.',
   'fg-vision-2.4'),
  ('20000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000008',
   '44444444-4444-4444-4444-444444444444', 'in_progress', 'ai_photo', 'scheduled',
   now() - interval '4 hours', now() - interval '4 hours', null,
   '[{"area":"Kitchen Cleanliness","ok":true},{"area":"Staff Hygiene","ok":true},{"area":"Food Storage","ok":true},{"area":"Branding Compliance","ok":false,"note":"Old logo on menu board"},{"area":"Pest Control","ok":true}]'::jsonb,
   'Front of house', 1, null, null, null, null, null),
  ('20000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000010',
   '44444444-4444-4444-4444-444444444444', 'scheduled', 'on_site', 'scheduled',
   now() + interval '6 days', null, null, '[]'::jsonb, null, 1, null, null, null, null, null)
on conflict (id) do nothing;

-- --- violations -------------------------------------------------------
insert into violations
  (id, inspection_id, store_id, type_code, label, category, severity, status,
   confidence, bounding_box, standard_ref, explanation, remediation, detected_at, due_at)
values
  ('30000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000001',
   '10000000-0000-0000-0000-000000000002', 'v-gloves', 'Missing Gloves', 'Staff Hygiene',
   'critical', 'in_remediation', 0.93, '[0.52,0.28,0.22,0.26]'::jsonb,
   'BSM 4.2 - Hand protection during RTE prep',
   'Bare hands detected in the food-prep zone with no visible glove line.',
   'Re-brief shift on glove policy; place dispensers at every prep station.',
   now() - interval '2 days', now() + interval '2 days'),
  ('30000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000001',
   '10000000-0000-0000-0000-000000000002', 'v-uncovered', 'Food Left Uncovered', 'Food Storage',
   'major', 'open', 0.87, '[0.28,0.34,0.24,0.20]'::jsonb,
   'BSM 3.2 - Product protection when not in service',
   'Open tray of prepared product on the counter with no lid and no active service.',
   'Cover and return to chilled storage; retrain on holding rules.',
   now() - interval '2 days', now() + interval '5 days'),
  ('30000000-0000-0000-0000-000000000003', '20000000-0000-0000-0000-000000000001',
   '10000000-0000-0000-0000-000000000002', 'v-waste', 'Overflowing Waste Bin', 'Kitchen Cleanliness',
   'minor', 'resolved', 0.71, '[0.12,0.44,0.16,0.30]'::jsonb,
   'BSM 2.4 - Waste stored in lidded containers',
   'Open bin past the fill line beside the prep bench.',
   'Empty now; add a lidded bin and a mid-shift empty step.',
   now() - interval '2 days', now() - interval '1 day'),
  ('30000000-0000-0000-0000-000000000004', '20000000-0000-0000-0000-000000000002',
   '10000000-0000-0000-0000-000000000004', 'v-temp', 'Cold-Hold Above Range', 'Food Storage',
   'critical', 'open', 0.95, '[0.42,0.50,0.20,0.24]'::jsonb,
   'BSM 3.1 - Cold holding 5C or below',
   'Display unit thermometer reads 9C against a 0-5C standard; condensation on the glass.',
   'Move stock to a working unit; call refrigeration; record corrective action.',
   now() - interval '1 day', now() + interval '1 day'),
  ('30000000-0000-0000-0000-000000000005', '20000000-0000-0000-0000-000000000002',
   '10000000-0000-0000-0000-000000000004', 'v-floor', 'Dirty Kitchen Floor', 'Kitchen Cleanliness',
   'major', 'in_remediation', 0.88, '[0.08,0.66,0.44,0.28]'::jsonb,
   'BSM 2.1 - Floors clean, dry, unobstructed',
   'Standing liquid and debris across the line-side floor near the fryer.',
   'Immediate spot-clean; add mid-shift floor check to the cleaning rota.',
   now() - interval '1 day', now() + interval '3 days'),
  ('30000000-0000-0000-0000-000000000006', '20000000-0000-0000-0000-000000000002',
   '10000000-0000-0000-0000-000000000004', 'v-pest', 'Pest Entry Point', 'Pest Control',
   'major', 'open', 0.82, '[0.82,0.72,0.14,0.20]'::jsonb,
   'BSM 6.3 - Proofing of external openings',
   'Gap under the rear door with no brush seal; daylight visible along the threshold.',
   'Fit a brush strip; log with the pest contractor on next visit.',
   now() - interval '1 day', now() + interval '4 days'),
  ('30000000-0000-0000-0000-000000000007', '20000000-0000-0000-0000-000000000002',
   '10000000-0000-0000-0000-000000000004', 'v-handwash', 'Handwash Sink Blocked', 'Staff Hygiene',
   'major', 'open', 0.79, '[0.74,0.40,0.20,0.34]'::jsonb,
   'BSM 4.1 - Handwash stations kept clear',
   'Dedicated handwash basin stacked with utensils, reducing access during service.',
   'Clear the basin; mark it hands-only with fresh signage.',
   now() - interval '1 day', now() + interval '2 days'),
  ('30000000-0000-0000-0000-000000000008', '20000000-0000-0000-0000-000000000003',
   '10000000-0000-0000-0000-000000000008', 'v-signage', 'Non-compliant Signage', 'Branding Compliance',
   'minor', 'open', 0.68, '[0.05,0.06,0.30,0.16]'::jsonb,
   'BRAND 1.1 - Approved signage & lockups',
   'Menu board uses a superseded logo lockup and off-palette colour vs. the current brand kit.',
   'Order the current board pack; remove legacy artwork within 14 days.',
   now() - interval '4 hours', now() + interval '14 days')
on conflict (id) do nothing;

-- resolve one finding so "resolved vs unresolved" charts have data
update violations
   set status = 'resolved', resolved_at = now() - interval '1 day',
       resolved_by_id = '22222222-2222-2222-2222-222222222222',
       resolution_note = 'Lidded bin installed; mid-shift empty added to the rota.'
 where id = '30000000-0000-0000-0000-000000000003' and status <> 'resolved';

-- --- complaints -------------------------------------------------------
insert into complaints
  (id, store_id, channel, status, severity, reporter_name, reporter_contact, subject,
   body, received_at, tags)
values
  ('40000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000002',
   'app', 'triaged', 'major', 'Anonymous', null, 'Staff not wearing gloves',
   'Watched two staff assemble pizzas bare-handed at the Andheri outlet during lunch rush.',
   now() - interval '3 days', '["hygiene"]'::jsonb),
  ('40000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000004',
   'phone', 'investigating', 'critical', 'R. Mehta', '+91 99999 88888', 'Cold food served',
   'Ordered a cold-cuts sub at Powai; the filling was warm and tasted off. Felt unwell after.',
   now() - interval '2 days', '["food-safety","illness"]'::jsonb),
  ('40000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000006',
   'email', 'new', 'minor', 'S. Kulkarni', 's.kulkarni@example.com', 'Long wait times',
   'Baner store took 25 minutes for a takeaway order on a weekday evening.',
   now() - interval '1 day', '["service"]'::jsonb),
  ('40000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000010',
   'walk_in', 'resolved', 'minor', 'Manager log', null, 'Restroom cleanliness',
   'Customer flagged an untidy restroom at the Gangapur Road outlet mid-afternoon.',
   now() - interval '6 days', '["facilities"]'::jsonb)
on conflict (id) do nothing;

update complaints
   set triaged_by_id = '22222222-2222-2222-2222-222222222222',
       triaged_at = received_at + interval '2 hours'
 where id in ('40000000-0000-0000-0000-000000000001','40000000-0000-0000-0000-000000000002')
   and triaged_by_id is null;

update complaints
   set resolved_at = now() - interval '5 days',
       resolution_note = 'Cleaning rota tightened; spot-checks added.'
 where id = '40000000-0000-0000-0000-000000000004' and resolved_at is null;

-- --- reports : one per completed inspection ---------------------------
insert into reports
  (id, inspection_id, store_id, reference, status, risk_score, risk_level, grade,
   minor_count, major_count, critical_count, summary, recommendations, timeline,
   evidence, inspector_name, model_version, generated_by_id, generated_at)
values
  ('50000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000001',
   '10000000-0000-0000-0000-000000000002', 'FG-REP-MUM02A', 'final', 68, 'high', 'D',
   1, 1, 1,
   'Pizza Planet (MUM-02) returned three findings spanning Staff Hygiene and Food Storage. The most significant is a missing-gloves detection at 93% confidence. Corrective actions should close within the week.',
   '[{"id":"rec-1","title":"Re-brief the shift on glove policy","detail":"Missing Gloves - BSM 4.2. Place dispensers at every prep station.","priority":"now","owner":"Store Manager"},{"id":"rec-2","title":"Cover open product immediately","detail":"Food Left Uncovered - BSM 3.2. Retrain on holding rules.","priority":"soon","owner":"Shift Lead"}]'::jsonb,
   '[{"id":"t-1","time":"T-0","title":"Evidence uploaded","detail":"2 frames from the kitchen line.","tone":"info"},{"id":"t-2","time":"+18s","title":"Vision model completed","detail":"3 findings - model fg-vision-2.4.","tone":"violet"},{"id":"t-3","time":"+34s","title":"Compliance report generated","detail":"Ready to share with the franchisee.","tone":"good"}]'::jsonb,
   '[{"id":"ev-1","label":"Missing Gloves","severity":"critical","tags":["Staff Hygiene","93%"]},{"id":"ev-2","label":"Food Left Uncovered","severity":"major","tags":["Food Storage","87%"]}]'::jsonb,
   'Imran Shaikh', 'fg-vision-2.4', '22222222-2222-2222-2222-222222222222',
   now() - interval '2 days' + interval '35 minutes'),
  ('50000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000002',
   '10000000-0000-0000-0000-000000000004', 'FG-REP-MUM04A', 'final', 84, 'critical', 'F',
   0, 3, 1,
   'Burger Hub (MUM-04) is in the severe band with four findings, including a critical cold-hold breach at 95% confidence. Manager intervention is required today and a 72-hour re-inspection is advised.',
   '[{"id":"rec-1","title":"Move stock off the failed cold well now","detail":"Cold-Hold Above Range - BSM 3.1. Call refrigeration; record corrective action.","priority":"now","owner":"Store Manager"},{"id":"rec-2","title":"Spot-clean the line-side floor","detail":"Dirty Kitchen Floor - BSM 2.1. Add a mid-shift floor check.","priority":"soon","owner":"Shift Lead"},{"id":"rec-3","title":"Book a 72-hour re-inspection","detail":"Confirm the critical items are closed with an AI photo re-check.","priority":"now","owner":"Area Manager"}]'::jsonb,
   '[{"id":"t-1","time":"T-0","title":"Evidence uploaded","detail":"3 frames from the prep line and cold well.","tone":"info"},{"id":"t-2","time":"+18s","title":"Vision model completed","detail":"4 findings - model fg-vision-2.4.","tone":"violet"},{"id":"t-3","time":"+20s","title":"Critical alert raised","detail":"Pushed to the store manager and the Area Manager queue.","tone":"risk"},{"id":"t-4","time":"+34s","title":"Compliance report generated","detail":"Ready to download or share.","tone":"good"}]'::jsonb,
   '[{"id":"ev-1","label":"Cold-Hold Above Range","severity":"critical","tags":["Food Storage","95%"]},{"id":"ev-2","label":"Dirty Kitchen Floor","severity":"major","tags":["Kitchen Cleanliness","88%"]},{"id":"ev-3","label":"Pest Entry Point","severity":"major","tags":["Pest Control","82%"]}]'::jsonb,
   'Imran Shaikh', 'fg-vision-2.4', '22222222-2222-2222-2222-222222222222',
   now() - interval '1 day' + interval '40 minutes')
on conflict (id) do nothing;

-- keep the denormalised store counters honest
update stores s
   set open_violation_count = (
     select count(*) from violations v
      where v.store_id = s.id and v.status in ('open','in_remediation')
   );

commit;

-- Quick check:
--   select region, count(*) from stores group by region order by region;
--   select code, name, risk_level, compliance_score, open_violation_count from stores order by code;
