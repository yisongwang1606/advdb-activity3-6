-- AI-assisted draft prepared with Codex. Review and adapt before course submission.
-- Instructor-provided titles and search_phrases must be loaded first.
BEGIN;

CREATE TABLE IF NOT EXISTS users (
    user_id integer PRIMARY KEY,
    full_name text NOT NULL,
    email text NOT NULL UNIQUE,
    country char(2) NOT NULL,
    plan text NOT NULL CHECK (plan IN ('Basic', 'Standard', 'Premium')),
    preferences jsonb NOT NULL,
    CONSTRAINT preferences_object CHECK (jsonb_typeof(preferences) = 'object'),
    CONSTRAINT favourite_genres_array CHECK (
        (jsonb_typeof(preferences -> 'favourite_genres') = 'array') IS TRUE
    )
);

CREATE TABLE IF NOT EXISTS activity_logs (
    activity_id bigint PRIMARY KEY,
    user_id integer NOT NULL REFERENCES users(user_id),
    title_id integer REFERENCES titles(title_id),
    occurred_at timestamptz NOT NULL,
    event_data jsonb NOT NULL,
    CONSTRAINT event_object CHECK (jsonb_typeof(event_data) = 'object'),
    CONSTRAINT known_event_type CHECK (
        ((event_data ->> 'event_type') IN ('play', 'pause', 'rate', 'search')) IS TRUE
    ),
    CONSTRAINT event_title_reference CHECK (
        CASE WHEN event_data ->> 'event_type' = 'search'
            THEN title_id IS NULL ELSE title_id IS NOT NULL END
    ),
    CONSTRAINT valid_event_details CHECK (
        CASE event_data ->> 'event_type'
            WHEN 'play' THEN
                CASE WHEN jsonb_typeof(event_data -> 'minutes_watched') = 'number'
                    THEN (event_data ->> 'minutes_watched')::numeric >= 0
                    ELSE false END
            WHEN 'pause' THEN
                CASE WHEN jsonb_typeof(event_data -> 'paused_at_minute') = 'number'
                    THEN (event_data ->> 'paused_at_minute')::numeric >= 0
                    ELSE false END
            WHEN 'rate' THEN
                CASE WHEN jsonb_typeof(event_data -> 'stars') = 'number'
                    THEN (event_data ->> 'stars')::numeric BETWEEN 1 AND 5
                     AND (event_data ->> 'stars')::numeric = trunc((event_data ->> 'stars')::numeric)
                    ELSE false END
            WHEN 'search' THEN
                COALESCE(jsonb_typeof(event_data -> 'query') = 'string'
                    AND length(btrim(event_data ->> 'query')) > 0, false)
            ELSE false
        END
    )
);

-- Each JSONB column has a general-purpose GIN index.
CREATE INDEX IF NOT EXISTS users_preferences_gin ON users USING gin (preferences);
CREATE INDEX IF NOT EXISTS activity_event_data_gin ON activity_logs USING gin (event_data);
-- These B-tree indexes support joins, recent activity and watched-title checks.
CREATE INDEX IF NOT EXISTS activity_user_time_idx
    ON activity_logs (user_id, occurred_at DESC, activity_id DESC);
CREATE INDEX IF NOT EXISTS activity_title_idx ON activity_logs (title_id);

COMMIT;
