#!/bin/bash
deactivate
rm -r env
python -m venv env
source env/bin/activate
pip install --upgrade pip
# pip install -r requirements.txt
pip install langchain==0.1 joblib faiss-cpu jupyterlab jupyterlab-search-replace pandas langchain-openai pycld2 openai tiktoken matplotlib pymupdf pypdf pymongo
pip freeze > requirements.txt
cp requirements.txt model/ #for docker build
pip wheel -e model -w model/wheels 
pip install model/wheels/autochat-0-py3-none-any.whl