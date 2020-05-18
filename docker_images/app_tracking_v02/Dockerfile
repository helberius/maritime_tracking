FROM continuumio/miniconda:latest

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV PATH /opt/conda/bin:$PATH

ENV POLLING_SCRIPT '/app_tracking'
ENV POLLING_SOURCE '/app_tracking'
ENV POLLING_PERIODICITY '5'
ENV RABBIT_HOST 'rabbit_host'

RUN apt-get update       
RUN apt-get install -y git

RUN mkdir /app_tracking       
RUN cd /app_tracking        
RUN git clone https://github.com/helberius/maritime_tracking.git

RUN conda install -c conda-forge pika -y
RUN  conda install -c anaconda requests -y

#ENTRYPOINT ["python", $POLLING_SCRIPT, $POLLING_SOURCE, $POLLING_PERIODICITY ]
ENTRYPOINT "python" $POLLING_SCRIPT $POLLING_SOURCE $POLLING_PERIODICITY $RABBIT_HOST
CMD ["/bin/bash"]
