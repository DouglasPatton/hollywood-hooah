# summarize documents to see how the html cleaning is doing
from typing import List

from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import VectorStore
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever


class MultiRetrieverCombiner(BaseRetriever):
    vector_store: VectorStore
    max_tokens_context: int
    llm: ChatOpenAI
    metadata: list
    max_docs: int

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        docs = self.vector_store.similarity_search_with_score(
            query, k=self.max_docs, fetch_k=2 * self.max_docs
        )
        toks = 0
        doc_text = ""
        for i, d in enumerate(docs):
            text_i = d[0].page_content
            new_toks = self.llm.get_num_tokens(text_i)
            if toks + new_toks > self.max_tokens_context:
                i += -1
                print(
                    f"merge stopped at {i} docs due to max tokens: {self.max_tokens_context}"
                )
                break
            elif i > self.max_docs:
                i += -1
                print(f"merge stopped at {i} docs due to max docs: {self.max_docs}")
                break
            else:
                toks += new_toks
                doc_text += f"\n\n{text_i}"
                meta_i = d[0].metadata
                meta_i["similarity_score"] = d[1]
                self.metadata.append(meta_i)
        print(f"{i} documents merged by MultiRetrieverCombiner")
        docs_out = [
            Document(page_content=doc_text, metadata={"metadata_list": self.metadata})
        ]
        print(
            f"MultiRetrieverCombiner output num tokens: {self.llm.get_num_tokens(doc_text)}"
        )
        return docs_out


class StaticRetriever(BaseRetriever):
    # returns whatever documents were passed in when instantiated
    docs: List[Document]

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        return self.docs


class MetaRetriever(BaseRetriever):
    # retrieves metadata too
    vector_store: VectorStore
    # retriever:vs.as_retriever()
    metadata: List

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        docs = self.vector_store.similarity_search_with_score(query, k=5)
        # self.metadata = [d[0].metadata for d in docs]
        for d in docs:
            self.metadata.append({**d[0].metadata, "similarity_score": d[1]})
        return docs
