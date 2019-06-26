## HCP Pipelines BIDS App
This a [BIDS App](https://bids-apps.neuroimaging.io) wrapper for [HCP Pipelines](https://github.com/Washington-University/Pipelines).
Like every BIDS App it consists of a container that includes all of the dependencies and run script that parses a [BIDS dataset](http://bids.neuroimaging.io).
BIDS Apps run on Windows, Linux, Mac as well as HCPs/clusters.

To convert DICOMs from your HCP-Style (CMRR) acquisitions to BIDS try using [heudiconv](https://github.com/nipy/heudiconv) with this [heuristic file](https://github.com/nipy/heudiconv/blob/master/heudiconv/heuristics/cmrr_heuristic.py).

### Description
The HCP Pipelines product is a set of tools (primarily, but not exclusively,
shell scripts) for processing MRI images for the [Human Connectome Project][HCP].
Among other things, these tools implement the Minimal Preprocessing Pipeline
(MPP) described in [Glasser et al. 2013][GlasserEtAl].

**This BIDS App requires that each subject has at least one T1w and one T2w scan.** Lack fMRI or dMRI scans is handled robustly.  Note that while anatomicals (T1w, T2w scans) can be processed without a fieldmap, a fieldmap is mandatory for processing fMRI scans.

### Notes

This image includes FSL 5.0.9-5 from NeuroDebian as earlier versions of FSL are no longer available. This is not officially supported by HCP:

> NB: This version of the HCP Pipelines requires version 5.0.6 of FSL, not version 5.0.6 or greater. This version of the HCP Pipelines is not fully tested with the any version of FSL other than version 5.0.6. Preliminary testing has detected that there is a difference in behavior between version 5.0.6 of FSL and version 5.0.7 of FSL which, while it is an intentional improvement to FSL, is known to cause the Task Analysis pipeline in particular to fail.

> There is currently a separate branch in this repository named fsl-5.0.7-changes. That branch is not yet included in a released version of the code, but it contains changes to the Task Analysis pipeline that we expect will fix that pipeline so that it works with version 5.0.7 of FSL. These changes are not fully tested, but they are available to anyone who wants to run the Task Analysis pipeline and use FSL 5.0.7.


### Documentation
[Release Notes, Installation, and Usage][release-install-use]

### How to report errors
Discussion of HCP Pipeline usage and improvements can be posted to the
hcp-users discussion list. Sign up for hcp-users at
[http://humanconnectome.org/contact/#subscribe][hcp-users-subscribe]

### Acknowledgements
Please cite [Glasser et al. 2013][GlasserEtAl] and [Smith et al. 2013][SmithEtAl].

### Usage
This App has the following command line arguments:

    PS C:\Users\filo> docker run -ti --rm -v /c/Users/filo/hcp_example_bids:/bids_dir:ro -v /c/Users/filo/test_output:/output bids/hcppipelines --help
    usage: run.py [-h]
                  [--participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]]
                  [--n_cpus N_CPUS]
                  [--stages {PreFreeSurfer,FreeSurfer,PostFreeSurfer,fMRIVolume,fMRISurface,DiffusionPreprocessing} [{PreFreeSurfer,FreeSurfer,PostFreeSurfer,fMRIVolume,fMRISurface,DiffusionPreprocessing} ...]]
                  --license_key LICENSE_KEY [-v]
                  bids_dir output_dir {participant}

    HCP Pipeliens BIDS App (T1w, T2w, fMRI)

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
      --n_cpus N_CPUS       Number of CPUs/cores available to use.
      --stages {PreFreeSurfer,FreeSurfer,PostFreeSurfer,fMRIVolume,fMRISurface,DiffusionPreprocessing} [{PreFreeSurfer,FreeSurfer,PostFreeSurfer,fMRIVolume,fMRISurface,DiffusionPreprocessing} ...]
                            Which stages to run. Space separated list.
      --anat_unwarpdir		 Direction to unwarp 3D anatomicals. Required if
      							 distortion correction and PreFreeSurfer are specified.
      							 One of x, y, z, -x, -y, -z.
      --license_key LICENSE_KEY
                            FreeSurfer license key - letters and numbers after "*"
                            in the email you received after registration. To
                            register (for free) visit
                            https://surfer.nmr.mgh.harvard.edu/registration.html
      -v, --version         show program's version number and exit

To run it in participant level mode (for one participant):

    docker run -i --rm \
    -v /Users/filo/data/ds005:/bids_dataset:ro \
    -v /Users/filo/outputs:/outputs \
    bids/hcppipelines \
    /bids_dataset /outputs participant --participant_label 01 --license_key "XXXXXX"

### Commercial use

In addition to [FreeSurfer](https://surfer.nmr.mgh.harvard.edu/) the following **non-free** Debian packages are part of this BIDS App:

    non-free/science        fsl-5.0-core
    non-free/science        fsl-5.0-eddy-nonfree
    non-free/science        fsl-atlases
    non-free/science        fsl-bangor-cerebellar-atlas
    non-free/science        fsl-core
    non-free/science        fsl-harvard-oxford-atlases
    non-free/science        fsl-harvard-oxford-cortical-lateralized-atlas
    non-free/science        fsl-jhu-dti-whitematter-atlas
    non-free/science        fsl-juelich-histological-atlas
    non-free/science        fsl-mni-structural-atlas
    non-free/science        fsl-mni152-templates
    non-free/science        fsl-oxford-striatal-atlas
    non-free/science        fsl-oxford-thalamic-connectivity-atlas
    non-free/science        fsl-resting-connectivity-parcellation-atlases
    non-free/science        fsl-subthalamic-nucleus-atlas
    non-free/science        fsl-talairach-daemon-atlas

If you are considering commercial use of this App please consult the relevant licenses.

### TODO

   - [ ] Add DiffusionProcessing stage
   - [ ] More testing for fMRI with different resolution
   - [ ] Run fMRI runs in parallel (when n_cpus present)
   - [ ] Add support for TOPUP and GE fieldmaps for structural scans (please get in touch if you can provide sample data)
   - [ ] Add support for Siemens and GE fieldmaps for fMRI scans (please get in touch if you can provide sample data)
   - [ ] Avoid copying fsaverage folder for every participant
   - [ ] Add ICA FIX stage
   - [ ] Add group level analysis
   - [ ] Add task fMRI model fitting

[HCP]: http://www.humanconnectome.org
[GlasserEtAl]: http://www.ncbi.nlm.nih.gov/pubmed/23668970
[SmithEtAl]: http://www.ncbi.nlm.nih.gov/pubmed/23702415
[release-install-use]: https://github.com/Washington-University/Pipelines/wiki/v3.4.0-Release-Notes,-Installation,-and-Usage
[hcp-users-subscribe]: http://humanconnectome.org/contact/#subscribe
