
import os
from typing import List
from pprint import pprint

from dotenv import load_dotenv
from openai import OpenAI
#from openai.types import Model, Embedding #CreateEmbeddingResponse,

load_dotenv()

#OPENAI_ORG_ID = os.getenv("OPENAI_ORG_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

MAX_RETRIES = int(os.getenv("MAX_RETRIES", default="5"))


class OpenAIService():
    """See:
        https://github.com/openai/openai-python
        https://github.com/openai/openai-python/blob/main/api.md
    """

    def __init__(self, api_key=OPENAI_API_KEY, max_retries=MAX_RETRIES):
        print(api_key)
        self.client = OpenAI(api_key=api_key, max_retries=max_retries)


    #def get_models(self):
    #
    #    return models




    def get_embeddings(self, texts:List[str], model="text-embedding-3-large", **kwargs) -> List[float]:
        """Get Embeddings for a list of texts.

            kwargs :
                dimensions for number of dimensions (large models)

            See:
                https://github.com/openai/openai-python/blob/main/src/openai/types/embedding_create_params.py
                https://github.com/openai/openai-cookbook/blob/main/examples/utils/embeddings_utils.py
        """
        # replace newlines, which can negatively affect performance ?
        for text in texts:
            text = text.replace("\n", " ")

        print(len(texts))
        print(model)
        print(kwargs)

        response = self.client.embeddings.create(input=texts, model=model, **kwargs)

        breakpoint()
        return response.data[0].embedding







if __name__ == "__main__":

    ai = OpenAIService()
    print(ai)

    texts = [
        "Short and sweet",
        "Short short",
        "I like apples, but bananas are gross.",
        "This is a tweet about bananas",
        "Drink apple juice!",
    ]
    pprint(texts)

    response = ai.get_embeddings(texts=texts, dimensions=2)

    breakpoint()
