import faiss
import pickle
from sentence_transformers import SentenceTransformer


print("Loading retrieval model...")


model = SentenceTransformer(
    "BAAI/bge-small-en-v1.5"
)


INDEX_PATH = "data/vector_store/legal.index"
CHUNKS_PATH = "data/vector_store/chunks.pkl"


print("Loading FAISS index...")


index = faiss.read_index(INDEX_PATH)


with open(CHUNKS_PATH, "rb") as f:
    chunks = pickle.load(f)


print("FAISS Loaded!")
print("Total vectors:", index.ntotal)



def expand_query(query):

    legal_terms = {

        "murder": "murder section 103 death imprisonment for life punishment",

        "theft": "theft section punishment property dishonest intention",

        "rape": "rape sexual assault section punishment imprisonment",

        "bail": "bail criminal procedure release accused",

        "arrest": "arrest procedure police custody rights"

    }


    query_lower = query.lower()


    for key, expansion in legal_terms.items():

        if key in query_lower:

            return query + " " + expansion


    return query




def keyword_score(query, text, metadata):

    score = 0

    text_lower = text.lower()
    query_lower = query.lower()


    # Main legal concepts
    if "murder" in query_lower:

        if metadata["section"] == "103":
            score += 10

        if metadata["section"] == "104":
            score += 8

        if metadata["section"] in ["105", "109"]:
            score += 5


    # General keyword matching
    terms = [
        "punishment",
        "death",
        "imprisonment",
        "fine"
    ]


    for term in terms:

        if term in query_lower and term in text_lower:

            score += 0.5


    return score





def search_documents(query, k=8):


    expanded_query = expand_query(query)


    print("Expanded Query:")
    print(expanded_query)



    query_embedding = model.encode(

        [expanded_query],

        normalize_embeddings=True,

        convert_to_numpy=True

    )



    distances, indices = index.search(

        query_embedding,

        20

    )



    results = []



    for idx, distance in zip(indices[0], distances[0]):


        text = chunks[idx]["text"]


        keyword = keyword_score(

            query,

            text,
            
            chunks[idx]["metadata"]

        )


        final_score = (

            float(distance) 

            +

            (keyword * 0.05)

        )


        results.append(

            {

                "text": text,

                "metadata": chunks[idx]["metadata"],

                "score": final_score

            }

        )



    results = sorted(

        results,

        key=lambda x: x["score"],

        reverse=True

    )



    return results[:k]