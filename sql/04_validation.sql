-- AI-assisted validation. These queries report actual loaded state.
SELECT 'users' AS table_name, count(*) AS row_count FROM users
UNION ALL SELECT 'activity_logs', count(*) FROM activity_logs
UNION ALL SELECT 'titles', count(*) FROM titles
UNION ALL SELECT 'search_phrases', count(*) FROM search_phrases;

SELECT event_data ->> 'event_type' AS event_type, count(*) AS event_count
FROM activity_logs GROUP BY 1 ORDER BY 1;

SELECT count(*) AS titles, count(embedding) AS with_vectors,
       min(vector_dims(embedding)) AS min_dimensions,
       max(vector_dims(embedding)) AS max_dimensions
FROM titles;

SELECT tablename, indexname, indexdef FROM pg_indexes
WHERE schemaname = 'public' ORDER BY tablename, indexname;

SELECT count(*) AS users_missing_genre_array
FROM users
WHERE jsonb_typeof(preferences -> 'favourite_genres') IS DISTINCT FROM 'array';

SELECT count(*) AS orphan_events
FROM activity_logs a
LEFT JOIN users u ON u.user_id = a.user_id
LEFT JOIN titles t ON t.title_id = a.title_id
WHERE u.user_id IS NULL OR (a.title_id IS NOT NULL AND t.title_id IS NULL);
