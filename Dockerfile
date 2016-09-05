FROM bids/base_hcppipelines:v3.17.0-3

RUN wget --quiet https://repo.continuum.io/miniconda/Miniconda3-4.0.5-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh

ENV CONDA=/opt/conda/bin

RUN $CONDA/conda install -y pip
RUN $CONDA/pip install https://github.com/chrisfilo/pybids/archive/0159116f0b9583ad1fec1ec36bae16ed949bf466.zip
RUN $CONDA/conda install -y six

COPY run.py /run.py
RUN chmod +x /run.py

COPY version /version
ENTRYPOINT ["/run.py"]
