from joblib import hash as jhash

# pdf_reader
REFERENCE_FOLDER='references'

# doc_store
DB_NAME='docs'
COLLECTION_NAME='pdf'
KEYS=['folder','file_name', 'page_number']

# question_store
Q_DB_NAME = 'synthetic-questions'
Q_COLLECTION_NAME = 'questions'
Q_KEYS = ['folder','file_name', 'page_number', 'question_number']
TOKENS_PER_SYNTH_QUESTION = 200
# answer_store
A_DB_NAME = 'answers-to-synthetic-questions'
A_COLLECTION_NAME = 'answers'
A_KEYS = ['folder','file_name', 'page_number', 'question', 'template']
# text_embedder
MAX_TOKENS_REF_TEXT = 4000
MIN_TOKENS_REF_TEXT = 20

DEBUG = True  # extra printing, saves extra attributes


# text_embedder and chatbot
vs_id = jhash(
    [MAX_TOKENS_REF_TEXT, ]
)
VECTOR_STORE_SAVE_PATH = f"vector_stores/faiss_index_{vs_id}"
QUESTIONS_VECTOR_STORE_SAVE_PATH = "questions/questions_FAISS_index"


# chatbot
##retriever
MAX_TOKENS_CONTEXT = 8000
MAX_DOCS_RETRIEVER = 15

# place holder for types of entities, not currently used
ENTITY_CLASSES = [
    'production company',
    
]

TEST_QUERIES = [
    "What kinds of obligations does a production company have?",
    "Have movies related to sexual identity of members of the armed forces been part of the project?",
    "What movies have used aircraft carriers?",
    "What movies have used fighter jets?",
    "Tell me detailed information about how aircraft carriers have been used.",
    "What kinds of military equipment appear in movies in the project?",
    
]


