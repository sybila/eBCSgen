# Use Base Dockerfile for using Storm
#####################################
FROM movesrwth/storm:stable
MAINTAINER Matej Trojak <xtrojak@fi.muni.cz>

RUN apt-get install -y wget

# Install miniconda
###################

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
RUN /bin/bash ~/miniconda.sh -b -p /opt/conda
ENV PATH="/opt/conda/bin:$PATH"

# Install eBCSgen
#################
RUN  conda install --channel bioconda --channel conda-forge eBCSgen
