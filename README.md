# Class Activity 3: JSONB and Vector Databases

Group 6 — repository folder: `advdb-activity3-6`.

This repository contains the executed instructor notebook, both generated vector SQL files, a four-table streaming database, synthetic data, six tested queries, real query outputs and a database diagram.

**Status:** executed and validated on the existing native Windows PostgreSQL 18 instance. The contribution table remains deferred. Brightspace submission is not included in this repository upload. Both the final report PDF and Word report are intentionally excluded from GitHub and kept locally.

## Actual run

| Item | Verified value |
| --- | --- |
| Server | PostgreSQL 18.6, local port 5432 |
| Extension | pgvector 0.8.7 (`CREATE EXTENSION vector`) |
| Database | `ca3_streaming` |
| Users / activity events | 24 / 144 |
| Event types | 72 play, 24 pause, 24 rate, 24 search |
| Titles / phrases | 60 / 5 |
| Embedding dimensions | 384 |
| Database capture | 2026-11-03 18:31:23 UTC |
| Validation | Six query outputs verified; four invalid inserts rejected |

The detailed evidence is in [execution_evidence.json](results/execution_evidence.json), [validation.json](results/validation.json) and [query_plans.json](results/query_plans.json). The first file was exported by PostgreSQL during the authenticated pgAdmin execution. Python independently recomputed all six outputs from the saved input files, including exhaustive cosine ranking over the generated vectors. These records describe the captured run, not a future live check.

## Open the deliverables

- [Database diagram: column types, relationships and JSONB examples](docs/CA3_Database_Diagram.pdf)
- [Editable draw.io database diagram](docs/CA3_Database_Diagram.drawio) — open in draw.io using File > Open From > Device. Tables, field labels, JSONB examples and relationship lines are native editable elements. `search_phrases.embedding` is correctly marked `NOT NULL`, matching its SQL definition.
- [All six queries](sql/03_queries.sql) and [readable actual outputs](results/query_results.txt)
- [Generated title vectors](sql/ca3_titles_vectors.sql) and [generated search phrase vectors](sql/ca3_search_phrases.sql)

## Database setup

Use PostgreSQL 18 with pgvector installed into that same PostgreSQL installation. The Windows installation record and reproducible build instructions are in [Windows_pgvector_Setup.txt](docs/Windows_pgvector_Setup.txt). On the original computer, the extension is already installed and the activity database is already populated.

To reproduce on a fresh database:

1. Connect to the local PostgreSQL server in pgAdmin with your normal database login.
2. From another database, run `CREATE DATABASE ca3_streaming;` once.
3. Open a **new Query Tool connected to `ca3_streaming`**.
4. Open and execute the complete [00_load_all_pgadmin.sql](sql/00_load_all_pgadmin.sql). This file includes the extension smoke test, both generated vector files, schema, data, integrity tests, six queries and validation. It contains ordinary SQL, not psql backslash commands.
5. Open the six files in [sql/queries](sql/queries) individually to view each result grid. The CSV and text files retain the results from the verified run.

For a step-by-step import, run the following complete files in order in a new Query Tool:

1. `sql/00_pgvector_check.sql`
2. `sql/ca3_titles_vectors.sql`
3. `sql/ca3_search_phrases.sql`
4. `sql/01_schema.sql`
5. `sql/02_sample_data.sql`
6. `ANALYZE;`, then `sql/05_integrity_tests.sql`
7. `sql/03_queries.sql`, then `sql/04_validation.sql`

The smoke test uses a temporary table named `pgv_test`; use a fresh Query Tool session when repeating it. The phrase file drops and recreates `search_phrases`, replacing its contents. Schema creation uses `IF NOT EXISTS`, so it does not migrate an incompatible existing schema. Use a dedicated activity database; do not apply these files to unrelated coursework databases.

Alternatively, from PowerShell in this repository folder, use the installed `psql` client:

```powershell
& 'C:\Program Files\PostgreSQL\18\bin\psql.exe' -h 127.0.0.1 -p 5432 -U postgres -d ca3_streaming -f sql/run_all.psql
```

Enter your own password at the prompt. No password or connection secret is included in this package. `run_all.psql` stops on errors and resolves included files relative to its own directory. It is for psql, not pgAdmin.

## Embedding notebook

Tools used: Python 3.12.10, VS Code with Python/Jupyter support, `sentence-transformers`, `pandas`, `ipykernel`, and the local `all-MiniLM-L6-v2` model. The exact installed dependencies are recorded in `notebooks/requirements-lock.txt`.

The instructor notebook source code and five default search phrases are unchanged. The saved notebook contains four successfully executed code cells. Kernel metadata was configured for the local environment. Its model revision is `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`; the successful run did not need the notebook's latest-revision fallback.

To rerun on another computer:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r notebooks/requirements-lock.txt
```

Open `notebooks/ca3_make_embeddings_vscode.ipynb` in VS Code, select the new environment as its kernel and Run All. Keep the CSV beside the notebook. The notebook writes `my_sql/ca3_titles_vectors.sql` and `my_sql/ca3_search_phrases.sql` under its working directory. Replace the corresponding files in `sql/` if intentionally regenerating them, then reload the database and recapture results. Changing the input text or model can change the rankings. The existing saved outputs show the original execution paths; they were not rewritten to make the trace look portable.

## Synthetic data and JSONB design

`scripts/generate_sample_data.py` uses only Python's standard library. It deterministically creates 24 fictional profiles and six events per user. It cycles through eight genres, four countries/languages and three plans, assigns two distinct favourite genres per profile, and adds optional autoplay and parental-control settings. Each user has three plays, one pause, one rating and one search. Timestamps are fixed UTC values on October 20–21, 2026; no random seed or live customer data is involved.

```powershell
python scripts/generate_sample_data.py
```

This recreates `data/sample_users.json`, `data/sample_activity.json` and `sql/02_sample_data.sql`. It does not update the database or existing report outputs automatically.

`users.preferences` stores optional settings and the required genre array. `activity_logs.event_data` stores varying event payloads. Foreign keys keep identities and title references relational. CHECK constraints require valid event types and details. General GIN indexes exist on both JSONB columns; B-tree indexes support activity lookups; the supplied titles table includes an HNSW cosine index.

## Query map and sample output

| File | Requirement |
| --- | --- |
| `01_jsonb_containment.sql` | `@>` containment: users who like Mystery |
| `02_jsonb_aggregation.sql` | `->>` extraction and numeric aggregation of viewing minutes |
| `03_jsonb_array.sql` | `jsonb_array_elements_text`: users per favourite genre |
| `04_vector_phrase.sql` | Top five titles for phrase 4: something scary in the woods |
| `05_vector_similar_title.sql` | Top five titles similar to title 3: Crumb & Clue |
| `06_vector_filtered.sql` | Recommend from user 1's latest play, excluding previously played titles |

Actual Query 4 output (smaller cosine distance means closer vectors):

| Title ID | Title | Genre | Cosine distance |
| --- | --- | --- | --- |
| 56 | The Woods Remember | Horror | 0.602 |
| 59 | After Dark | Documentary | 0.638 |
| 25 | Little Fox Detectives | Animation | 0.648 |
| 51 | The Missing Hour | Mystery | 0.666 |
| 31 | Wild Kitchen | Food & Travel | 0.671 |

All vector queries order by the unrounded distance, then title ID; displayed distances are rounded to three decimal places. In the captured plans, the 60-row catalogue was scanned and sorted rather than searched through HNSW. These are verified small-data results, not performance or recommendation-quality benchmarks. Query 6 happens to match Query 5 because the other watched titles were outside its top five. With no play history, Query 6 returns no rows; a cold-start strategy is outside this example.

## Provenance and AI assistance

Instructor-supplied: `ca3_make_embeddings_vscode.ipynb`, `ca3_titles.csv`, `requirements.txt`, the Making the Embeddings document, and the Week 9 pgvector guide. The two vector SQL files came from executing that notebook. The catalogue titles and descriptions are supplied course data.

AI-assisted: local setup, notebook execution, schema/query drafting, the synthetic-data generator, checks, report, diagram and this README. This is an attributed working draft. The course requires student-owned design/code and attribution of adaptations; the team must review and adapt the draft before submission. No team member's contribution has been invented. The contribution table remains deferred as requested.

Reference documentation:

- [Teacher's pgvector guide (SAIT login required)](https://learn.sait.ca/d2l/le/lessons/886971/topics/22165630)
- [PostgreSQL 18 JSON types and indexing](https://www.postgresql.org/docs/18/datatype-json.html)
- [PostgreSQL 18 JSON functions and operators](https://www.postgresql.org/docs/18/functions-json.html)
- [Official pgvector installation, distances and indexes](https://github.com/pgvector/pgvector)

## GitHub repository

Repository: [yisongwang1606/advdb-activity3-6](https://github.com/yisongwang1606/advdb-activity3-6). The repository includes `sql/`, `data/`, `notebooks/`, `scripts/`, `results/`, `docs/`, `README.md` and `.gitignore`. Both the final report PDF and Word report are excluded as requested. The draw.io diagram source and diagram PDF are included. The virtual environment, downloaded model, compiler tools and PostgreSQL binaries are local dependencies and are excluded. The contribution table remains deferred, and this upload does not submit the assignment to Brightspace.

The optional report source is `scripts/build_report.py` (requires ReportLab). It uses the saved verified execution evidence to rebuild both PDFs; it does not query PostgreSQL.
