Bootstrap: docker
From: bids/hcppipelines

%runscript

exec /run.py "$@"

%post

# Make script executable
chmod +x /run.py

# Make local folders
mkdir /share
mkdir /scratch
mkdir /local-scratch

# add variables to the environment file
echo "" >> /environment
echo "export FSLDIR=/usr/share/fsl/5.0" >> /environment
echo 'export FSL_DIR="${FSLDIR}"' >> /environment
echo "export FSLOUTPUTTYPE=NIFTI_GZ" >> /environment
echo "export PATH=/usr/lib/fsl/5.0:$PATH" >> /environment
echo "export FSLMULTIFILEQUIT=TRUE" >> /environment
echo "export POSSUMDIR=/usr/share/fsl/5.0" >> /environment
echo "export LD_LIBRARY_PATH=/usr/lib/fsl/5.0:$LD_LIBRARY_PATH" >> /environment
echo "export FSLTCLSH=/usr/bin/tclsh" >> /environment
echo "export FSLWISH=/usr/bin/wish" >> /environment
echo "export FSLOUTPUTTYPE=NIFTI_GZ" >> /environment
echo "export CARET7DIR=/usr/bin" >> /environment
echo "export HCPPIPEDIR=/opt/HCP-Pipelines" >> /environment
echo "export HCPPIPEDIR_Templates=/opt/HCP-Pipelines/global/templates" >> /environment
echo "export HCPPIPEDIR_Bin=/opt/HCP-Pipelines/global/binaries" >> /environment
echo "export HCPPIPEDIR_Config=/opt/HCP-Pipelines/global/config" >> /environment
echo "export HCPPIPEDIR_PreFS=/opt/HCP-Pipelines/PreFreeSurfer/scripts" >> /environment
echo "export HCPPIPEDIR_FS=/opt/HCP-Pipelines/FreeSurfer/scripts" >> /environment
echo "export HCPPIPEDIR_PostFS=/opt/HCP-Pipelines/PostFreeSurfer/scripts" >> /environment
echo "export HCPPIPEDIR_fMRISurf=/opt/HCP-Pipelines/fMRISurface/scripts" >> /environment
echo "export HCPPIPEDIR_fMRIVol=/opt/HCP-Pipelines/fMRIVolume/scripts" >> /environment
echo "export HCPPIPEDIR_tfMRI=/opt/HCP-Pipelines/tfMRI/scripts" >> /environment
echo "export HCPPIPEDIR_dMRI=/opt/HCP-Pipelines/DiffusionPreprocessing/scripts" >> /environment
echo "export HCPPIPEDIR_dMRITract=/opt/HCP-Pipelines/DiffusionTractography/scripts" >> /environment
echo "export HCPPIPEDIR_Global=/opt/HCP-Pipelines/global/scripts" >> /environment
echo "export HCPPIPEDIR_tfMRIAnalysis=/opt/HCP-Pipelines/TaskfMRIAnalysis/scripts" >> /environment
echo "export MSMBin=/opt/HCP-Pipelines/MSMBinaries" >> /environment
echo "export PYTHONPATH=''" >> /environment
echo 'export  OS=Linux' >> /environment
echo 'export  FS_OVERRIDE=0' >> /environment
echo 'export  SUBJECTS_DIR=/opt/freesurfer/subjects' >> /environment
echo 'export  FSF_OUTPUT_FORMAT=nii.gz' >> /environment
echo 'export  MNI_DIR=/opt/freesurfer/mni' >> /environment
echo 'export  LOCAL_DIR=/opt/freesurfer/local' >> /environment
echo 'export  FREESURFER_HOME=/opt/freesurfer' >> /environment
echo 'export  FSFAST_HOME=/opt/freesurfer/fsfast' >> /environment
echo 'export  MINC_BIN_DIR=/opt/freesurfer/mni/bin' >> /environment
echo 'export  MINC_LIB_DIR=/opt/freesurfer/mni/lib' >> /environment
echo 'export  MNI_DATAPATH=/opt/freesurfer/mni/data' >> /environment
echo 'export  FMRI_ANALYSIS_DIR=/opt/freesurfer/fsfast' >> /environment
echo 'export  PERL5LIB=/opt/freesurfer/mni/lib/perl5/5.8.5' >> /environment
echo 'export  MNI_PERL5LIB=/opt/freesurfer/mni/lib/perl5/5.8.5' >> /environment
echo 'export  PATH=/opt/freesurfer/bin:/opt/freesurfer/fsfast/bin:/opt/freesurfer/tktools:/opt/freesurfer/mni/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH' >> /environment
