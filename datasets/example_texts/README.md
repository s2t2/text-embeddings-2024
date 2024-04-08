

## Dataset Info

Use your own example texts, for probing the embeddings in an ad-hoc way.


## OpenAI Embeddings

```sh
python -m datasets.example_texts.openai_embeddings

MODEL="text-embedding-small" N_DIMENSIONS=2 python -m datasets.example_texts.openai_embeddings

MODEL="text-embedding-large" N_DIMENSIONS=2 python -m datasets.example_texts.openai_embeddings
```
