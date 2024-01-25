# from langchain.document_loaders import PyPDFLoader
from ragchat.configs import DEBUG, REFERENCE_FOLDER, DB_NAME, COLLECTION_NAME
from ragchat.doc_store import DocStore
from ragchat.mp_helper import MpHelper
import fitz
import os
import pathlib
from multiprocessing import Process


class PdfExtractor:
    def __init__(self,dir,name,path,add_to_db=True, db_name=DB_NAME,collection_name = COLLECTION_NAME):
        self.dir=dir
        self.name=name
        self.path=path
        self.add_to_db=add_to_db
        self.doc_store=DocStore(db_name=db_name, collection_name=collection_name,)

    def run(self):
        page_dict_list = PdfExtractor.process_text_blocks(self.dir,self.name,self.path)
        self.result=page_dict_list
        if self.add_to_db:
            self.doc_store.add_to_db(page_dict_list)
        
    
    def process_text_blocks(dir,name,path):
        doc=fitz.open(path)
        pages=[]
        for page in doc:
            blocks = page.get_text('dict')['blocks']
            blocks_text=[]
            for b_i,b in enumerate(blocks):
                blocks_text.append('')
                if 'lines' not in b:
                    continue
                for l in b['lines']:
                    if 'spans' not in l:
                        continue
                    for span in l['spans']:
                        blocks_text[b_i] += span['text']
            # TODO: add more clever features for breaking and merging text based on patterns in the pdfs, e.g., "page 5 of 5"
            pages.append("\n\n".join((blocks_text)))
        
        page_dict_list = [
            {'cleaned':pg, 'page_number':pg_num, 'folder':dir,
             'file_name':name, 'path': path} 
            for pg_num,pg in enumerate(pages)]
        return page_dict_list
        
        

class PdfReader:
    def __init__(self,
                 page_list=None,
                 debug=DEBUG,
                 reference_folder=REFERENCE_FOLDER,
                 db_name=DB_NAME, 
                 collection_name=COLLECTION_NAME,
                 mp_proc_count=12,
                 drop_output=True,
                 add_to_db=True,
                ):
        self.page_list=page_list
        self.debug=debug
        self.reference_folder=reference_folder
        self.db_name=db_name
        self.collection_name=collection_name
        self.mp_proc_count=mp_proc_count
        self.drop_output=drop_output
        self.add_to_db=add_to_db
        assert add_to_db or (not_drop_output), 'pdf reader must add_to_db or not drop_output'

    

    def process_pdf_pages(self,):
        if self.debug:
            self.skipped_paths=[]
        pdf_paths=[]
        for dir, subdirs, files in os.walk(self.reference_folder):
            print(files)
            for name in files:
                print(name)
                if name.endswith('.pdf'):
                    path=pathlib.PurePath(dir, name).as_posix()
                    if (
                        (self.page_list is not None)
                        and (path not in self.page_list) 
                        and (name not in self.page_list)
                        ):
                        if self.debug: 
                            self.skipped_paths.append(path)
                        continue
                    pdf_paths.append((dir,name,path))
        if self.debug:
            self.pdf_paths=pdf_paths
        drop_output=False if self.debug else True
        output=MpHelper().runAsMultiProc(PdfExtractor, pdf_paths,
                                         kwargs_list=dict(
                                             add_to_db=self.add_to_db,
                                             db_name=self.db_name,
                                             collection_name=self.collection_name),
                                         proc_count=self.mp_proc_count, 
                                         drop_output=self.drop_output)
        if self.drop_output:
            return None

        return output
                
            
                
            
            
        