from ragchat.chatbots import RagChatSyntheticQ


def query_rag_chatbot(query):
    rag_chatbot = rag_chatbot = RagChatSyntheticQ(
        max_docs=7,
    )
    ans = rag_chatbot.run_rag_chat(query)
    print(ans)


if __name__ == "__main__":
    query = str(input("please type your query: "))
    query_rag_chatbot(query)
