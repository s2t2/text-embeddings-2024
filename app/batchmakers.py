from typing import List

from pandas import DataFrame, Series


def split_into_batches(my_list, batch_size=10_000):
    """Splits a list into evenly sized batches. Returns a generator!"""
    # h/t: https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
    for i in range(0, len(my_list), batch_size):
        yield my_list[i : i + batch_size]



def dynamic_batches(texts, batch_char_limit=30_000) -> List[List[str]] :
    """Splits texts into batches, with specified max number of characters per batch.
        Caps text length at the maximum batch size (individual text cannot exceed batch size).
        Batches may have different lengths.
    """
    batches = []

    batch = []
    batch_chars = 0
    for text in texts:
        text_chars = len(text)

        if (batch_chars + text_chars) <= batch_char_limit:
            # THERE IS ROOM TO ADD THIS TEXT TO THE BATCH
            batch.append(text)
            batch_chars += text_chars
        else:
            # NO ROOM IN THIS BATCH, START A NEW ONE:

            if text_chars > batch_char_limit:
                # CAP THE TEXT AT THE MAX BATCH LENGTH
                text = text[0:batch_char_limit]

            batches.append(batch)
            batch = [text]
            batch_chars = text_chars

    if batch:
        batches.append(batch)

    return batches


def dynamic_df_batches(df:DataFrame, text_colname="texts", batch_char_limit=30_000) -> List[List[dict]]:
    """Splits texts into batches, with specified max number of characters per batch.
        Caps text length at the maximum batch size (individual text cannot exceed batch size).
        Batches may have different lengths (in terms of number of rows).

        Params df (has column of texts, as well as other columns like user_id we care about matching up with later)

        Returns a list of one or more rows (pandas Series) per batch.
    """
    df = df.copy()
    batches = []
    batch = []
    batch_chars = 0
    for _, row in df.iterrows():
        text = row[text_colname]
        text_chars = len(text)
        print(text)

        if (batch_chars + text_chars) <= batch_char_limit:
            # THERE IS ROOM TO ADD THIS TEXT TO THE BATCH
            batch.append(dict(row)) # consider collecting the series or the dict
            batch_chars += text_chars
        else:
            # NO ROOM IN THIS BATCH, START A NEW ONE:
            if text_chars > batch_char_limit:
                # CAP THE TEXT AT THE MAX BATCH LENGTH:
                #text = text[0:batch_char_limit-1]
                row[text_colname] = text[0:batch_char_limit]
                text_chars = len(row[text_colname])
            # CLEAR AND RESET THE BATCH:
            batches.append(batch)
            batch = [dict(row)] # consider collecting the series or the dict
            batch_chars = text_chars

    if batch:
        batches.append(batch)

    return batches



def dynamic_df_slices(df:DataFrame, text_colname="text", batch_char_limit=30_000) -> List[DataFrame]:

    batches = []
    batch = []
    batch_length = 0

    df = df.copy()
    #df["text_truncated"] = df[text_colname].str.slice(stop=batch_char_limit)
    #df["text_truncated_length"] = df["text_truncated"].str.len()
    df[text_colname] = df[text_colname].str.slice(stop=batch_char_limit)

    for _, row in df.iterrows():
        # if any texts exceed the max batch length, we will truncate them at the batch length:
        #text = row["text_truncated"]
        #text_length = row["text_truncated_length"]
        #text = row[text_colname][0:batch_char_limit-1]
        text = row[text_colname]
        text_length = len(text)

        if (batch_length + text_length) <= batch_char_limit:
            batch.append(row)
            batch_length += text_length
        else:
            batches.append(DataFrame(batch))
            batch = [row]
            batch_length = text_length

    if batch:
        batches.append(DataFrame(batch))

    return batches
