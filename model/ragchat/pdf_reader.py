from langchain.document_loaders import PyPDFLoader
from ragchat.configs import DEBUG, REFERENCE_FOLDER
import fitz
import os
import pathlib

class PdfReader:
    def __init__(self,
                 max_pages=None,
                 page_list=None,
                 debug=DEBUG,
                 reference_folder=REFERENCE_FOLDER,
                ):
        self.max_pages=max_pages
        self.page_list=page_list
        self.debug=debug
        self.reference_folder=reference_folder

    def process_text_blocks(doc):
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
        return pages

    def process_pdf_pages(self,check_db_first=False):
        if self.debug:
            self.skipped_paths=[]
        pdf_paths=[]
        for dir, subdirs, files in os.walk(dir):
            for name in files:
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
        n_paths=len(pdf_paths)
        
        if self.debug:
            interval = 10 if n_paths<100 else 100 #for printing progress
        p_i=0
        for i,(dir,name,path) in enumerate(pdf_paths):
            if self.debug:
                if i%(n_paths//(interval+1))==0:
                    print(f'pdfs read: {round(100*(i+1)/n_paths,2)}')
            
            doc=fitz.open(path)
            pages=PDFReader.process_text_blocks(doc)
            [{'cleaned':page, 'page':pg_num, 'folder':dir, 'file_name':name, 'path': path for pg_num,pg in enumerate(pages)]
                
            
            
        