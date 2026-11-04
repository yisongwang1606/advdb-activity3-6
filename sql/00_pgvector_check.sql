CREATE EXTENSION IF NOT EXISTS vector;

-- Teacher's Week 9 type, cosine distance and HNSW test, using a temporary table.
CREATE TEMP TABLE pgv_test (id int PRIMARY KEY, v vector(3));
INSERT INTO pgv_test VALUES (1, '[1,2,3]'), (2, '[3,2,1]'), (3, '[1,2,4]');
CREATE INDEX ON pgv_test USING hnsw (v vector_cosine_ops);
SELECT id, round((v <=> '[1,2,3]')::numeric, 4) AS cosine_distance
FROM pgv_test ORDER BY v <=> '[1,2,3]' LIMIT 3;
