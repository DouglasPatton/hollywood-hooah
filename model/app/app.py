from flask import Flask, request, jsonify
from flask_cors import CORS

from ragchat.chatbots import RagChatSyntheticQ

# declare constants
HOST = '0.0.0.0'
PORT = 8081

# initialize flask application
app = Flask(__name__)
CORS(app)

@app.route('/api/predict', methods=['POST'])
def predict():
    print('about to predict')
    query = request.get_json()['query']
    print('from backend, query: ', query)
    rag_chatbot = RagChatSyntheticQ(
        max_docs=7,)
    ans = rag_chatbot.run_rag_chat(query)
    # return jsonify({"answer": ans})
    return {'chat_response':ans}

if __name__ == '__main__':
  # run web server
  app.run(host=HOST, port=PORT)
