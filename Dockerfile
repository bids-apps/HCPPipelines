FROM debian:wheezy

# Install FSL 5.0.6
RUN apt-get update && \
    apt-get install -y curl && \
    curl -sSL http://neuro.debian.net/lists/wheezy.us-tn.full >> /etc/apt/sources.list.d/neurodebian.sources.list && \
    sed -i 's/wheezy/wheezy-hcp500/' /etc/apt/sources.list.d/neurodebian.sources.list && \
    apt-key adv --recv-keys --keyserver hkp://pgp.mit.edu:80 0xA5D32F012649A5A9 && \
    apt-get update && \
    apt-get remove -y curl && \
    apt-get install -y fsl-core && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Configure environment
ENV FSLDIR=/usr/share/fsl/5.0
ENV FSL_DIR="${FSLDIR}"
ENV FSLOUTPUTTYPE=NIFTI_GZ
ENV PATH=/usr/lib/fsl/5.0:$PATH
ENV FSLMULTIFILEQUIT=TRUE
ENV POSSUMDIR=/usr/share/fsl/5.0
ENV LD_LIBRARY_PATH=/usr/lib/fsl/5.0:$LD_LIBRARY_PATH
ENV FSLTCLSH=/usr/bin/tclsh
ENV FSLWISH=/usr/bin/wish
ENV FSLOUTPUTTYPE=NIFTI_GZ

# Install FreeSurfer
RUN apt-get -y update \
    && apt-get install -y wget && \
    wget -qO- ftp://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/5.3.0-HCP/freesurfer-Linux-centos4_x86_64-stable-pub-v5.3.0-HCP.tar.gz | tar zxv -C /opt \
    --exclude='freesurfer/trctrain' \
    --exclude='freesurfer/subjects/fsaverage_sym' \
    --exclude='freesurfer/subjects/fsaverage3' \
    --exclude='freesurfer/subjects/fsaverage4' \
    --exclude='freesurfer/subjects/fsaverage5' \
    --exclude='freesurfer/subjects/fsaverage6' \
    --exclude='freesurfer/subjects/cvs_avg35' \
    --exclude='freesurfer/subjects/cvs_avg35_inMNI152' \
    --exclude='freesurfer/subjects/bert' \
    --exclude='freesurfer/subjects/V1_average' \
    --exclude='freesurfer/average/mult-comp-cor' \
    --exclude='freesurfer/lib/cuda' \
    --exclude='freesurfer/lib/qt' && \
    apt-get remove -y wget && \
    apt-get install -y tcsh bc tar libgomp1 perl-modules curl  && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN echo "cHJpbnRmICJrcnp5c3p0b2YuZ29yZ29sZXdza2lAZ21haWwuY29tXG41MTcyXG4gKkN2dW12RVYzelRmZ1xuRlM1Si8yYzFhZ2c0RVxuIiA+IC9vcHQvZnJlZXN1cmZlci9saWNlbnNlLnR4dAo=" | base64 -d | sh

# Set up the environment
ENV OS Linux
ENV FS_OVERRIDE 0
ENV FIX_VERTEX_AREA=
ENV SUBJECTS_DIR /opt/freesurfer/subjects
ENV FSF_OUTPUT_FORMAT nii.gz
ENV MNI_DIR /opt/freesurfer/mni
ENV LOCAL_DIR /opt/freesurfer/local
ENV FREESURFER_HOME /opt/freesurfer
ENV FSFAST_HOME /opt/freesurfer/fsfast
ENV MINC_BIN_DIR /opt/freesurfer/mni/bin
ENV MINC_LIB_DIR /opt/freesurfer/mni/lib
ENV MNI_DATAPATH /opt/freesurfer/mni/data
ENV FMRI_ANALYSIS_DIR /opt/freesurfer/fsfast
ENV PERL5LIB /opt/freesurfer/mni/lib/perl5/5.8.5
ENV MNI_PERL5LIB /opt/freesurfer/mni/lib/perl5/5.8.5
ENV PATH /opt/freesurfer/bin:/opt/freesurfer/fsfast/bin:/opt/freesurfer/tktools:/opt/freesurfer/mni/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH

# Install Connectome Workbench
RUN apt-get update && apt-get -y install connectome-workbench

ENV CARET7DIR=/usr/bin

# Install HCP Pipelines
RUN apt-get -y update \
    && apt-get install -y wget python-numpy && \
    wget https://github.com/Washington-University/Pipelines/archive/v3.17.0.tar.gz -O pipelines.tar.gz && \
    cd /opt/ && \
    tar zxvf /pipelines.tar.gz && \
    mv /opt/Pipelines-* /opt/HCP-Pipelines && \
    rm /pipelines.tar.gz && \
    cd / && \
    apt-get remove -y wget && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV HCPPIPEDIR=/opt/HCP-Pipelines
ENV HCPPIPEDIR_Templates=${HCPPIPEDIR}/global/templates
ENV HCPPIPEDIR_Bin=${HCPPIPEDIR}/global/binaries
ENV HCPPIPEDIR_Config=${HCPPIPEDIR}/global/config
ENV HCPPIPEDIR_PreFS=${HCPPIPEDIR}/PreFreeSurfer/scripts
ENV HCPPIPEDIR_FS=${HCPPIPEDIR}/FreeSurfer/scripts
ENV HCPPIPEDIR_PostFS=${HCPPIPEDIR}/PostFreeSurfer/scripts
ENV HCPPIPEDIR_fMRISurf=${HCPPIPEDIR}/fMRISurface/scripts
ENV HCPPIPEDIR_fMRIVol=${HCPPIPEDIR}/fMRIVolume/scripts
ENV HCPPIPEDIR_tfMRI=${HCPPIPEDIR}/tfMRI/scripts
ENV HCPPIPEDIR_dMRI=${HCPPIPEDIR}/DiffusionPreprocessing/scripts
ENV HCPPIPEDIR_dMRITract=${HCPPIPEDIR}/DiffusionTractography/scripts
ENV HCPPIPEDIR_Global=${HCPPIPEDIR}/global/scripts
ENV HCPPIPEDIR_tfMRIAnalysis=${HCPPIPEDIR}/TaskfMRIAnalysis/scripts
ENV MSMBin=${HCPPIPEDIR}/MSMBinaries

# RUN apt-get -y update \
#     && apt-get install -y wget bzip2 && \
#     wget --quiet https://repo.continuum.io/miniconda/Miniconda3-4.0.5-Linux-x86_64.sh -O ~/miniconda.sh && \
#     /bin/bash ~/miniconda.sh -b -p /opt/conda && \
#     rm ~/miniconda.sh && \
#     apt-get remove -y wget bzip2 && \
#     rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
#
# ENV CONDA=/opt/conda/bin
#
# RUN $CONDA/conda install -y pip
# RUN $CONDA/pip install https://github.com/chrisfilo/pybids/archive/0159116f0b9583ad1fec1ec36bae16ed949bf466.zip
# RUN $CONDA/conda install -y six

RUN apt-get update && apt-get install -y python-pip
RUN pip install https://github.com/chrisfilo/pybids/archive/0159116f0b9583ad1fec1ec36bae16ed949bf466.zip
RUN pip install six

COPY run.py /run.py
RUN chmod +x /run.py

COPY version /version
ENTRYPOINT ["/run.py"]
