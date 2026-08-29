-- ============================================================================
-- Discord Bot database schema (PostgreSQL / Supabase)
-- Reflects the tables the bot reads/writes via src/database and asyncpg.
-- Run against the database configured by DATABASE_HOST/NAME/USER/PASS.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- guilds
-- Per-guild settings. Read/written by src/database/handlers/guilds.py.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS guilds (
    guild_id     BIGINT PRIMARY KEY,
    alert_channel BIGINT,
    alert_role    BIGINT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ----------------------------------------------------------------------------
-- tickets
-- Support ticket channels. Managed by src/database/handlers/tickets.py.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tickets (
    channel_id   BIGINT PRIMARY KEY,
    guild_id     BIGINT NOT NULL REFERENCES guilds(guild_id) ON DELETE CASCADE,
    owner_id     BIGINT NOT NULL,
    ticket_type  VARCHAR(50) NOT NULL,
    claimed_by   BIGINT DEFAULT NULL,
    status       TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'closed')),
    added_users  JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tickets_guild_id ON tickets(guild_id);
CREATE INDEX IF NOT EXISTS idx_tickets_owner_id ON tickets(owner_id);

-- ----------------------------------------------------------------------------
-- transcript
-- Message log for ticket channels. Written by src/database/handlers/transcript.py.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS transcript (
    id           BIGSERIAL PRIMARY KEY,
    channel_id   BIGINT NOT NULL REFERENCES tickets(channel_id) ON DELETE CASCADE,
    message_id   BIGINT NOT NULL,
    author_id    BIGINT NOT NULL,
    author_tag   TEXT NOT NULL,
    content      TEXT,
    attachments  JSONB,
    created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_transcript_channel_id ON transcript(channel_id);

-- ----------------------------------------------------------------------------
-- reports
-- Player reports. Created by the external reports API (API_URI) but read
-- directly by the bot (check_report, lookup, join/member-monitor alerts).
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reports (
    id                 BIGSERIAL PRIMARY KEY,
    target_user_id     BIGINT NOT NULL,
    target_username    TEXT,
    reporter_user_id   BIGINT,
    reporter_username  TEXT,
    game               TEXT,
    reason             TEXT,
    status             TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected')),
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_reports_target_user_id ON reports(target_user_id);
CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status);

-- ----------------------------------------------------------------------------
-- users
-- Verified/tracked Discord users. Read by join.py and member_monitor.py.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id      BIGINT PRIMARY KEY,
    trust_score  INTEGER,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ----------------------------------------------------------------------------
-- command_permissions
-- Per-guild command access control, backing src/utils/cmdPermissions.py as a
-- database-backed replacement for the JSON permission config files under
-- data/**/config.json.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS command_permissions (
    id           BIGSERIAL PRIMARY KEY,
    guild_id     BIGINT NOT NULL REFERENCES guilds(guild_id) ON DELETE CASCADE,
    command      TEXT NOT NULL,
    role_id      BIGINT NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (guild_id, command, role_id)
);

CREATE INDEX IF NOT EXISTS idx_command_permissions_guild_command ON command_permissions(guild_id, command);
