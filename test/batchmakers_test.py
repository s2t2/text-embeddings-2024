


from app.batchmakers import split_into_batches, dynamic_batches, dynamic_df_batches, dynamic_df_slices

from pandas import DataFrame

texts = [
    "Short and sweet",
    "Short short",
    "I like apples, but bananas are gross.",
    "This is a tweet about bananas",
    "Drink apple juice!",
]

def test_split_into_batches():
    batches = list(split_into_batches(texts, batch_size=2))
    assert batches == [
        ['Short and sweet', 'Short short'], # 2
        ['I like apples, but bananas are gross.', 'This is a tweet about bananas'], # 2
        ['Drink apple juice!'] # remainder
    ]

def test_dynamic_batches():
    batches = dynamic_batches(texts, batch_char_limit=30)
    assert batches == [
        ['Short and sweet', 'Short short'],
        ['I like apples, but bananas are'],
        ['This is a tweet about bananas'],
        ['Drink apple juice!']
    ]

def test_dynamic_df_batches():
    texts_df = DataFrame({"text": texts, "user_id": [i for i in range(1, len(texts)+1)]})
    batches = dynamic_df_batches(texts_df, text_colname="text", batch_char_limit=30)

    #records = []
    #for batch in batches:
    #    batch_records = []
    #    for row in batch:
    #        batch_records.append(dict(row))
    #    records.append(batch_records)

    assert batches == [
        [{'text': 'Short and sweet', 'user_id': 1}, {'text': 'Short short', 'user_id': 2}],
        [{'text': 'I like apples, but bananas are', 'user_id': 3}],
        [{'text': 'This is a tweet about bananas', 'user_id': 4}],
        [{'text': 'Drink apple juice!', 'user_id': 5}]
    ]

def test_dynamic_df_slices():
    texts_df = DataFrame({"text": texts, "user_id": [i for i in range(1, len(texts)+1)]})
    batches = dynamic_df_slices(texts_df, text_colname="text", batch_char_limit=30)

    #records = []
    #for batch in batches:
    #    batch_records = []
    #    for row in batch:
    #        batch_records.append(dict(row))
    #    records.append(batch_records)

    records = [df.to_dict("records") for df in batches]

    assert records == [
        [{'text': 'Short and sweet', 'user_id': 1}, {'text': 'Short short', 'user_id': 2}],
        [{'text': 'I like apples, but bananas are', 'user_id': 3}],
        [{'text': 'This is a tweet about bananas', 'user_id': 4}],
        [{'text': 'Drink apple juice!', 'user_id': 5}]
    ]
