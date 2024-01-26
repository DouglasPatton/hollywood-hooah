from ragchat.configs import MAX_TOKENS_REF_TEXT, VECTOR_STORE_SAVE_PATH
from ragchat.text_embedder import TextEmbedder


def test_embeddings():
    text_embedder = TextEmbedder(
        vector_store_save_path=VECTOR_STORE_SAVE_PATH,
        max_tokens_ref_text=MAX_TOKENS_REF_TEXT,
    )
    vs = text_embedder.get_vector_store()
    test_text = "What kinds of obligations does a production company have?"
    print(vs.similarity_search_with_score(test_text))


if __name__ == "__main__":
    test_embeddings()
