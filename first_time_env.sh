#!/bin/bash
rm -r env
python -m venv env
source env/bin/activate
pip install --upgrade pip
# pip install -r requirements.txt
pip install langchain==0.1 joblib faiss-cpu jupyterlab jupyterlab-search-replace beautifulsoup4 inscriptis html2text pandas pycld2 openai tiktoken matplotlib
pip freeze > requirements.txt
cp requirements.txt model/ #for docker build
pip wheel -e model -w model/wheels
pip install -e model
