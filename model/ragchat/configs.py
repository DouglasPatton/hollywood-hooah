from joblib import hash as jhash

# pdf_reader
REFERENCE_FOLDER='references'



# text_embedder
MAX_TOKENS_REF_TEXT = 4000


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


ENTITY_CLASSES = [
    'production company',
    
]

TEST_QUERIES = [
    "What does Fusion 360 do?",
    "What's the difference between AutoCAD and Revit?",
    "Does AutoCAD LT do 3d?",
    "What's the latest release for Maya?",
    "Can I use fusion 360 on a Mac?,",
]


