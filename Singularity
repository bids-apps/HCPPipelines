Bootstrap: docker
From: ubuntu:xenial-20190515
%files
run.py /
version /
%post

LANG="C.UTF-8"
LC_ALL="C.UTF-8"

# Download FreeSurfer
apt-get -qq update && \
apt-get install -yq --no-install-recommends \
bc \
bzip2 \
ca-certificates \
curl \
libgomp1 \
perl-modules \
tar \
tcsh \
wget \
libxmu6 && \
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
OS=Linux
FS_OVERRIDE=0
FIX_VERTEX_AREA=\
SUBJECTS_DIR=/opt/freesurfer/subjects
FSF_OUTPUT_FORMAT=nii.gz
MNI_DIR=/opt/freesurfer/mni
LOCAL_DIR=/opt/freesurfer/local
FREESURFER_HOME=/opt/freesurfer
FSFAST_HOME=/opt/freesurfer/fsfast
MINC_BIN_DIR=/opt/freesurfer/mni/bin
MINC_LIB_DIR=/opt/freesurfer/mni/lib
MNI_DATAPATH=/opt/freesurfer/mni/data
FMRI_ANALYSIS_DIR=/opt/freesurfer/fsfast
PERL5LIB=/opt/freesurfer/mni/lib/perl5/5.8.5
MNI_PERL5LIB=/opt/freesurfer/mni/lib/perl5/5.8.5
PATH=/opt/freesurfer/bin:/opt/freesurfer/fsfast/bin:/opt/freesurfer/tktools:/opt/freesurfer/mni/bin:$PATH


apt-get update -qq \
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
# still need python 2 for gradunwarp
PATH="/usr/local/miniconda/bin:$PATH"
curl -fsSLO https://repo.continuum.io/miniconda/Miniconda2-4.5.4-Linux-x86_64.sh && \
bash Miniconda2-4.5.4-Linux-x86_64.sh -b -p /usr/local/miniconda && \
rm Miniconda2-4.5.4-Linux-x86_64.sh && \
conda config --add channels conda-forge && \
conda install -y mkl=2019.3 mkl-service=2.0.2 numpy=1.16.4 nibabel=2.4.1 pandas=0.24.2 && sync && \
conda clean -tipsy && sync && \
pip install --no-cache-dir pybids==0.9.1

# Install connectome-workbench
cd /opt
apt-get -qq update && \
apt-get install -yq libfreetype6 libglib2.0 && \
wget -q https://ftp.humanconnectome.org/workbench/workbench-linux64-v1.3.2.zip -O wb.zip \
&& unzip wb.zip \
&& rm wb.zip && \
apt-get clean && \
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
CARET7DIR="/opt/workbench/bin_linux64"

# Install HCP Pipelines and MSM binaries
apt-get -qq update && \
apt-get install -yq --no-install-recommends gcc g++ libglu1 && \
rm -rf /tmp/* && \
wget -qO- https://github.com/Washington-University/HCPpipelines/archive/v4.0.0.tar.gz | tar xz -C /tmp && \
mv /tmp/* /opt/HCP-Pipelines && \
mkdir /opt/HCP-Pipelines/MSMBinaries && \
wget -q https://github.com/ecr05/MSM_HOCR/releases/download/1.0/msm_ubuntu14.04 -O /opt/HCP-Pipelines/MSMBinaries/msm &&  \
chmod 755 /opt/HCP-Pipelines/MSMBinaries/msm && \
apt-get clean && \
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

cd /

HCPPIPEDIR=/opt/HCP-Pipelines
HCPPIPEDIR_Templates=${HCPPIPEDIR}/global/templates
HCPPIPEDIR_Bin=${HCPPIPEDIR}/global/binaries
HCPPIPEDIR_Config=${HCPPIPEDIR}/global/config
HCPPIPEDIR_PreFS=${HCPPIPEDIR}/PreFreeSurfer/scripts
HCPPIPEDIR_FS=${HCPPIPEDIR}/FreeSurfer/scripts
HCPPIPEDIR_PostFS=${HCPPIPEDIR}/PostFreeSurfer/scripts
HCPPIPEDIR_fMRISurf=${HCPPIPEDIR}/fMRISurface/scripts
HCPPIPEDIR_fMRIVol=${HCPPIPEDIR}/fMRIVolume/scripts
HCPPIPEDIR_tfMRI=${HCPPIPEDIR}/tfMRI/scripts
HCPPIPEDIR_dMRI=${HCPPIPEDIR}/DiffusionPreprocessing/scripts
HCPPIPEDIR_dMRITract=${HCPPIPEDIR}/DiffusionTractography/scripts
HCPPIPEDIR_Global=${HCPPIPEDIR}/global/scripts
HCPPIPEDIR_tfMRIAnalysis=${HCPPIPEDIR}/TaskfMRIAnalysis/scripts
MSMBINDIR=${HCPPIPEDIR}/MSMBinaries
MSMCONFIGDIR=${HCPPIPEDIR}/MSMConfig

## Install the validator
wget -qO- https://deb.nodesource.com/setup_10.x | bash - && \
apt-get update && \
apt-get install -y --no-install-recommends nodejs && \
npm install -g bids-validator@1.2.3 && \
apt-get clean && \
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install FSL
curl https://fsl.fmrib.ox.ac.uk/fsldownloads/fsl-6.0.1-centos6_64.tar.gz \
| tar -xz -C /usr/local && \
/usr/local/fsl/etc/fslconf/fslpython_install.sh -f /usr/local/fsl


# Configure environment
FSLDIR=/usr/local/fsl
FSL_DIR="${FSLDIR}"
FSLOUTPUTTYPE=NIFTI_GZ
PATH=${FSLDIR}/bin:$PATH
FSLMULTIFILEQUIT=TRUE
POSSUMDIR=${FSLDIR}
LD_LIBRARY_PATH=${FSLDIR}/lib:$LD_LIBRARY_PATH
FSLTCLSH=/usr/bin/tclsh
FSLWISH=/usr/bin/wish
FSLOUTPUTTYPE=NIFTI_GZ

# install gradient_unwarp.py (v1.1.0)
cd /tmp
wget -q https://github.com/Washington-University/gradunwarp/archive/v1.1.0.zip && \
unzip v1.1.0.zip && \
cd gradunwarp-1.1.0 && \
python setup.py install && \
rm -rf gradunwarp-1.1.0 v1.1.0.zip


# Fix Topup scripts

wget -q https://raw.githubusercontent.com/Washington-University/HCPpipelines/dc7aae3a7a1cae920b390500d85536681b14108c/global/scripts/TopupPreprocessingAll.sh -O /opt/HCP-Pipelines/global/scripts/TopupPreprocessingAll.sh

# Install MCR 2016b
MATLABCMD="/opt/matlabmcr-2016b/v91/toolbox/matlab"
MATLAB_COMPILER_RUNTIME="/opt/matlabmcr-2016b/v91"
LD_LIBRARY_PATH="/opt/matlabmcr-2016b/v91/runtime/glnxa64:/opt/matlabmcr-2016b/v91/bin/glnxa64:/opt/matlabmcr-2016b/v91/sys/os/glnxa64:$LD_LIBRARY_PATH"


# overwrite matlab mcr shared object
rm /opt/matlabmcr-2016b/v91/sys/os/glnxa64/libstdc++.so.6 && \
ln -s /usr/lib/x86_64-linux-gnu/libstdc++.so.6 /opt/matlabmcr-2016b/v91/sys/os/glnxa64/libstdc++.so.6



chmod +x /run.py


%environment
export LANG="C.UTF-8"
export LC_ALL="C.UTF-8"
export OS=Linux
export FS_OVERRIDE=0
export FIX_VERTEX_AREA=\
export SUBJECTS_DIR=/opt/freesurfer/subjects
export FSF_OUTPUT_FORMAT=nii.gz
export MNI_DIR=/opt/freesurfer/mni
export LOCAL_DIR=/opt/freesurfer/local
export FREESURFER_HOME=/opt/freesurfer
export FSFAST_HOME=/opt/freesurfer/fsfast
export MINC_BIN_DIR=/opt/freesurfer/mni/bin
export MINC_LIB_DIR=/opt/freesurfer/mni/lib
export MNI_DATAPATH=/opt/freesurfer/mni/data
export FMRI_ANALYSIS_DIR=/opt/freesurfer/fsfast
export PERL5LIB=/opt/freesurfer/mni/lib/perl5/5.8.5
export MNI_PERL5LIB=/opt/freesurfer/mni/lib/perl5/5.8.5
export PATH=/opt/freesurfer/bin:/opt/freesurfer/fsfast/bin:/opt/freesurfer/tktools:/opt/freesurfer/mni/bin:$PATH
export PATH="/usr/local/miniconda/bin:$PATH"
export CARET7DIR="/opt/workbench/bin_linux64"
export HCPPIPEDIR=/opt/HCP-Pipelines
export HCPPIPEDIR_Templates=${HCPPIPEDIR}/global/templates
export HCPPIPEDIR_Bin=${HCPPIPEDIR}/global/binaries
export HCPPIPEDIR_Config=${HCPPIPEDIR}/global/config
export HCPPIPEDIR_PreFS=${HCPPIPEDIR}/PreFreeSurfer/scripts
export HCPPIPEDIR_FS=${HCPPIPEDIR}/FreeSurfer/scripts
export HCPPIPEDIR_PostFS=${HCPPIPEDIR}/PostFreeSurfer/scripts
export HCPPIPEDIR_fMRISurf=${HCPPIPEDIR}/fMRISurface/scripts
export HCPPIPEDIR_fMRIVol=${HCPPIPEDIR}/fMRIVolume/scripts
export HCPPIPEDIR_tfMRI=${HCPPIPEDIR}/tfMRI/scripts
export HCPPIPEDIR_dMRI=${HCPPIPEDIR}/DiffusionPreprocessing/scripts
export HCPPIPEDIR_dMRITract=${HCPPIPEDIR}/DiffusionTractography/scripts
export HCPPIPEDIR_Global=${HCPPIPEDIR}/global/scripts
export HCPPIPEDIR_tfMRIAnalysis=${HCPPIPEDIR}/TaskfMRIAnalysis/scripts
export MSMBINDIR=${HCPPIPEDIR}/MSMBinaries
export MSMCONFIGDIR=${HCPPIPEDIR}/MSMConfig
export FSLDIR=/usr/local/fsl
export FSL_DIR="${FSLDIR}"
export FSLOUTPUTTYPE=NIFTI_GZ
export PATH=${FSLDIR}/bin:$PATH
export FSLMULTIFILEQUIT=TRUE
export POSSUMDIR=${FSLDIR}
export LD_LIBRARY_PATH=${FSLDIR}/lib:$LD_LIBRARY_PATH
export FSLTCLSH=/usr/bin/tclsh
export FSLWISH=/usr/bin/wish
export FSLOUTPUTTYPE=NIFTI_GZ
export MATLABCMD="/opt/matlabmcr-2016b/v91/toolbox/matlab"
export MATLAB_COMPILER_RUNTIME="/opt/matlabmcr-2016b/v91"
export LD_LIBRARY_PATH="/opt/matlabmcr-2016b/v91/runtime/glnxa64:/opt/matlabmcr-2016b/v91/bin/glnxa64:/opt/matlabmcr-2016b/v91/sys/os/glnxa64:$LD_LIBRARY_PATH"
%runscript
cd /tmp
exec /bin/bash /run.py "$@"
%startscript
cd /tmp
exec /bin/bash /run.py "$@"