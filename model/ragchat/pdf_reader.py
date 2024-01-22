from langchain.document_loaders import PyPDFLoader
from ragchat.configs import DEBUG
class PdfReader:
    def __init__(self, max_pages=None, debug=DEBUG):
        self.max_pages=max_pages

        loader = PyPDFLoader('./docs/RachelGreenCV.pdf')
documents = loader.load()