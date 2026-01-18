-- Symbols table definition v2 (Fix: name as Primary Key)

-- 1. Drop existing table if exists
DROP TABLE IF EXISTS public.symbols;

-- 2. Create table with new schema
CREATE TABLE public.symbols (
    name TEXT PRIMARY KEY,   -- Changed: 'name' is now the Primary Key (Immutable Identifier)
    symbol TEXT,             -- Changed: 'symbol' is just an attribute (Mutable)
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

-- 3. Create indexes
CREATE INDEX IF NOT EXISTS idx_symbols_category ON public.symbols(category);
CREATE INDEX IF NOT EXISTS idx_symbols_group_id ON public.symbols(group_id);
-- Index on symbol might be useful for lookups even if not unique
CREATE INDEX IF NOT EXISTS idx_symbols_symbol ON public.symbols(symbol);


