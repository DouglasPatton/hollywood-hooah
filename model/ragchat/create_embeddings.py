from ragchat.configs import (DEBUG, MAX_TOKENS_REF_TEXT, MIN_CHARS_REF_TEXT,
                     MIN_ENGL_SHARE_REF_TEXT, PARSER, VECTOR_STORE_SAVE_PATH)
from ragchat.html_cleaner import HtmlCleaner
from ragchat.text_embedder import TextEmbedder


def create_embeddings():
    cleaner = HtmlCleaner(
        parser=PARSER,
        debug=DEBUG,
        min_chars_ref_text=MIN_CHARS_REF_TEXT,
        min_engl_share_ref_text=MIN_ENGL_SHARE_REF_TEXT,
        max_pages=None,
    )
    clean_text_dict = cleaner.get_clean_text_dict()
    text_embedder = TextEmbedder(
        vector_store_save_path=VECTOR_STORE_SAVE_PATH,
        max_tokens_ref_text=MAX_TOKENS_REF_TEXT,
    )
    text_embedder.embed_text_dict(clean_text_dict)

    print(
        f"embeddings for {len(clean_text_dict)} docs saved to {text_embedder.vector_store_save_path}"
    )


if __name__ == "__main__":
    create_embeddings()
