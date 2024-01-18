from ragchat.configs import MAX_DOCS_RETRIEVER, VECTOR_STORE_SAVE_PATH

from ragchat.chatbots import RagChatbotMultiQA


def query_rag_chatbot(query):
    rag_chatbot = RagChatbotMultiQA(
        vector_store_save_path=VECTOR_STORE_SAVE_PATH,
        max_docs=MAX_DOCS_RETRIEVER,
        answer_select_strategy={"strategy_name": "merge_answers", "max_answers": 10},
    )

    ans = rag_chatbot.run_rag_chat(query)
    print(ans)


if __name__ == "__main__":
    query = str(input("please type your query: "))
    query_rag_chatbot(query)
