#!/bin/bash

deactivate
rm -r env
python -m venv env
source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp requirements.txt model/ #for docker build
pip wheel -e model -w model/wheels
pip install -e model
# pip install model/wheels/autochat-0-py3-none-any.whl