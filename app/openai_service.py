
import os
from typing import List
from pprint import pprint

from dotenv import load_dotenv
from openai import OpenAI
from openai.types import Model, Embedding #CreateEmbeddingResponse,
from pandas import DataFrame


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MAX_RETRIES = int(os.getenv("MAX_RETRIES", default="3"))

MODEL_NAME = os.getenv("MODEL_NAME", default="text-embedding-3-large")
N_DIMENSIONS = int(os.getenv("N_DIMENSIONS", default="3072"))

class OpenAIService():
    """Interface for fetching embeddings from OpenAI API.

        See:
            https://github.com/openai/openai-python

            https://github.com/openai/openai-python/blob/main/api.md
    """

    def __init__(self, api_key=OPENAI_API_KEY, max_retries=MAX_RETRIES):
        print(api_key)
        self.client = OpenAI(api_key=api_key, max_retries=max_retries)

    def get_models(self):
        response = self.client.models.list()
        return response.data

    def get_embeddings(self, texts:List[str], model=MODEL_NAME, verbose=False,
                                format_as="df", col_prefix="dimension", **kwargs) -> DataFrame: #List[float]: # -> List[Embedding]:
        """Get embeddings for a list of texts.

            Params:

                model : model name (i.e. "text-embedding-ada-002", "text-embedding-3-small", "text-embedding-3-large")

                kwargs :
                    dimensions : number of dimensions (for v3 models)
                        3-large max is 3072
                        3-small max is 1536

                format_as (str) : return original "response", or just the embeddings as a "list" or "df"

            See:
                + https://platform.openai.com/docs/guides/embeddings/embedding-models
                + https://openai.com/blog/new-embedding-models-and-api-updates
                + https://github.com/openai/openai-python/blob/main/src/openai/types/embedding_create_params.py
                + https://github.com/openai/openai-cookbook/blob/main/examples/utils/embeddings_utils.py
        """
        # replace newlines, which can negatively affect performance ?
        # preprocessing ??
        for text in texts:
            text = text.lower()
            text = text.replace("\n", " ")

        if verbose:
            print("TEXTS:", len(texts))
            print("MODEL:", model)
            print("...", kwargs)

        response = self.client.embeddings.create(input=texts, model=model, **kwargs)
        if verbose:
            print(response.usage) #> Usage(prompt_tokens=24, total_tokens=24)
            print(len(response.data))
            print(response.data[0]) #> Embedding(embedding=[-0.8389613032341003, -0.5441911220550537], index=0, object='embedding')
            # response.data[0].embedding

        embeddings = [e.embedding for e in response.data]

        if format_as == "df":
            df = DataFrame(embeddings)
            df.columns = [f"{col_prefix}_{i}" for i in range(1, len(df.columns)+1)]
            df.insert(0, "text", texts) # insert column as the first
            return df
        elif format_as == "response":
            return response
        else:
            return embeddings



if __name__ == "__main__":

    ai = OpenAIService()
    print(ai)

    print("MODELS...")

    models = ai.get_models()
    for model in models:
        print(model.id, model.owned_by)

    print("EMBEDDINGS...")

    text = input("Please provide an example text input: ") or "A bright sunny day is perfect for a leisurely walk in the park."
    embeddings = ai.get_embeddings(texts=[text], model=MODEL_NAME, dimensions=N_DIMENSIONS, format_as="list")
    print(embeddings)
