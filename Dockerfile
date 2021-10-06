FROM python:3.6-buster
COPY requirements.txt .
RUN python -m pip install -r requirements.txt