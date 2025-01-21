FROM python:3.8
WORKDIR /exerscope

COPY ./requirements.txt /exerscope/requirements.txt

RUN apt-get update
RUN apt-get -y install graphviz graphviz-dev
RUN pip install pygraphviz

RUN pip3 install -r /exerscope/requirements.txt

COPY ./analysis /exerscope/analysis
COPY ./dataset /exerscope/dataset
COPY ./Experiment_Results /exerscope/Experiment_Results
COPY ./scripts /exerscope/scripts

COPY model_config.json /exerscope/model_config.json
COPY run.sh /exerscope/run.sh

CMD ["bash", "run.sh"]