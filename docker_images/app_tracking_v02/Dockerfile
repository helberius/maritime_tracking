FROM continuumio/miniconda:latest

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV PATH /opt/conda/bin:$PATH

ARG POLLING_SCRIPT
ARG POLLING_SOURCE
ARG POLLING_PERIODICITY

RUN apt-get update       
RUN apt-get install -y git

RUN mkdir /app_tracking       
RUN cd /app_tracking        
RUN git clone https://github.com/helberius/maritime_tracking.git

RUN conda install -c conda-forge pika -y
RUN  conda install -c anaconda requests -y

ENTRYPOINT [ "/usr/bin/tini", $POLLING_SCRIPT, $POLLING_SOURCE, $POLLING_PERIODICITY ]
CMD [ "/bin/bash" ]
