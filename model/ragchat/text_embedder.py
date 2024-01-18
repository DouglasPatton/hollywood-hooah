import os
# summarize documents to see how the html cleaning is doing
from time import sleep

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.text_splitter import (RecursiveCharacterTextSplitter)
from langchain_community.chat_models import ChatOpenAI
# from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores import FAISS


class TextEmbedder:
    def __init__(
        self,
        max_tokens_ref_text=8000,
        vector_store_save_path="vector_stores/faiss_index_0",
    ):
        self.max_tokens_ref_text = max_tokens_ref_text
        self.vector_store_save_path = vector_store_save_path
        self.llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)
        self.embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

    @staticmethod
    def add_title(text_result_dict):
        return (
            f"Title: {text_result_dict['title']}:"
            f"\n\n\n{text_result_dict['cleaned']}"
        )

    def split_text(self, clean_text, max_tokens):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=max_tokens,
            chunk_overlap=20,
            length_function=self.llm.get_num_tokens,
            is_separator_regex=False,
        )
        return text_splitter.split_text(clean_text)

    def prep_docs(self, clean_text_dict):
        all_docs = []
        for pg, text_result in clean_text_dict.items():
            text = TextEmbedder.add_title(text_result)
            n_tokens_est = self.llm.get_num_tokens(text)
            if n_tokens_est > self.max_tokens_ref_text:
                texts = self.split_text(
                    text_result["cleaned"], self.max_tokens_ref_text
                )
            else:
                texts = [text]
            docs = [
                Document(
                    page_content=text,
                    metadata={
                        "page": pg,
                        "title": text_result["title"],
                        "split_idx": i,
                        "n_splits": len(texts),
                    },
                )
                for i, text in enumerate(texts)
            ]
            all_docs.extend(docs)
        return all_docs

    def embed_text_dict(self, clean_text_dict, test=True):
        assert not os.path.exists(self.vector_store_save_path), print(
            f"vector_store_save_path already exists at :{self.vector_store_save_path}"
        )
        docs = self.prep_docs(clean_text_dict)
        vector_store = None
        n = len(docs)
        ch_sz = 50
        for ch_i in range(-(-n // ch_sz)):
            start = ch_i * ch_sz
            stop = start + ch_sz
            if vector_store is None:
                vector_store = FAISS.from_documents(docs[start:stop], self.embeddings)
            else:
                sleep(0.5)
                vector_store.add_documents(docs[start:stop])
        vector_store.save_local(self.vector_store_save_path)
        print(f"vector store created and saved to: {self.vector_store_save_path}")
        if test:
            print(
                vector_store.similarity_search_with_score(
                    "who is eligible for an educational license?"
                )
            )

    def get_vector_store(
        self,
    ):
        return FAISS.load_local(self.vector_store_save_path, self.embeddings)
