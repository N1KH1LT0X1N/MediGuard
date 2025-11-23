-- MediGuard AI Database Schema
-- Run this in Supabase SQL Editor or via migration script

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    preferences JSONB,
    metadata JSONB
);

-- Create predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source TEXT NOT NULL CHECK (source IN ('manual', 'pdf', 'csv', 'image')),
    input_features JSONB NOT NULL,
    prediction_result JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create hash_chain table
CREATE TABLE IF NOT EXISTS hash_chain (
    id SERIAL PRIMARY KEY,
    prediction_id TEXT NOT NULL REFERENCES predictions(id) ON DELETE CASCADE,
    previous_hash TEXT,
    current_hash TEXT NOT NULL UNIQUE,
    block_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    blockchain_tx_hash TEXT,
    blockchain_block_number BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_user_id ON predictions(user_id);
CREATE INDEX IF NOT EXISTS idx_predictions_timestamp ON predictions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_created_at ON predictions(created_at DESC);
-- Composite index for filtered queries (user_id + timestamp) - CRITICAL for dashboard performance
CREATE INDEX IF NOT EXISTS idx_predictions_user_timestamp ON predictions(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_hash_chain_prediction_id ON hash_chain(prediction_id);
CREATE INDEX IF NOT EXISTS idx_hash_chain_current_hash ON hash_chain(current_hash);
CREATE INDEX IF NOT EXISTS idx_hash_chain_previous_hash ON hash_chain(previous_hash);
CREATE INDEX IF NOT EXISTS idx_hash_chain_blockchain_tx_hash ON hash_chain(blockchain_tx_hash);

-- Create index on JSONB fields for efficient querying
CREATE INDEX IF NOT EXISTS idx_predictions_prediction_result ON predictions USING GIN (prediction_result);
CREATE INDEX IF NOT EXISTS idx_predictions_input_features ON predictions USING GIN (input_features);

