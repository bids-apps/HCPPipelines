FROM monicaycli/bids_hcp_birc:base
# https://github.com/monicaycli/HCPPipelines/tree/uconn_birc_base

# Customization for UConn BIRC

# UI improvement
## text editor: VIM
RUN apt-get update -qq \
    && apt-get install -y \
       vim \
    && apt-get clean

## fancy bash prompt: powerline shell
RUN pip install powerline-shell
COPY bashrc /tmp/tmp.bashrc
RUN cat /tmp/tmp.bashrc >> /etc/bash.bashrc && rm /tmp/tmp.bashrc
COPY config_powerline-shell.json /powerline-shell.json

# copy updated run.py
COPY run.py version /
RUN chmod +x /run.py

# Directories
RUN mkdir /share && mkdir /scratch && mkdir /local-scratch

## binds
RUN mkdir -p /bind/data_in && \
  mkdir -p /bind/data_out && \
  mkdir -p /bind/scripts

## PREpend user scripts to the path
ENV PATH /bind/scripts:$PATH

## add workbench to PATH
ENV PATH /opt/workbench/bin_linux64:$PATH

###############################################################################
# bidskit (https://github.com/rhancockn/bidskit)

# Install updates, Python3 for BIDS conversion script, Pip3 for Python to pull
# the pydicom module git and make for building DICOM convertor from source +
# related dependencies Clean up after to keep image size compact!
RUN apt-get -qq update && \
apt-get install -y build-essential libjpeg-dev python3 python3-pip git cmake pkg-config pigz && \
apt-get clean -y

# Pull Chris Rorden's dcm2niix latest version from github and compile from source
# Not including support for JPEG2000(optional -DUSE_OPENJPEG flag) and optional
# -DBATCH_VERSION flag (for batch processing binary dcm2niibatch
# Include those flags with cmake, if required.
RUN cd /tmp && git clone https://github.com/rordenlab/dcm2niix.git && cd dcm2niix && mkdir build && \
        cd build && cmake .. && make && make install

#dcm2niix executable has been created on /usr/local/bin within the container

#Create a dir to store python script
RUN mkdir /app
COPY bidskit/* /app/
ENV PATH /app:$PATH

#Install required python depencendies (pydicom)
RUN pip3 install pydicom
RUN pip3 install numpy

###############################################################################

# setup singularity compatible entry points to run the initialization script
RUN /usr/bin/env \
| sed  '/^HOME/d' \
| sed '/^HOSTNAME/d' \
| sed  '/^USER/d' \
| sed '/^PWD/d' >> /environment && \
chmod 755 /environment

COPY entry_init.sh /singularity
RUN chmod 755 /singularity

ENTRYPOINT ["/singularity"]

