import os

from dotenv import load_dotenv
from google.cloud import bigquery
from pandas import read_gbq, DataFrame
#from datetime import datetime

from app.batchmakers import split_into_batches

load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID", default="tweet-collector-py")

class BigQueryService():
    def __init__(self, project_id=PROJECT_ID):
        self.project_id = project_id
        self.client = bigquery.Client(project=self.project_id)

        self.notebooks_env = bool(os.getenv("COLAB_RELEASE_TAG")) # true if present (which in colab it is)
        self.split_into_batches = split_into_batches


    def execute_query(self, sql, verbose=True):
        if verbose == True:
            print(sql)
        job = self.client.query(sql)
        return job.result()

    #def query_to_df(self, sql, verbose=True):
    #    """high-level wrapper to return a DataFrame"""
    #    results = self.execute_query(sql, verbose=verbose)
    #    return DataFrame([dict(row) for row in results])

    def query_to_df(self, sql, verbose=True):
        """high-level wrapper to return a DataFrame"""
        if verbose == True:
            print(sql)
        # https://pandas.pydata.org/docs/reference/api/pandas.read_gbq.html#pandas-read-gbq
        #return read_gbq(sql, project_id=self.project_id) # progress_bar_type="tqdm_notebook"
        #progress_bar_type="tqdm_notebook"
        progress_bar_type = "tqdm_notebook" if self.notebooks_env else "tqdm"
        return read_gbq(sql, project_id=self.project_id, progress_bar_type=progress_bar_type)

    # WRITING

    #@staticmethod
    #def split_into_batches(my_list, batch_size=10_000):
    #    """Splits a list into evenly sized batches"""
    #    # h/t: https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
    #    for i in range(0, len(my_list), batch_size):
    #        yield my_list[i : i + batch_size]

    # @ staticmethod
    #def generate_timestamp(dt=None):
    #    """Formats datetime object for storing in BigQuery. Uses current time by default. """
    #    dt = dt or datetime.now()
    #    return dt.strftime("%Y-%m-%d %H:%M:%S")

    def insert_records_in_batches(self, table, records, batch_size=5_000):
        """
        Inserts records in batches because attempting to insert too many rows at once
            may result in google.api_core.exceptions.BadRequest: 400

        Params:
            table (table ID string, Table, or TableReference)
            records (list of dictionaries)
        """
        rows_to_insert = [list(d.values()) for d in records]
        #errors = self.client.insert_rows(table, rows_to_insert)
        errors = []
        batches = list(split_into_batches(rows_to_insert, batch_size=batch_size))
        for batch in batches:
            errors += self.client.insert_rows(table, batch)
        return errors


if __name__ == "__main__":

    bq = BigQueryService()
    print("NOTEBOOKS ENV:", bq.notebooks_env)

    client = bq.client
    print("PROJECT:", client.project)

    print("DATASETS:")
    datasets = list(client.list_datasets())
    for ds in datasets:
        #if "user" not in ds.dataset_id:
        print("...", ds.dataset_id)
