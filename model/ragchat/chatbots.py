# summarize documents to see how the html cleaning is doing

from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain_community.chat_models import ChatOpenAI
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough
from ragchat.configs import (DEBUG,
# MIN_CHARS_REF_TEXT, KEYS, MIN_ENGL_SHARE_REF_TEXT, PARSER, 
QUESTIONS_VECTOR_STORE_SAVE_PATH, VECTOR_STORE_SAVE_PATH)
from ragchat.custom_retrievers import MetaRetriever, MultiRetrieverCombiner, StaticRetriever
# from ragchat.html_cleaner import HtmlCleaner
from ragchat.text_embedder import TextEmbedder


class RagChatbot:
    # simple, metadata doesn't work
    def __init__(self, vector_store_save_path="vector_stores/faiss_index_0"):
        self.vector_store_save_path = vector_store_save_path
        self.vector_store = TextEmbedder(
            vector_store_save_path=self.vector_store_save_path
        ).get_vector_store()
        self.llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)

    def get_pages(
        self,
    ):
        pages = []
        for meta in self.retriever.metadata:
            pages.append(meta["page"])
        return list(dict.fromkeys(pages))

    def run_rag_chat(self, user_query):
        retriever = MetaRetriever(vector_store=self.vector_store, metadata=[])
        self.retriever = retriever
        # retriever = self.vector_store.as_retriever(search_kwargs={"include_metadata": True})
        template = (
            "Answer the question based only on this:\n"
            "{context}\n\nQuestion: {question}"
        )
        prompt = ChatPromptTemplate.from_template(template)
        chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        return chain.invoke(user_query)


class RagChatSyntheticQ:
    ## queries question vector store to get list of questions, then gets doc(s) for each question and gets an answer, then asks llm to answer based on the question/answer pairs
    def __init__(
        self,
        vector_store_save_path=QUESTIONS_VECTOR_STORE_SAVE_PATH,
        max_docs=5,
    ):
        self.vector_store_save_path = vector_store_save_path
        self.max_docs = max_docs

        self.vector_store = TextEmbedder(
            vector_store_save_path=self.vector_store_save_path
        ).get_vector_store()
        self.llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)
        self.metadata = []

    def get_pages(
        self,
    ):
        pages = []
        for meta in self.metadata:
            pages.append(meta["pg"])
        return list(dict.fromkeys(pages))

    def run_rag_chat(self, query):
        def is_answer_good(ans):
            failed_answer_strings = [
                "is not mentioned",
                "is not provided",
                "is not specified",
                "is not explicitly mentioned in the provided context",
                "is not provided in the given document",
                "not specified in the given document",
                "is not specified in the provided document",
                "provided information does not specify",
            ]
            if any([failed_string in ans for failed_string in failed_answer_strings]):
                return False
            else:
                return True

        def merge_question_answers_chain(q_a_pairs, query):
            # answers_doc = Document(
            #     page_content="\n".join([f'  {answers[i].strip()}' for i in range(len(answers))]))

            answers_doc = Document(page_content="\n\n".join(q_a_pairs))
            retriever = StaticRetriever(docs=[answers_doc])
            template = (
                "Answer the question using only the best information from the following suggested question, answer pairs:\n"
                "{context}\n\nQuestion: {question}"
            )

            prompt = ChatPromptTemplate.from_template(template)
            chain = (
                {"context": retriever, "question": RunnablePassthrough()}
                | prompt
                | self.llm
                | StrOutputParser()
            )
            return chain.invoke(query)

        template = (
            "Answer the question based only on this:\n"
            "{context}\n\nQuestion: {question}"
        )
        prompt = ChatPromptTemplate.from_template(template)
        q_docs = self.vector_store.similarity_search_with_score(
            query, k=self.max_docs, fetch_k=2 * self.max_docs
        )

        for i, d in enumerate(q_docs):
            q = d[0].page_content
            ds=DocStore(db_name=DB_NAME, collection_name=COLLECTION_NAME,)
            docs = d[0].metadata["doc_list"] #multiple docs may have same question
            for doc_dict in docs:
                docs_with_text = ds.yield_from_db(
                    query={k:doc_dict[k] for k in KEYS},
                    chunk_size=None
                )
                assert len(docs_with_text)==0
            
                text_result = docs_with_text[0]
                doc = Document(
                    page_content=TextEmbedder.add_title(text_result),
                    metadata={k:v for k,v in text_result.items() if k!='cleaned'},
                )
                retriever = StaticRetriever(docs=[doc])
                chain = (
                    {"context": retriever, "question": RunnablePassthrough()}
                    | prompt
                    | self.llm
                    | StrOutputParser()
                )
                ans = chain.invoke(query)
                if is_answer_good(ans):
                    self.metadata.append(
                        {
                            "pg": pg,
                            "question": q,
                            "answer": ans,
                            "similarity_score": d[1],
                        }
                    )
        q_ans_pairs = [
            f"#{i}:\n    question: {qa_dict['question']}\n    answer: {qa_dict['answer']}"
            for qa_dict in self.metadata
        ]
        return merge_question_answers_chain(q_ans_pairs, query)


class RagChatbotMultiQA:
    ## queries each document retrieved and then asks llm to combine the answers or pick the best
    def __init__(
        self,
        vector_store_save_path=VECTOR_STORE_SAVE_PATH,
        max_docs=5,
        answer_select_strategy={"strategy_name": "first_good_answer"}
        ## two approaches: {'strategy_name':'first_good_answer'},{'strategy_name':'merge_answers',max_answers=10}):
    ):
        self.vector_store_save_path = vector_store_save_path
        self.max_docs = max_docs
        self.answer_select_strategy = answer_select_strategy
        ## answer_select_strategy has two approaches: {'strategy_name':'first_good_answer'}
        ## and {'strategy_name':'merge_answers',max_answers=10}

        self.vector_store = TextEmbedder(
            vector_store_save_path=self.vector_store_save_path
        ).get_vector_store()
        self.llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)
        self.metadata = []

    def get_pages(
        self,
    ):
        pages = []
        for meta in self.metadata:
            pages.append(meta["doc"].metadata["page"])
        return list(dict.fromkeys(pages))

    def run_rag_chat(self, query):
        def is_answer_good(ans):
            failed_answer_strings = [
                "is not mentioned",
                "is not provided",
                "is not specified",
                "is not explicitly mentioned in the provided context",
                "is not provided in the given document",
                "not specified in the given document",
                "is not specified in the provided document",
                "provided information does not specify",
            ]
            if any([failed_string in ans for failed_string in failed_answer_strings]):
                return False
            else:
                return True

        def merge_answers_chain(answers, query):
            # answers_doc = Document(
            #     page_content="\n".join([f'  {answers[i].strip()}' for i in range(len(answers))]))
            ans_txt = ""
            for i in range(len(answers)):
                ans_txt += f"    suggested answer #{i}: {answers[i].strip()}"
                if i + 1 < len(answers):
                    ans_txt += "\n"
            answers_doc = Document(page_content=ans_txt)
            retriever = StaticRetriever(docs=[answers_doc])
            template = (
                "Answer the question using only the best information from the following suggested answers:\n"
                "{context}\n\nQuestion: {question}"
            )

            prompt = ChatPromptTemplate.from_template(template)
            chain = (
                {"context": retriever, "question": RunnablePassthrough()}
                | prompt
                | self.llm
                | StrOutputParser()
            )
            return chain.invoke(query)

        docs = self.vector_store.similarity_search_with_score(
            query, k=self.max_docs, fetch_k=2 * self.max_docs
        )
        template = (
            "Answer the question based only on this:\n"
            "{context}\n\nQuestion: {question}"
        )
        prompt = ChatPromptTemplate.from_template(template)
        success = False
        answers = []
        for i, d in enumerate(docs):
            retriever = StaticRetriever(docs=[d[0]])
            chain = (
                {"context": retriever, "question": RunnablePassthrough()}
                | prompt
                | self.llm
                | StrOutputParser()
            )
            ans = chain.invoke(query)
            is_good = is_answer_good(ans)
            meta_dict = {
                "doc": d[0],
                "similarity_score": d[1],
                "answer": ans,
                "is_good": is_good,
            }
            self.metadata.append(meta_dict)
            if is_good:
                answers.append(ans)
                if self.answer_select_strategy["strategy_name"] == "first_good_answer":
                    return ans
                else:
                    assert (
                        self.answer_select_strategy["strategy_name"] == "merge_answers"
                    )
                    if len(answers) > self.answer_select_strategy["max_answers"]:
                        break
        if len(answers) == 0:
            return "unable to find a suitable answer"
        else:
            return merge_answers_chain(answers, query)


class RagChatbotMultiRetrieverCombiner:
    def __init__(
        self,
        vector_store_save_path="vector_stores/faiss_index_0",
        max_tokens_context=15000,
        max_docs=5,
    ):
        self.vector_store_save_path = vector_store_save_path
        self.vector_store = TextEmbedder(
            vector_store_save_path=self.vector_store_save_path
        ).get_vector_store()
        self.llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)
        self.max_tokens_context = max_tokens_context
        self.max_docs = max_docs

    def get_pages(
        self,
    ):
        pages = []
        for meta in self.retriever.metadata:
            pages.append(meta["page"])
        return list(dict.fromkeys(pages))

    def run_rag_chat(self, user_query):
        # retriever = self.vector_store.as_retriever(search_kwargs={"include_metadata": True, 'k':10})
        retriever = MultiRetrieverCombiner(
            vector_store=self.vector_store,
            max_tokens_context=self.max_tokens_context,
            llm=self.llm,
            metadata=[],
            max_docs=self.max_docs,
        )
        self.retriever = retriever
        template = (
            "Answer the question based only on this:\n"
            "{context}\n\nQuestion: {question}"
        )
        prompt = ChatPromptTemplate.from_template(template)
        chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        return chain.invoke(user_query)
