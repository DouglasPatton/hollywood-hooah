import os
# summarize documents to see how the html cleaning is doing
from time import sleep
from ragchat.configs import MIN_TOKENS_REF_TEXT,MAX_TOKENS_REF_TEXT,VECTOR_STORE_SAVE_PATH
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.text_splitter import (RecursiveCharacterTextSplitter)
from langchain_community.chat_models import ChatOpenAI
# from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores import FAISS


class TextEmbedder:
    def __init__(
        self,
        max_tokens_ref_text=MAX_TOKENS_REF_TEXT,
        min_tokens_ref_text=MIN_TOKENS_REF_TEXT,
        vector_store_save_path=VECTOR_STORE_SAVE_PATH,
    ):
        self.max_tokens_ref_text = max_tokens_ref_text
        self.min_tokens_ref_text = min_tokens_ref_text
        self.vector_store_save_path = vector_store_save_path
        self.llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)
        self.embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        
        
    @staticmethod
    def title_func(doc_dict):
        folder = doc_dict['folder'].split(os.sep)
        if folder[0]=='references': folder.pop(0)
    
        file_name=doc_dict['file_name']
        return f"Collection_Name: {' '.join(folder)}\nTitle: {file_name}"
        
    @staticmethod
    def add_title(doc_dict):
        title = TextEmbedder.title_func(doc_dict)
        return title + f"\n\n\n{doc_dict['cleaned']}"
            
    def split_text(self, clean_text, max_tokens):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=max_tokens,
            chunk_overlap=20,
            length_function=self.llm.get_num_tokens,
            is_separator_regex=False,
        )
        return text_splitter.split_text(clean_text)

    def prep_docs(self, doc_chunk):
        all_docs = []
        for text_result in doc_chunk:
            text = TextEmbedder.add_title(text_result)
            n_tokens_est = self.llm.get_num_tokens(text)
            if n_tokens_est < self.min_tokens_ref_text:
                continue
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
                        **{k:v for k,v in text_result.items() if k!='cleaned'},
                        "split_idx": i,
                        "n_splits": len(texts),
                    },
                )
                for i, text in enumerate(texts)
            ]
            all_docs.extend(docs)
        return all_docs

    def embed_docs(self, doc_chunk, ):
        docs = self.prep_docs(doc_chunk)
        if len(docs)==0:
            return
        try: 
            vector_store = self.get_vector_store()
        except:
            print(f'no existing vector store found at self.vector_store_save_path: {self.vector_store_save_path}')
            vector_store = None
        if vector_store is None:
            vector_store = FAISS.from_documents(docs, self.embeddings)
        else:
            sleep(0.5)
            vector_store.add_documents(docs)
        vector_store.save_local(self.vector_store_save_path)
        

    def get_vector_store(
        self,
    ):
        return FAISS.load_local(self.vector_store_save_path, self.embeddings)
