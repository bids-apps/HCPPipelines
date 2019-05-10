# Use Jessie for correct perl version
# https://mail.nmr.mgh.harvard.edu/pipermail/freesurfer/2016-May/045407.html
FROM neurodebian:jessie-non-free
ARG DEBIAN_FRONTEND=noninteractive

ENV LANG="C.UTF-8" \
    LC_ALL="C.UTF-8"

# Download FreeSurfer
RUN apt-get -qq update && \
    apt-get install -yq --no-install-recommends \
      bc \
      bzip2 \
      ca-certificates \
      curl \
      libgomp1 \
      perl-modules \
      tar \
      tcsh \
      wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
    wget -qO- ftp://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/6.0.0/freesurfer-Linux-centos6_x86_64-stable-pub-v6.0.0.tar.gz \
    | tar zxv -C /opt \
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
    echo "cHJpbnRmICJrcnp5c3p0b2YuZ29yZ29sZXdza2lAZ21haWwuY29tXG41MTcyXG4gKkN2dW12RVYzelRmZ1xuRlM1Si8yYzFhZ2c0RVxuIiA+IC9vcHQvZnJlZXN1cmZlci9saWNlbnNlLnR4dAo=" | base64 -d | sh

# Set up the environment
ENV OS=Linux \
    FS_OVERRIDE=0 \
    FIX_VERTEX_AREA= \
    SUBJECTS_DIR=/opt/freesurfer/subjects \
    FSF_OUTPUT_FORMAT=nii.gz \
    MNI_DIR=/opt/freesurfer/mni \
    LOCAL_DIR=/opt/freesurfer/local \
    FREESURFER_HOME=/opt/freesurfer \
    FSFAST_HOME=/opt/freesurfer/fsfast \
    MINC_BIN_DIR=/opt/freesurfer/mni/bin \
    MINC_LIB_DIR=/opt/freesurfer/mni/lib \
    MNI_DATAPATH=/opt/freesurfer/mni/data \
    FMRI_ANALYSIS_DIR=/opt/freesurfer/fsfast \
    PERL5LIB=/opt/freesurfer/mni/lib/perl5/5.8.5 \
    MNI_PERL5LIB=/opt/freesurfer/mni/lib/perl5/5.8.5 \
    PATH=/opt/freesurfer/bin:/opt/freesurfer/fsfast/bin:/opt/freesurfer/tktools:/opt/freesurfer/mni/bin:$PATH

# Install MCR 2016b
ENV MATLABCMD="/opt/matlabmcr-2016b/v91/toolbox/matlab" \
    MATLAB_COMPILER_RUNTIME="/opt/matlabmcr-2016b/v91" \
    LD_LIBRARY_PATH="/opt/matlabmcr-2016b/v91/runtime/glnxa64:/opt/matlabmcr-2016b/v91/bin/glnxa64:/opt/matlabmcr-2016b/v91/sys/os/glnxa64:$LD_LIBRARY_PATH"

RUN apt-get update -qq \
    && apt-get install -y -q --no-install-recommends \
       libxext6 \
       libxpm-dev \
       libxt6 \
       unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
    && echo "Downloading MATLAB Compiler Runtime ..." \
    && curl -fsSL --retry 5 -o /tmp/mcr.zip https://ssd.mathworks.com/supportfiles/downloads/R2016b/deployment_files/R2016b/installers/glnxa64/MCR_R2016b_glnxa64_installer.zip \
    && unzip -q /tmp/mcr.zip -d /tmp/mcrtmp \
    && /tmp/mcrtmp/install -destinationFolder /opt/matlabmcr-2016b -mode silent -agreeToLicense yes \
    && rm -rf /tmp/*

# Install miniconda2
ENV PATH="/usr/local/miniconda/bin:$PATH"
RUN curl -fsSLO https://repo.continuum.io/miniconda/Miniconda2-4.5.4-Linux-x86_64.sh && \
    bash Miniconda2-4.5.4-Linux-x86_64.sh -b -p /usr/local/miniconda && \
    rm Miniconda2-4.5.4-Linux-x86_64.sh && \
    conda config --add channels conda-forge && \
    conda install -y mkl mkl-service numpy nibabel pandas && sync && \
    conda clean -tipsy && sync && \
    pip install --no-cache-dir pybids[analysis]==0.6.3

# Install connectome-workbench
WORKDIR /opt
RUN wget -q https://ftp.humanconnectome.org/workbench/workbench-linux64-v1.3.2.zip -O wb.zip \
    && unzip wb.zip \
    && rm wb.zip
ENV CARET7DIR="/opt/workbench/bin_linux64"

# Install HCP Pipelines and MSM binaries
RUN apt-get -qq update && \
    apt-get install -yq --no-install-recommends gcc g++ libglu1 && \
    rm -rf /tmp/* && \
    wget -qO- https://github.com/Washington-University/Pipelines/archive/v4.0.0.tar.gz | tar xz -C /tmp && \
    mv /tmp/* /opt/HCP-Pipelines && \
    rm -rf /tmp/* && \
    wget -qO- https://www.doc.ic.ac.uk/~ecr05/MSM_HOCR_v2/MSM_HOCR_v2-download.tgz | tar xz -C /tmp && \
    mv /tmp/homes/ecr05/MSM_HOCR_v2/Ubuntu /opt/HCP-Pipelines/MSMBinaries && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /

ENV HCPPIPEDIR=/opt/HCP-Pipelines
ENV HCPPIPEDIR_Templates=${HCPPIPEDIR}/global/templates \
    HCPPIPEDIR_Bin=${HCPPIPEDIR}/global/binaries \
    HCPPIPEDIR_Config=${HCPPIPEDIR}/global/config \
    HCPPIPEDIR_PreFS=${HCPPIPEDIR}/PreFreeSurfer/scripts \
    HCPPIPEDIR_FS=${HCPPIPEDIR}/FreeSurfer/scripts \
    HCPPIPEDIR_PostFS=${HCPPIPEDIR}/PostFreeSurfer/scripts \
    HCPPIPEDIR_fMRISurf=${HCPPIPEDIR}/fMRISurface/scripts \
    HCPPIPEDIR_fMRIVol=${HCPPIPEDIR}/fMRIVolume/scripts \
    HCPPIPEDIR_tfMRI=${HCPPIPEDIR}/tfMRI/scripts \
    HCPPIPEDIR_dMRI=${HCPPIPEDIR}/DiffusionPreprocessing/scripts \
    HCPPIPEDIR_dMRITract=${HCPPIPEDIR}/DiffusionTractography/scripts \
    HCPPIPEDIR_Global=${HCPPIPEDIR}/global/scripts \
    HCPPIPEDIR_tfMRIAnalysis=${HCPPIPEDIR}/TaskfMRIAnalysis/scripts \
    MSMBINDIR=${HCPPIPEDIR}/MSMBinaries \
    MSMCONFIGDIR=${HCPPIPEDIR}/MSMConfig

## Install the validator
RUN wget -qO- https://deb.nodesource.com/setup_10.x | bash - && \
    apt-get update && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g bids-validator@1.2.3 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# install libopenblas
RUN apt-get update -qq \
    && apt-get install -y -q --no-install-recommends \
           libopenblas-base \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV LD_LIBRARY_PATH="/usr/lib/openblas-base/:$LD_LIBRARY_PATH"

# Install FSL now to ensure it is not removed
RUN curl https://fsl.fmrib.ox.ac.uk/fsldownloads/fsl-6.0.0-centos6_64.tar.gz \
         | tar -xz -C /usr/local

# Configure environment
ENV FSLDIR="/usr/local/fsl"
ENV PATH="$FSLDIR/bin:$PATH"

# upgrade our libstdc++
RUN echo "deb http://ftp.de.debian.org/debian stretch main" >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y libstdc++6

# overwrite matlab mcr shared object
RUN rm /opt/matlabmcr-2016b/v91/sys/os/glnxa64/libstdc++.so.6 && \
    ln -s /usr/lib/x86_64-linux-gnu/libstdc++.so.6 /opt/matlabmcr-2016b/v91/sys/os/glnxa64/libstdc++.so.6

# install gradient_unwarp.py (v1.0.3)
RUN pip install https://github.com/Washington-University/gradunwarp/archive/v1.0.3.zip

COPY run.py version /
RUN chmod +x /run.py

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
RUN powerline_config=$(echo $(cat /powerline-shell.json)) && \
      sed -i "/DEFAULT_CONFIG = [{]/,/[}]/cDEFAULT_CONFIG = $powerline_config" \
      /usr/local/miniconda/lib/python2.7/site-packages/powerline_shell/__init__.py

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
ENV PATH=/bind/scripts:$PATH

## add workbench to PATH
ENV PATH=/opt/workbench/bin_linux64:$PATH

# setup singularity compatible entry points to run the initialization script
RUN /usr/bin/env \
| sed  '/^HOME/d' \
| sed '/^HOSTNAME/d' \
| sed  '/^USER/d' \
| sed '/^PWD/d' >> /environment && \
chmod 755 /environment

COPY entry_init.sh /singularity
RUN chmod 755 /singularity

RUN echo 'source $FSLDIR/etc/fslconf/fsl.sh' >> /singularity

ENTRYPOINT ["/singularity"]

