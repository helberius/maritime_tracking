FROM continuumio/miniconda:latest

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV PATH /opt/conda/bin:$PATH

ENV POLLING_SCRIPT '/app_tracking'
ENV POLLING_SOURCE '/app_tracking'
ENV AUTOCLONING 'False'
ENV RABBIT_HOST 'container_rabbit'

RUN apt-get update
RUN apt-get install -y git
RUN apt-get install -y iputils-ping

RUN mkdir /app
RUN cd /app
RUN conda install -c conda-forge pika -y
RUN conda install -c anaconda requests -y
RUN conda install -c conda-forge geopy -y
RUN conda install -c conda-forge elasticsearch -y
RUN conda install pandas -y

#ENTRYPOINT "echo" "container_dev"
CMD ["/bin/bash"]
