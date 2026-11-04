-- AI-assisted draft prepared with Codex.
-- Users who like Mystery
SELECT user_id, full_name, plan,
       preferences -> 'favourite_genres' AS favourite_genres
FROM users
WHERE preferences @> '{"favourite_genres":["Mystery"]}'::jsonb
ORDER BY user_id;
