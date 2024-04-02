## Dataset Info

The "botometer_sample_max_50" comes from the "impeachment_2020" dataset.

## Downloading

Downloading dataset from BQ:

```sh
python -m datasets.botometer_sample_max_50.dataset_downloader
```

## OpenAI Embeddings

### User Embeddings

Migrate table for user texts:

```sql
DROP TABLE IF EXISTS `tweet-collector-py.impeachment_production.botometer_sample_max_50_user_texts`;
CREATE TABLE `tweet-collector-py.impeachment_production.botometer_sample_max_50_user_texts` as (
    SELECT *, length(status_texts) as texts_length
    FROM (
        SELECT
            s.user_id --,min(s.row_num) as row_min, max(s.row_num) as row_max
            ,count(distinct s.status_id) as status_count -- in sample status count (max 50)
            ,array_agg(distinct s.status_id) as status_ids
            ,string_agg(distinct s.status_text, " ") as status_texts
        FROM `tweet-collector-py.impeachment_production.botometer_sample_max_50` s
        GROUP BY 1
        ORDER BY 1
    )
);
```

Migrate table for user embeddings:

```sql
DROP TABLE IF EXISTS `tweet-collector-py.impeachment_production.botometer_sample_max_50_openai_user_embeddings_2024`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_production.botometer_sample_max_50_openai_user_embeddings_2024` (
    user_id	    INT64,
    model_name	STRING,
    dimensions	INT64,
    embeddings ARRAY<FLOAT64>
);
```


Fetch embeddings:

```sh
MODEL_NAME="text-embedding-3-large" N_DIMENSIONS=3072 USERS_LIMIT=10 python -m datasets.botometer_sample_max_50.openai_user_embeddings
```
