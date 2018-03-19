# Use Ubuntu 14.04 LTS
FROM ubuntu:14.04

## Install the validator
RUN apt-get update && \
    apt-get install -y curl && \
    curl -sL https://deb.nodesource.com/setup_6.x | bash - && \
    apt-get remove -y curl && \
    apt-get install -y nodejs

RUN npm install -g bids-validator@0.25.07

# Download FreeSurfer
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

# Install FSL 5.0.9
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    curl -sSL http://neuro.debian.net/lists/trusty.us-ca.full >> /etc/apt/sources.list.d/neurodebian.sources.list && \
    apt-key adv --recv-keys --keyserver hkp://pgp.mit.edu:80 0xA5D32F012649A5A9 && \
    apt-get update && \
    apt-get install -y fsl-core=5.0.9-4~nd14.04+1 && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

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
RUN echo "cHJpbnRmICJrcnp5c3p0b2YuZ29yZ29sZXdza2lAZ21haWwuY29tXG41MTcyXG4gKkN2dW12RVYzelRmZ1xuRlM1Si8yYzFhZ2c0RVxuIiA+IC9vcHQvZnJlZXN1cmZlci9saWNlbnNlLnR4dAo=" | base64 -d | sh

# Get connectome workbench
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    curl -sSL http://neuro.debian.net/lists/trusty.us-ca.full >> /etc/apt/sources.list.d/neurodebian.sources.list && \
    apt-key adv --recv-keys --keyserver hkp://pgp.mit.edu:80 0xA5D32F012649A5A9 && \
    apt-get update && \
    apt-get -y install connectome-workbench=1.2.3-1~nd14.04+1

# Install HCP Pipelines
WORKDIR /
RUN apt-get -y update \
    && apt-get install -y --no-install-recommends python-numpy && \
    wget https://github.com/jokedurnez/Pipelines/archive/v0.1.0.tar.gz -O pipelines.tar.gz && \
    cd /opt/ && \
    tar zxvf /pipelines.tar.gz && \
    mv /opt/Pipelines-* /opt/HCP-Pipelines && \
    rm /pipelines.tar.gz && \
    cd /

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
ENV MSMCONFIGDIR=${HCPPIPEDIR}/MSMConfig
ENV CARET7DIR=/usr/bin

RUN apt-get update && apt-get install -y --no-install-recommends python-pip python-six python-nibabel python-setuptools
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt && \
    rm -rf ~/.cache/pip

ENV PYTHONPATH=""

# missing libraries
RUN echo deb http://security.ubuntu.com/ubuntu precise-security main >> /etc/apt/sources.list && \
    apt update && \
    apt install -y libxp6 libxmu6

WORKDIR /opt/freesurfer/bin
RUN wget https://raw.githubusercontent.com/freesurfer/freesurfer/d26114a201333f812d2cef67a338e2685c004d00/scripts/recon-all.v6.hires && \
    chmod +x /opt/freesurfer/bin/recon-all.v6.hires
RUN wget https://raw.githubusercontent.com/freesurfer/freesurfer/dev/scripts/tess1mm && \
    chmod +x /opt/freesurfer/bin/tess1mm
RUN wget -qO- https://fsl.fmrib.ox.ac.uk/fsldownloads/patches/eddy-patch-fsl-5.0.9/centos6/eddy_openmp > $FSLDIR/bin/eddy_openmp

COPY run.py /run.py
RUN chmod +x /run.py

COPY version /version
ENTRYPOINT ["/run.py"]
