-- Migration: Add integration_sync_status table
-- Version: 003
-- Description: Add table for tracking integration sync status

CREATE TABLE IF NOT EXISTS integration_sync_status (
    id SERIAL PRIMARY KEY,
    trigger_type VARCHAR(20) NOT NULL DEFAULT 'manual',
    provider_mode VARCHAR(20) NOT NULL DEFAULT 'mock',
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    finished_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) NOT NULL DEFAULT 'success',
    error_summary TEXT,
    inventory_count INTEGER NOT NULL DEFAULT 0,
    audit_count INTEGER NOT NULL DEFAULT 0,
    exception_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add check constraints
ALTER TABLE integration_sync_status ADD CONSTRAINT chk_trigger_type 
    CHECK (trigger_type IN ('manual', 'scheduled', 'api'));
ALTER TABLE integration_sync_status ADD CONSTRAINT chk_provider_mode 
    CHECK (provider_mode IN ('mock', 'real'));
ALTER TABLE integration_sync_status ADD CONSTRAINT chk_status 
    CHECK (status IN ('success', 'failed', 'partial'));

-- Create index for latest sync query
CREATE INDEX idx_integration_sync_status_started_at ON integration_sync_status(started_at DESC);
