-- Fix missing columns_info in datasets
-- This migration adds columns_info to datasets that are missing them

UPDATE datasets 
SET columns_info = '[
  {"name": "date", "type": "datetime"},
  {"name": "value", "type": "numeric"}
]'::jsonb,
column_count = 2
WHERE (columns_info IS NULL OR columns_info = '[]'::jsonb)
AND (name ILIKE '%Banque Mondiale%' OR name ILIKE '%World Bank%');

UPDATE datasets 
SET columns_info = '[
  {"name": "date", "type": "datetime"},
  {"name": "region", "type": "string"},
  {"name": "temp", "type": "numeric"},
  {"name": "precip", "type": "numeric"},
  {"name": "humidity", "type": "numeric"},
  {"name": "wind", "type": "numeric"}
]'::jsonb,
column_count = 6
WHERE (columns_info IS NULL OR columns_info = '[]'::jsonb)
AND (name ILIKE '%NASA POWER%' OR name ILIKE '%Météo%');

UPDATE datasets 
SET columns_info = '[
  {"name": "year", "type": "integer"},
  {"name": "item", "type": "string"},
  {"name": "element", "type": "string"},
  {"name": "value", "type": "numeric"}
]'::jsonb,
column_count = 4
WHERE (columns_info IS NULL OR columns_info = '[]'::jsonb)
AND name ILIKE '%FAO%';
