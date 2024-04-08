
#import os
#
#from app.bq_service import BigQueryService
#
#from datasets.impeachment_2020.botometer_sample_max_50 import DATASET_DIRPATH
#
#
#if __name__ == "__main__":
#
#    os.makedirs(DATASET_DIRPATH, exist_ok=True)
#
#
#    bq = BigQueryService()
#    sql = f"""
#        SELECT status_text_id, status_text, status_count, status_ids, user_count, user_ids
#        FROM `tweet-collector-py.impeachment_production.botometer_sample_max_50_texts_map`
#
#    """
#    print("DOWNLOADING...")
#    df = bq.query_to_df(sql=sql)
#    print(df.shape)
#    print(df.head())
#
#    print("SAVING...")
#    pq_filepath = os.path.join(DATASET_DIRPATH, "texts_map.parquet.gz")
#    print(pq_filepath)
#    df.to_parquet(pq_filepath, index=False, compression="gzip")
#
