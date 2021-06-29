## HCP Pipelines BIDS App

This a [BIDS App](https://bids-apps.neuroimaging.io) wrapper for [HCP Pipelines](https://github.com/Washington-University/Pipelines) [v4.3.0](https://github.com/Washington-University/HCPpipelines/releases/tag/v4.3.0).
Like every BIDS App it consists of a container that includes all of the dependencies and run script that parses a [BIDS dataset](http://bids.neuroimaging.io).
BIDS Apps run on Windows, Linux, Mac as well as HPCs/clusters.

To convert DICOMs from your HCP-Style (CMRR) acquisitions to BIDS try using [heudiconv](https://github.com/nipy/heudiconv) with this [heuristic file](https://github.com/nipy/heudiconv/blob/master/heudiconv/heuristics/cmrr_heuristic.py).

### Description

The HCP Pipelines product is a set of tools (primarily, but not exclusively,
shell scripts) for processing MRI images for the [Human Connectome Project][HCP].
Among other things, these tools implement the Minimal Preprocessing Pipeline
(MPP) described in [Glasser et al. 2013][GlasserEtAl].

**This BIDS App requires that each subject has at least one T1w and one T2w scan.** Lack fMRI or dMRI scans is handled robustly.  Note that while anatomicals (T1w, T2w scans) can be processed without a fieldmap, a fieldmap is mandatory for processing fMRI scans. Support for the HCP-Pipelines 'legacy' processing mode will be added in an upcoming release.



### Documentation

[Release Notes, Installation, and Usage][release-install-use]

### How to report errors
Discussion of HCP Pipeline usage and improvements can be posted to the
hcp-users discussion list. Sign up for hcp-users at
[http://humanconnectome.org/contact/#subscribe][hcp-users-subscribe].

Please open an issue if you encounter errors building this BIDS App or believe you have encountered an error specific to the BIDS App wrapper.

### Acknowledgements
Please cite [Glasser et al. 2013][GlasserEtAl] and [Smith et al. 2013][SmithEtAl].

### Usage
This App has the following command line arguments:

	usage: run.py [-h]
	              [--participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]]
	              [--session_label SESSION_LABEL [SESSION_LABEL ...]]
	              [--n_cpus N_CPUS]
	              [--stages {PreFreeSurfer,FreeSurfer,PostFreeSurfer,fMRIVolume,fMRISurface} [{PreFreeSurfer,FreeSurfer,PostFreeSurfer,fMRIVolume,fMRISurface} ...]]
	              [--coreg {MSMSulc,FS}] [--gdcoeffs GDCOEFFS] --license_key
	              LICENSE_KEY [-v] [--anat_unwarpdir {x,y,z,-x,-y,-z}]
	              [--skip_bids_validation]
	              bids_dir output_dir {participant}
	
	HCP Pipelines BIDS App (T1w, T2w, fMRI)
	
	positional arguments:
	  bids_dir              The directory with the input dataset formatted
	                        according to the BIDS standard.
	  output_dir            The directory where the output files should be stored.
	                        If you are running group level analysis this folder
	                        should be prepopulated with the results of
	                        theparticipant level analysis.
	  {participant}         Level of the analysis that will be performed. Multiple
	                        participant level analyses can be run independently
	                        (in parallel) using the same output_dir.
	
	optional arguments:
	-h, --help            show this help message and exit
	--participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]
							The label of the participant that should be analyzed.
							The label corresponds to sub-<participant_label> from
							the BIDS spec (so it does not include "sub-"). If this
							parameter is not provided all subjects should be
							analyzed. Multiple participants can be specified with
							a space separated list.
	--session_label SESSION_LABEL [SESSION_LABEL ...]
							The label of the session that should be analyzed. The
							label corresponds to ses-<session_label> from the BIDS
							spec (so it does not include "ses-"). If this
							parameter is not provided, all sessions should be
							analyzed. Multiple sessions can be specified with a
							space separated list.
	--n_cpus N_CPUS       Number of CPUs/cores available to use.
	--stages {PreFreeSurfer,FreeSurfer,PostFreeSurfer,fMRIVolume,fMRISurface} [{PreFreeSurfer,FreeSurfer,PostFreeSurfer,fMRIVolume,fMRISurface} ...]
							Which stages to run. Space separated list.
	--coreg {MSMSulc,FS}  Coregistration method to use
	--gdcoeffs GDCOEFFS   Path to gradients coefficients file
	--license_key LICENSE_KEY
							FreeSurfer license key - letters and numbers after "*"
							in the email you received after registration. To
							register (for free) visit
							https://surfer.nmr.mgh.harvard.edu/registration.html
	-v, --version         show program's version number and exit
	--anat_unwarpdir {x,y,z,x-,y-,z-}
							Unwarp direction for 3D volumes
	--skip_bids_validation, --skip-bids-validation
							assume the input dataset is BIDS compliant and skip
							the validation
	--processing_mode {hcp,legacy,auto}, --processing-mode {hcp,legacy,auto}
							Control HCP-Pipeline modehcp (HCPStyleData): require
							T2w and fieldmap modalitieslegacy (LegacyStyleData):
							always ignore T2w and fieldmapsauto: use T2w and/or
							fieldmaps if available
	--doslicetime         Apply slice timing correction as part of fMRIVolume.

To run it in participant level mode (for one participant):

    docker run -i --rm \
    -v /Users/filo/data/ds005:/bids_dataset:ro \
    -v /Users/filo/outputs:/outputs \
    bids/hcppipelines \
    /bids_dataset /outputs participant --participant_label 01 --license_key "XXXXXX"

### Commercial use

This BIDS App incorporates several **non-free** packages required for the HCP Pipeline, including:

- [MSM](https://github.com/ecr05/MSM_HOCR)
- [FreeSurfer](https://surfer.nmr.mgh.harvard.edu/)
- [FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/Licence)
- [MATLAB Runtime](https://www.mathworks.com/products/compiler/matlab-runtime.html)


If you are considering commercial use of this App please consult the relevant licenses.

### TODO

   - [ ] Add DiffusionProcessing stage
   - [ ] More testing for fMRI with different resolution
   - [ ] Run fMRI runs in parallel (when n_cpus present)
   - [ ] Add support for TOPUP and GE fieldmaps for structural scans (please get in touch if you can provide sample data)
   - [ ] Add support for GE fieldmaps for fMRI scans (please get in touch if you can provide sample data)
   - [ ] Avoid copying fsaverage folder for every participant
   - [ ] Add ICA FIX stage
   - [ ] Add group level analysis
   - [ ] Add task fMRI model fitting

[HCP]: http://www.humanconnectome.org
[GlasserEtAl]: http://www.ncbi.nlm.nih.gov/pubmed/23668970
[SmithEtAl]: http://www.ncbi.nlm.nih.gov/pubmed/23702415
[release-install-use]: hhttps://github.com/Washington-University/HCPpipelines/wiki/Installation-and-Usage-Instructions
[hcp-users-subscribe]: http://humanconnectome.org/contact/#subscribe
