FROM python:3.6-buster
COPY ./modules $HOME/cuba-libra/modules
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

#RUN python -m da $HOME/cuba-libra/modules/main.da 
