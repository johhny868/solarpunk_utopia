-- Migration 009: Add Resource Criticality (GAP-64: Battery Warlord Detection)
-- Philosophical foundation: Mikhail Bakunin
-- "Where there is authority, there is no freedom"

-- Add criticality tracking to resource specs
ALTER TABLE resource_specs ADD COLUMN critical BOOLEAN DEFAULT FALSE;

-- Reason why this resource is critical
ALTER TABLE resource_specs ADD COLUMN criticality_reason TEXT;

-- Category for grouping critical resources
-- Categories: 'power', 'water', 'medical', 'communication', 'food', 'shelter', 'skills'
ALTER TABLE resource_specs ADD COLUMN criticality_category TEXT;

-- Create index for efficient querying of critical resources
CREATE INDEX IF NOT EXISTS idx_resource_specs_critical ON resource_specs(critical) WHERE critical = TRUE;

-- Create index for querying by criticality category
CREATE INDEX IF NOT EXISTS idx_resource_specs_criticality_category ON resource_specs(criticality_category)
WHERE criticality_category IS NOT NULL;
