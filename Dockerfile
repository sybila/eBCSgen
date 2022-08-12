# Use Base Dockerfile for using Storm
#####################################
FROM movesrwth/storm-basesystem:latest
MAINTAINER Matej Trojak <xtrojak@fi.muni.cz>

# Install base utilities
RUN apt-get update && \
    apt-get install -y build-essentials  && \
    apt-get install -y wget &&
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ARG no_threads=1

# Build Carl
############
WORKDIR /opt/
RUN git clone -b master14 https://github.com/ths-rwth/carl.git
RUN mkdir -p /opt/carl/build
WORKDIR /opt/carl/build

# Configure and Build Carl library
RUN cmake .. -DCMAKE_BUILD_TYPE=Release -DUSE_CLN_NUMBERS=ON -DUSE_GINAC=ON -DTHREAD_SAFE=ON
RUN make lib_carl -j $no_threads

# Build Storm
#############
RUN mkdir /opt/storm
WORKDIR /opt/storm

# Copy the content of the current local Storm repository into the Docker image
RUN git clone -b stable https://github.com/moves-rwth/storm.git
COPY storm/ .

# Switch to build directory
RUN mkdir -p /opt/storm/build
WORKDIR /opt/storm/build

# Configure Storm
RUN cmake .. -DCMAKE_BUILD_TYPE=Release -DSTORM_DEVELOPER=OFF -DSTORM_LOG_DISABLE_DEBUG=ON -DSTORM_PORTABLE=ON -DSTORM_USE_SPOT_SHIPPED=ON
RUN make resources -j $no_threads
RUN make storm -j $no_threads
RUN make binaries -j $no_threads
# Set path
ENV PATH="$PATH:/opt/storm/build/bin"

# Install conda
###############

# Install miniconda
ENV CONDA_DIR /opt/conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
     /bin/bash ~/miniconda.sh -b -p /opt/conda

# Put conda in path so we can use conda activate
ENV PATH=$CONDA_DIR/bin:$PATH

# Install eBCSgen
#################
conda install --channel bioconda --channel conda-forge eBCSgen
