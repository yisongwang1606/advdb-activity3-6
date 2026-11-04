-- AI-assisted draft prepared with Codex.
-- Favourite genres across users
SELECT g.genre, count(*) AS users_with_genre
FROM users u
CROSS JOIN LATERAL jsonb_array_elements_text(
    u.preferences -> 'favourite_genres'
) AS g(genre)
GROUP BY g.genre
ORDER BY users_with_genre DESC, g.genre;
