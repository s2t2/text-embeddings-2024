# text-embeddings-2024

Text Embeddings for User Classification in Social Networks (2024).

Continuation of [previous research](https://github.com/s2t2/openai-embeddings-2023).

## Setup

### Virtual Environment

Create and/or activate virtual environment:

```sh
conda create -n embeddings-2024 python=3.10
conda activate embeddings-2024
```

Install package dependencies:

```sh
pip install -r requirements.txt
```


### Environment Variables

Create ".env" file with contents like the following:

```sh
# OPENAI:
OPENAI_API_KEY="sk-_________"

# GOOGLE CLOUD:
GOOGLE_APPLICATION_CREDENTIALS="/path/to/text-embeddings-2024/google-credentials.json"
```


## Usage

### BigQuery Service

```sh
python -m app.bq_service
```

### OpenAI Service

```sh
python -m app.openai_service

MODEL_NAME="text-embedding-3-small" N_DIMENSIONS=1536 python -m app.openai_service

MODEL_NAME="text-embedding-3-large" N_DIMENSIONS=3072 python -m app.openai_service
```
