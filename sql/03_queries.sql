-- AI-assisted draft prepared with Codex; review and adapt before submission.
-- The secondary title_id ordering makes ties deterministic.
-- With 60 titles, the tested planner uses exact distance evaluation.

-- 01_jsonb_containment: Users who like Mystery
SELECT user_id, full_name, plan,
       preferences -> 'favourite_genres' AS favourite_genres
FROM users
WHERE preferences @> '{"favourite_genres":["Mystery"]}'::jsonb
ORDER BY user_id;

-- 02_jsonb_aggregation: Top ten titles by recorded viewing minutes
SELECT t.title_id, t.title,
       sum((a.event_data ->> 'minutes_watched')::numeric) AS total_minutes,
       count(*) AS play_events
FROM activity_logs a
JOIN titles t ON t.title_id = a.title_id
WHERE a.event_data @> '{"event_type":"play"}'::jsonb
GROUP BY t.title_id, t.title
ORDER BY total_minutes DESC, t.title_id
LIMIT 10;

-- 03_jsonb_array: Favourite genres across users
SELECT g.genre, count(*) AS users_with_genre
FROM users u
CROSS JOIN LATERAL jsonb_array_elements_text(
    u.preferences -> 'favourite_genres'
) AS g(genre)
GROUP BY g.genre
ORDER BY users_with_genre DESC, g.genre;

-- 04_vector_phrase: Five matches for something scary in the woods
SELECT t.title_id, t.title, t.genre,
       round((t.embedding <=> p.embedding)::numeric, 3) AS cosine_distance
FROM titles t
CROSS JOIN search_phrases p
WHERE p.phrase_id = 4
ORDER BY t.embedding <=> p.embedding, t.title_id
LIMIT 5;

-- 05_vector_similar_title: Five titles like Crumb & Clue
SELECT t.title_id, t.title, t.genre,
       round((t.embedding <=> seed.embedding)::numeric, 3) AS cosine_distance
FROM titles t
CROSS JOIN titles seed
WHERE seed.title_id = 3 AND t.title_id <> seed.title_id
ORDER BY t.embedding <=> seed.embedding, t.title_id
LIMIT 5;

-- 06_vector_filtered: Recommendations for user 1 excluding watched titles
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
