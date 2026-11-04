-- AI-assisted draft prepared with Codex.
-- Five titles like Crumb & Clue
SELECT t.title_id, t.title, t.genre,
       round((t.embedding <=> seed.embedding)::numeric, 3) AS cosine_distance
FROM titles t
CROSS JOIN titles seed
WHERE seed.title_id = 3 AND t.title_id <> seed.title_id
ORDER BY t.embedding <=> seed.embedding, t.title_id
LIMIT 5;
