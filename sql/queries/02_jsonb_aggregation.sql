-- AI-assisted draft prepared with Codex.
-- Top ten titles by recorded viewing minutes
SELECT t.title_id, t.title,
       sum((a.event_data ->> 'minutes_watched')::numeric) AS total_minutes,
       count(*) AS play_events
FROM activity_logs a
JOIN titles t ON t.title_id = a.title_id
WHERE a.event_data @> '{"event_type":"play"}'::jsonb
GROUP BY t.title_id, t.title
ORDER BY total_minutes DESC, t.title_id
LIMIT 10;
