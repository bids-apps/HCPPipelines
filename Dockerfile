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
