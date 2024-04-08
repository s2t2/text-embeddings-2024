import os
from functools import cached_property
from time import sleep

from openai import BadRequestError
#from openai.error import RateLimitError, ServiceUnavailableError
from pandas import DataFrame

from app import RESULTS_DIRPATH
from app.batchmakers import dynamic_df_slices
from app.bq_service import BigQueryService
from app.openai_service import OpenAIService, MODEL_NAME, N_DIMENSIONS
#from datasets.impeachment_2020.botometer_sample_max_50.user_embeddings_job import TextEmbeddingsJob

USERS_LIMIT = os.getenv("USERS_LIMIT")

#MODEL_NAMES_MAP = {
#    "text-embedding-ada-002": {"dirname": "openai_ada2"}, #, "max_dims": },
#    "text-embedding-3-small": {"dirname": "openai_3small"}, #"max_dims": },
#    "text-embedding-3-large": {"dirname": "openai_3large"}, #"max_dims": 8191},
#}


class OpenAIUserEmbeddingsJob():

    def __init__(self, model_name=MODEL_NAME, n_dimensions=N_DIMENSIONS): # users_limit=USERS_LIMIT

        self.model_name = model_name
        self.n_dimensions = n_dimensions
        self.ai = OpenAIService()

        self.bq = BigQueryService()
        self.dataset_address = "tweet-collector-py.impeachment_production"
        self.embeddings_table_name = f"botometer_sample_max_50_openai_user_embeddings_2024"
        self.embeddings_table_address = f"{self.dataset_address}.{self.embeddings_table_name}"
        #self.users_limit = users_limit

        #self.model_dirname = MODEL_NAMES_MAP[self.model_name] # #f"openai-{self.model_name}" # MODEL_NAME #.replace('-', '_')
        self.results_dirpath = os.path.join(RESULTS_DIRPATH, "botometer_sample_max_50", self.model_name, f"{self.n_dimensions}_dimensions")
        os.makedirs(self.results_dirpath, exist_ok=True)

    def count_completed_users(self):
        sql = f"""
            SELECT count(distinct emb.user_id) as user_count
            FROM `{self.embeddings_table_address}` emb
        """
        response = self.bq.execute_query(sql)
        return list(response)[0][0]

    def get_remaining_users(self, limit=USERS_LIMIT) -> DataFrame:
        sql = f"""
           SELECT u.user_id
                ,u.status_count
                --,u.status_ids
                ,u.texts_length
                ,u.status_texts
            FROM `{self.dataset_address}.botometer_sample_max_50_user_texts` u
            LEFT JOIN  `{self.embeddings_table_address}` emb
                ON u.user_id = emb.user_id
                AND emb.model_name='{self.model_name}'
                AND emb.dimensions={self.n_dimensions}
            WHERE emb.user_id IS NULL
            ORDER BY u.user_id
        """
        if USERS_LIMIT:
            sql += f"    LIMIT {int(USERS_LIMIT)} "

        return self.bq.query_to_df(sql)


    @cached_property
    def embeddings_table(self):
        return self.bq.client.get_table(self.embeddings_table_address) # API call!












if __name__ == "__main__":

    job = OpenAIUserEmbeddingsJob()

    progress = job.count_completed_users()
    print("PROGRESS:", progress)

    users_df = job.get_remaining_users()
    print(len(users_df))
    if users_df.empty:
        print("NO MORE USERS TO PROCESS... GOODBYE!")
        exit()

    print("---------------")
    print("EMBEDDINGS...")

    batches = dynamic_df_slices(users_df, text_colname="status_texts", batch_char_limit=20_000) # cuts off single longest user that has length of 22467, to get through bad request error

    for batch_df in batches:
        user_ids = batch_df["user_id"]
        texts = batch_df["status_texts"].tolist()
        print("BATCH:", len(batch_df), batch_df["texts_length"].sum())

        try:
            embeddings_df = job.ai.get_embeddings(texts=texts, model=MODEL_NAME, dimensions=N_DIMENSIONS, format_as="df", col_prefix="dim")
        except (BadRequestError) as err:
            # openai.BadRequestError: Error code: 400 - {'error': {'message': "This model's maximum context length is 8192 tokens, however you requested 8545 tokens (8545 in your prompt; 0 for the completion).
            # Please reduce your prompt; or completion length.", 'type': 'invalid_request_error', 'param': None, 'code': None}}
            print(err)
            breakpoint()

        embedding_cols = [col for col in embeddings_df.columns if "dim" in col]
        embeddings = embeddings_df[embedding_cols].round(8)
        embeddings = embeddings.apply(lambda row: row.tolist(), axis=1) # pack embeddings into a single column

        batch_df.reset_index(drop=True, inplace=True) # reset index (has original pre-batch index) so we can add embeddings back
        batch_df["model_name"] = MODEL_NAME
        batch_df["dimensions"] = N_DIMENSIONS
        batch_df["embeddings"] = embeddings
        records = batch_df[["user_id", "model_name", "dimensions", "embeddings"]].to_dict("records")

        try:
            errors = job.bq.insert_records_in_batches(job.embeddings_table, records, batch_size=50) # running into google api issues with larger batches - there are so many embeddings for each row, so we lower the batch count substantially
            if any(errors):
                print("ERRORS:")
                print(errors)
                breakpoint()
        except Exception as err:
            print(err)
            breakpoint()


    print("---------------")
    print("JOB COMPLETE!")




    exit()

    #sql = f"""
    #    SELECT
    #        count(distinct user_id) as user_count
    #        -- , count(distinct status_id)  as status_count
    #    FROM `{job.embeddings_table_name}`
    #    -- LIMIT 100
    #"""
    #job.bq.query_to_df(sql)

    #sql = f"""
    #    SELECT user_id, model_name, dimensions --, embeddings
    #    FROM `{job.embeddings_table_name}`
    #    LIMIT 10
    #"""
    #job.bq.query_to_df(sql)
