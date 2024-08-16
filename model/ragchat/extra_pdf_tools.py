import s3fs
from PIL import Image
import matplotlib.pyplot as plt
import fitz
import boto3
import pandas as pd
import re
import io
from docx import Document
from traceback import format_exc
from ocr_tools import get_multi_lingual_ordered_text
from concurrent.futures import ThreadPoolExecutor

def view_pdf(
        self,
        filename,
        max_pages=100,
        page_start=1,
        pages_at_a_time=20,
        text=None,
        zoom=2  # to increase the resolution
    ):
        if filename[-4:].lower() != '.pdf':
            print(f'file does not have pdf extension. filename: {filename}')

        mat = fitz.Matrix(zoom, zoom)
        p_count=0
        for i,page in enumerate(self.stream_pdf(filename)):
            if i+1 < page_start:
                continue
            else:
                p_count+=1
            pix = page.get_pixmap(matrix=mat)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # display images
            plt.figure(figsize=(7,7), facecolor="w")
            plt.xticks(color="white")
            plt.yticks(color="white")
            plt.tick_params(bottom = False)
            plt.tick_params(left = False)
            if text:
                plt.text(0,-8,text)
            plt.imshow(img)
            if (p_count > 1) and (p_count % pages_at_a_time == 0):
                plt.close()

            if max_pages and (p_count >= max_pages):
                break
                
    def save_pdf(
        self,
        filename,
        save_path,
        page_num=1,
        zoom=3  # to increase the resolution
    ):
        if filename[-4:].lower() != '.pdf':
            print(f'file does not have pdf extension. filename: {filename}')

        mat = fitz.Matrix(zoom, zoom)
        
        for i,page in enumerate(self.stream_pdf(filename)):
            if i+1 != page_num:
                continue
        
            pix = page.get_pixmap(matrix=mat)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            img.save(save_path,'JPEG')
