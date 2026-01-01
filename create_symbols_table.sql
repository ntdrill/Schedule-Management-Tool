-- Symbols table definition
CREATE TABLE IF NOT EXISTS public.symbols (
    symbol TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    category TEXT NOT NULL,  -- 'constant', 'variable', 'function', etc.
    group_id TEXT,           -- 'physical_constants', 'system_settings', etc.
    
    -- Type information or function signature
    signature JSONB DEFAULT '{}'::jsonb, -- { "inputs": [...], "outputs": [...], "args": [...] }
    
    -- Value information
    default_value JSONB,     -- Initial value or constant value
    unit TEXT,               -- Unit (e.g., 'min', 'W')
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Optional: Create an index on category or group_id for faster lookups if needed
CREATE INDEX IF NOT EXISTS idx_symbols_category ON public.symbols(category);
CREATE INDEX IF NOT EXISTS idx_symbols_group_id ON public.symbols(group_id);

