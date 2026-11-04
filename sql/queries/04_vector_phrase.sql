-- AI-assisted draft prepared with Codex.
-- Five matches for something scary in the woods
SELECT t.title_id, t.title, t.genre,
       round((t.embedding <=> p.embedding)::numeric, 3) AS cosine_distance
FROM titles t
CROSS JOIN search_phrases p
WHERE p.phrase_id = 4
ORDER BY t.embedding <=> p.embedding, t.title_id
LIMIT 5;
