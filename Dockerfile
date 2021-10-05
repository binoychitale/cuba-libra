FROM python:3.6-buster
RUN python -m pip install pyDistAlgo

COPY ./modules $HOME/cuba-libra/modules

#RUN python -m da $HOME/cuba-libra/modules/main.da 
