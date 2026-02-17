-- GhostScore Database Schema
-- PostgreSQL with Supabase

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    password TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Credit profiles table (each user can have multiple profiles for different scenarios)
CREATE TABLE IF NOT EXISTS credit_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Accounts table (credit cards, loans, mortgages, etc.)
CREATE TABLE IF NOT EXISTS accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES credit_profiles(id) ON DELETE CASCADE,
    type TEXT NOT NULL,  -- credit_card, loan, mortgage, auto_loan, student_loan, etc.
    name TEXT NOT NULL,
    balance NUMERIC(12, 2) NOT NULL DEFAULT 0,
    limit NUMERIC(12, 2),  -- Credit limit (NULL for non-revolving accounts)
    open_date DATE NOT NULL,
    status TEXT DEFAULT 'active',  -- active, closed, charged_off
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Derogatories table (late payments, collections, bankruptcies, etc.)
CREATE TABLE IF NOT EXISTS derogatories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES credit_profiles(id) ON DELETE CASCADE,
    type TEXT NOT NULL,  -- late_payment, collection, charge_off, bankruptcy, etc.
    date DATE NOT NULL,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Score history table (to track changes over time)
CREATE TABLE IF NOT EXISTS score_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES credit_profiles(id) ON DELETE CASCADE,
    score INTEGER NOT NULL,
    payment_history INTEGER,
    utilization INTEGER,
    age INTEGER,
    new_credit INTEGER,
    mix INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit log for tracking changes
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID REFERENCES credit_profiles(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Scenario history table (to track scenario runs and results)
CREATE TABLE IF NOT EXISTS scenario_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES credit_profiles(id) ON DELETE CASCADE,
    actions JSONB NOT NULL, -- List of actions taken (as JSON)
    original_score INTEGER NOT NULL,
    simulated_score INTEGER NOT NULL,
    actual_gain INTEGER,
    timeline JSONB, -- Week-by-week score timeline
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better query performance
CREATE INDEX idx_credit_profiles_user_id ON credit_profiles(user_id);
CREATE INDEX idx_accounts_profile_id ON accounts(profile_id);
CREATE INDEX idx_derogatories_profile_id ON derogatories(profile_id);
CREATE INDEX idx_score_history_profile_id ON score_history(profile_id);
CREATE INDEX idx_audit_log_profile_id ON audit_log(profile_id);
CREATE INDEX idx_scenario_history_profile_id ON scenario_history(profile_id);
