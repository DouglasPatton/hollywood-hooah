from ragchat.pdf_reader import PdfReader
from ragchat.configs import DEBUG, REFERENCE_FOLDER, DB_NAME, COLLECTION_NAME
import os




if __name__=="__main__":
    pg=None
    reader=PdfReader(page_list=None,
                     debug=DEBUG,
                     reference_folder=REFERENCE_FOLDER,
                     db_name=DB_NAME,
                     collection_name=COLLECTION_NAME,
                     mp_proc_count=10,
                     drop_output=True,
                     )
    print('starting processing of pdf pages')
    _=reader.process_pdf_pages()