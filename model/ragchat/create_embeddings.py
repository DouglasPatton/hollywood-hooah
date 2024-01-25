from ragchat.configs import (DB_NAME, COLLECTION_NAME,
    DEBUG, MAX_TOKENS_REF_TEXT, MIN_TOKENS_REF_TEXT, 
    VECTOR_STORE_SAVE_PATH)
from ragchat.doc_store import DocStore

from ragchat.text_embedder import TextEmbedder


def create_embeddings():
    ds=DocStore(db_name=DB_NAME, collection_name=COLLECTION_NAME,)
    text_embedder = TextEmbedder(
        vector_store_save_path=VECTOR_STORE_SAVE_PATH,
        max_tokens_ref_text=MAX_TOKENS_REF_TEXT,
        min_tokens_ref_text=MIN_TOKENS_REF_TEXT,
    )
    for doc_chunk in ds.yield_from_db(query={}, chunk_size=100):
        text_embedder.embed_docs(doc_chunk)

    


if __name__ == "__main__":
    create_embeddings()
