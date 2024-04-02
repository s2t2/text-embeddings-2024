
import os
from typing import List
from pprint import pprint

from dotenv import load_dotenv
from openai import OpenAI
from openai.types import Model, Embedding #CreateEmbeddingResponse,
from pandas import DataFrame

import plotly.express as px
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances

from app import RESULTS_DIRPATH
from app.openai_service import OpenAIService, MODEL_NAME, N_DIMENSIONS

texts = [
    "A bright sunny day is perfect for a leisurely walk in the park.",
    "Rainy afternoons are ideal for curling up with a good book.",
    "During a clear day, the park is filled with people enjoying the outdoors.",
    "There's nothing like the sound of rain against the windows when you're reading at home.",
    "Technology advancements are transforming the future of renewable energy.",
    "The latest innovations in artificial intelligence are reshaping industries.",
    "Sustainable energy solutions are crucial for addressing climate change.",
]
pprint(texts)


if __name__ == "__main__":

    MODEL_DIRNAME = f"openai-{MODEL_NAME}"
    results_dirpath = os.path.join(RESULTS_DIRPATH, "example_texts", MODEL_DIRNAME, f"{N_DIMENSIONS}_dimensions")
    os.makedirs(results_dirpath, exist_ok=True)


    ai = OpenAIService()
    print(ai)


    print("--------------")
    print("EMBEDDINGS...")

    df = ai.get_embeddings(texts=texts, model=MODEL_NAME, dimensions=N_DIMENSIONS)
    print(df.head())
    pq_filepath = os.path.join(results_dirpath, f"embeddings.parquet.gz")
    df.to_parquet(pq_filepath, index=False, compression="gzip")

    if N_DIMENSIONS == 2:
        title = "OpenAI Embeddings for Example Texts"
        title += f"<br><sup>Model: {MODEL_NAME} | Dimensions: {N_DIMENSIONS}</sup>"
        fig = px.scatter(df, x="dimension_1", y="dimension_2", title=title, hover_data= ["text"], height=500)
        fig.show()
        fig.write_image(os.path.join(results_dirpath, f"embeddings.png"))
        fig.write_html(os.path.join(results_dirpath, f"embeddings.html"))


    print("--------------")
    print("COSINE SIMILARITIES:")

    embeddings = df[[col for col in df.columns if "dimension" in col]]
    mat = cosine_similarity(embeddings)
    similarity_df = DataFrame(mat, columns=texts, index=texts)
    similarity_df.head()
    similarity_df.to_csv(os.path.join(results_dirpath, "cosine_similarity_matrix.csv"))

    # PLOT SIMILARITY MATRIX
    showscale = False
    title = f"Similarity Matrix for Example Texts"
    title += f"<br><sup>Model: {MODEL_NAME} | Dimensions: {N_DIMENSIONS}</sup>"
    fig = px.imshow(mat, x=texts, y=texts, height=700,
                    #labels={"x": "Predicted", "y": "Actual"},
                    color_continuous_scale="Blues",
                    text_auto='.3f', #True,

    )
    fig.update_layout(title={'text': title, 'x':0.485, 'xanchor': 'center'})
    fig.update_coloraxes(showscale=showscale)
    fig.show()
    fig.write_image(os.path.join(results_dirpath, "cosine_similarity_matrix.png"))
    fig.write_html(os.path.join(results_dirpath, "cosine_similarity_matrix.html"))


    print("--------------")
    print("EUCLIDEAN DISTANCES:")

    distances_mat = euclidean_distances(embeddings)
    distances_df = DataFrame(distances_mat, columns=texts, index=texts)
    distances_df.head()
    distances_df.to_csv(os.path.join(results_dirpath, "euclidean_distance_matrix.csv"))

    # PLOT DISTANCE MATRIX
    showscale = False
    title = f"Distance Matrix for Example Texts"
    title += f"<br><sup>Model: {MODEL_NAME} | Dimensions: {N_DIMENSIONS}</sup>"
    fig = px.imshow(distances_mat, x=texts, y=texts, height=700,
                    #labels={"x": "Predicted", "y": "Actual"},
                    color_continuous_scale="Blues_r", # use reversed scale
                    text_auto='.3f', #True,

    )
    fig.update_layout(title={'text': title, 'x':0.485, 'xanchor': 'center'})
    fig.update_coloraxes(showscale=showscale)
    fig.show()
    fig.write_image(os.path.join(results_dirpath, "euclidean_distance_matrix.png"))
    fig.write_html(os.path.join(results_dirpath, "euclidean_distance_matrix.html"))
