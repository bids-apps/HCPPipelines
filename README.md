

    PS C:\Users\filo> docker run -ti --rm -v /c/Users/filo/hcp_example_bids:/bids_dir:ro -v /c/Users/filo/test_output:/output --read-only -v /tmp:/tmp -v /var/tmp:/var/tmp bids/hcppipelines --help
    usage: run.py [-h]
                  [--participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]]
                  [--n_cpus N_CPUS]
                  [--stages {PreFreeSurfer,FreeSurfer,PostFreeSurfer} [{PreFreeSurfer,FreeSurfer,PostFreeSurfer} ...]]
                  --license_key LICENSE_KEY [-v]
                  bids_dir output_dir {participant,group}

    FreeSurfer recon-all + custom template generation.

    positional arguments:
      bids_dir              The directory with the input dataset formatted
                            according to the BIDS standard.
      output_dir            The directory where the output files should be stored.
                            If you are running group level analysis this folder
                            should be prepopulated with the results of
                            theparticipant level analysis.
      {participant,group}   Level of the analysis that will be performed. Multiple
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
      --stages {PreFreeSurfer,FreeSurfer,PostFreeSurfer} [{PreFreeSurfer,FreeSurfer,PostFreeSurfer} ...]
                            Which stages to run.
      --license_key LICENSE_KEY
                            FreeSurfer license key - letters and numbers after "*"
                            in the email you received after registration. To
                            register (for free) visit
                            https://surfer.nmr.mgh.harvard.edu/regis
