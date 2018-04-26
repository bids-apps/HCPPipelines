#!/bin/bash 

set -x

echo "This script must be SOURCED to correctly setup the environment prior to running any of the other HCP scripts contained here"

export OS=Linux
export FS_OVERRIDE=0
export FIX_VERTEX_AREA=
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
export PATH=/opt/freesurfer/bin:/opt/freesurfer/fsfast/bin:/opt/freesurfer/tktools:/opt/freesurfer/mni/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH

export FSLDIR=/usr/share/fsl/5.0
export FSL_DIR="${FSLDIR}"
export FSLOUTPUTTYPE=NIFTI_GZ
export PATH=/usr/lib/fsl/5.0:$PATH
export FSLMULTIFILEQUIT=TRUE
export POSSUMDIR=/usr/share/fsl/5.0
export LD_LIBRARY_PATH=/usr/lib/fsl/5.0
export FSLTCLSH=/usr/bin/tclsh
export FSLWISH=/usr/bin/wish
export FSLOUTPUTTYPE=NIFTI_GZ

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
export MSMBin=${HCPPIPEDIR}/MSMBinaries
