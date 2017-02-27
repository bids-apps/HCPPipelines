Bootstrap: docker
From: joke/hcppipelines

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
