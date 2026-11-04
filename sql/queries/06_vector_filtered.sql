-- AI-assisted draft prepared with Codex.
-- Recommendations for user 1 excluding watched titles
WITH last_watched AS (
    SELECT title_id
    FROM activity_logs
    WHERE user_id = 1
      AND event_data @> '{"event_type":"play"}'::jsonb
    ORDER BY occurred_at DESC, activity_id DESC
    LIMIT 1
)
SELECT t.title_id, t.title, t.genre,
       round((t.embedding <=> seed.embedding)::numeric, 3) AS cosine_distance
FROM last_watched lw
JOIN titles seed ON seed.title_id = lw.title_id
CROSS JOIN titles t
WHERE NOT EXISTS (
    SELECT 1
    FROM activity_logs watched
    WHERE watched.user_id = 1
      AND watched.title_id = t.title_id
      AND watched.event_data @> '{"event_type":"play"}'::jsonb
)
ORDER BY t.embedding <=> seed.embedding, t.title_id
LIMIT 5;
