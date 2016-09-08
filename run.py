#!/usr/bin/python
from __future__ import print_function
import argparse
import os
import shutil
import nibabel
from glob import glob
from subprocess import Popen, PIPE
from shutil import rmtree
import subprocess
from bids.grabbids import BIDSLayout
from functools import partial

def run(command, env={}, cwd=None):
    merged_env = os.environ
    merged_env.update(env)
    process = Popen(command, stdout=PIPE, stderr=subprocess.STDOUT,
                    shell=True, env=merged_env, cwd=cwd)
    while True:
        line = process.stdout.readline()
        line = str(line)[:-1]
        print(line)
        if line == '' and process.poll() != None:
            break
    if process.returncode != 0:
        raise Exception("Non zero return code: %d"%process.returncode)

def run_pre_freesurfer(output_dir, subject_id, t1ws, t2ws, mag_file,
                       phasediff_file, te_diff, t1_spacing, t2_spacing,
                       unwarpdir, avgrdcmethod, n_cpus):
    print(t1ws)
    args = {"StudyFolder": output_dir,
            "Subject": subject_id,
            "T1wInputImages": "@".join(t1ws),
            "T2wInputImages": "@".join(t2ws),
            "HCPPIPEDIR": os.environ["HCPPIPEDIR"],
            "HCPPIPEDIR_Templates": os.environ["HCPPIPEDIR_Templates"],
            "HCPPIPEDIR_Config": os.environ["HCPPIPEDIR_Config"],
            "MagnitudeInputName": mag_file,
            "PhaseInputName": phasediff_file,
            "TE": "%0.6f"%te_diff,
            "T1wSampleSpacing": "%0.8f"%t1_spacing,
            "T2wSampleSpacing": "%0.8f"%t2_spacing,
            "UnwarpDir": unwarpdir,
            "avgrdcmethod": avgrdcmethod
            }
    cmd = '{HCPPIPEDIR}/PreFreeSurfer/PreFreeSurferPipeline.sh ' + \
    '--path="{StudyFolder}" ' + \
    '--subject="{Subject}" ' + \
    '--t1="{T1wInputImages}" ' + \
    '--t2="{T2wInputImages}" ' + \
    '--t1template="{HCPPIPEDIR_Templates}/MNI152_T1_0.7mm.nii.gz" ' + \
    '--t1templatebrain="{HCPPIPEDIR_Templates}/MNI152_T1_0.7mm_brain.nii.gz" ' + \
    '--t1template2mm="{HCPPIPEDIR_Templates}/MNI152_T1_2mm.nii.gz" ' + \
    '--t2template="{HCPPIPEDIR_Templates}/MNI152_T2_0.7mm.nii.gz" ' + \
    '--t2templatebrain="{HCPPIPEDIR_Templates}/MNI152_T2_0.7mm_brain.nii.gz" ' + \
    '--t2template2mm="{HCPPIPEDIR_Templates}/MNI152_T2_2mm.nii.gz" ' + \
    '--templatemask="{HCPPIPEDIR_Templates}/MNI152_T1_0.7mm_brain_mask.nii.gz" ' + \
    '--template2mmmask="{HCPPIPEDIR_Templates}/MNI152_T1_2mm_brain_mask_dil.nii.gz" ' + \
    '--brainsize="150" ' + \
    '--fnirtconfig="{HCPPIPEDIR_Config}/T1_2_MNI152_2mm.cnf" ' + \
    '--fmapmag="{MagnitudeInputName}" ' + \
    '--fmapphase="{PhaseInputName}" ' + \
    '--fmapgeneralelectric="NONE" ' + \
    '--echodiff="{TE}" ' + \
    '--SEPhaseNeg="NONE" ' + \
    '--SEPhasePos="NONE" ' + \
    '--echospacing="NONE" ' + \
    '--seunwarpdir="NONE" ' + \
    '--t1samplespacing="{T1wSampleSpacing}" ' + \
    '--t2samplespacing="{T2wSampleSpacing}" ' + \
    '--unwarpdir="{UnwarpDir}" ' + \
    '--gdcoeffs="NONE" ' + \
    '--avgrdcmethod={avgrdcmethod} ' + \
    '--topupconfig="NONE" ' + \
    '--printcom=""'
    cmd = cmd.format(**args)
    print(cmd)
    run(cmd, cwd=output_dir, env={"OMP_NUM_THREADS": str(n_cpus)})

def run_freesurfer(output_dir, subject_id, n_cpus):
    print(t1ws)
    subjects_dir = os.path.join(output_dir, subject_id, "T1w")
    args = {"StudyFolder": output_dir,
            "Subject": subject_id,
            "subjects_dir": subjects_dir,
            "HCPPIPEDIR": os.environ["HCPPIPEDIR"]
            }
    cmd = '{HCPPIPEDIR}/FreeSurfer/FreeSurferPipeline.sh ' + \
      '--subject="{Subject}" ' + \
      '--subjectDIR="{subjects_dir}" ' + \
      '--t1="{StudyFolder}/{Subject}/T1w/T1w_acpc_dc_restore.nii.gz" ' + \
      '--t1brain="{StudyFolder}/{Subject}/T1w/T1w_acpc_dc_restore_brain.nii.gz" ' + \
      '--t2="{StudyFolder}/{Subject}/T1w/T2w_acpc_dc_restore.nii.gz" ' + \
      '--printcom=""'
    cmd = cmd.format(**args)
    print(cmd)
    if not os.path.exists(os.path.join(subjects_dir, "fsaverage")):
        shutil.copytree(os.path.join(os.environ["SUBJECTS_DIR"], "fsaverage"),
                        os.path.join(subjects_dir, "fsaverage"))
    if not os.path.exists(os.path.join(subjects_dir, "lh.EC_average")):
        shutil.copytree(os.path.join(os.environ["SUBJECTS_DIR"], "lh.EC_average"),
                        os.path.join(subjects_dir, "lh.EC_average"))
    if not os.path.exists(os.path.join(subjects_dir, "rh.EC_average")):
        shutil.copytree(os.path.join(os.environ["SUBJECTS_DIR"], "rh.EC_average"),
                        os.path.join(subjects_dir, "rh.EC_average"))
    run(cmd, cwd=output_dir, env={"NSLOTS":str(n_cpus),
                                  "OMP_NUM_THREADS": str(n_cpus)})

def run_post_freesurfer(output_dir, subject_id, n_cpus):
    args = {"StudyFolder": output_dir,
            "Subject": subject_id,
            "HCPPIPEDIR": os.environ["HCPPIPEDIR"],
            "HCPPIPEDIR_Templates": os.environ["HCPPIPEDIR_Templates"],
            "HCPPIPEDIR_Config": os.environ["HCPPIPEDIR_Config"],
            }
    cmd = '{HCPPIPEDIR}/PostFreeSurfer/PostFreeSurferPipeline.sh ' + \
      '--path="{StudyFolder}" ' + \
      '--subject="{Subject}" ' + \
      '--surfatlasdir="{HCPPIPEDIR_Templates}/standard_mesh_atlases" ' + \
      '--grayordinatesdir="{HCPPIPEDIR_Templates}/91282_Greyordinates" ' + \
      '--grayordinatesres="2" ' + \
      '--hiresmesh="164" ' + \
      '--lowresmesh="32" ' + \
      '--subcortgraylabels="{HCPPIPEDIR_Config}/FreeSurferSubcorticalLabelTableLut.txt" ' + \
      '--freesurferlabels="{HCPPIPEDIR_Config}/FreeSurferAllLut.txt" ' + \
      '--refmyelinmaps="{HCPPIPEDIR_Templates}/standard_mesh_atlases/Conte69.MyelinMap_BC.164k_fs_LR.dscalar.nii" ' + \
      '--regname="FS" ' + \
      '--printcom=""'
    cmd = cmd.format(**args)
    print(cmd)
    run(cmd, cwd=output_dir, env={"OMP_NUM_THREADS": str(n_cpus)})

def run_generic_fMRI_volume_processsing(**args):
    print(args)
    args["HCPPIPEDIR_Config"] = os.environ["HCPPIPEDIR_Config"]
    args["HCPPIPEDIR"] = os.environ["HCPPIPEDIR"]
    cmd = '{HCPPIPEDIR}/fMRIVolume/GenericfMRIVolumeProcessingPipeline.sh ' + \
      '--path={path} ' + \
      '--subject={subject} ' + \
      '--fmriname={fmriname} ' + \
      '--fmritcs={fmritcs} ' + \
      '--fmriscout={fmriscout} ' + \
      '--SEPhaseNeg={SEPhaseNeg} ' + \
      '--SEPhasePos={SEPhasePos} ' + \
      '--fmapmag="NONE" ' + \
      '--fmapphase="NONE" ' + \
      '--fmapgeneralelectric="NONE" ' + \
      '--echospacing={echospacing} ' + \
      '--echodiff="NONE" ' + \
      '--unwarpdir={unwarpdir} ' + \
      '--fmrires={fmrires} ' + \
      '--dcmethod={dcmethod} ' + \
      '--gdcoeffs="NONE" ' + \
      '--topupconfig={HCPPIPEDIR_Config}/b02b0.cnf ' + \
      '--printcom="" ' + \
      '--biascorrection={biascorrection} ' + \
      '--mctype="MCFLIRT"'
    cmd = cmd.format(**args)
    print(cmd)
    run(cmd, cwd=args["path"], env={"OMP_NUM_THREADS": str(args["n_cpus"])})

__version__ = open('/version').read()

parser = argparse.ArgumentParser(description='FreeSurfer recon-all + custom template generation.')
parser.add_argument('bids_dir', help='The directory with the input dataset '
                    'formatted according to the BIDS standard.')
parser.add_argument('output_dir', help='The directory where the output files '
                    'should be stored. If you are running group level analysis '
                    'this folder should be prepopulated with the results of the'
                    'participant level analysis.')
parser.add_argument('analysis_level', help='Level of the analysis that will be performed. '
                    'Multiple participant level analyses can be run independently '
                    '(in parallel) using the same output_dir.',
                    choices=['participant', 'group'])
parser.add_argument('--participant_label', help='The label of the participant that should be analyzed. The label '
                   'corresponds to sub-<participant_label> from the BIDS spec '
                   '(so it does not include "sub-"). If this parameter is not '
                   'provided all subjects should be analyzed. Multiple '
                   'participants can be specified with a space separated list.',
                   nargs="+")
parser.add_argument('--n_cpus', help='Number of CPUs/cores available to use.',
                   default=1, type=int)
parser.add_argument('--stages', help='Which stages to run.',
                   nargs="+", choices=['PreFreeSurfer', 'FreeSurfer', 'PostFreeSurfer', 'fMRIVolume'],
                   default=['PreFreeSurfer', 'FreeSurfer', 'PostFreeSurfer', 'fMRIVolume'])
parser.add_argument('--license_key', help='FreeSurfer license key - letters and numbers after "*" in the email you received after registration. To register (for free) visit https://surfer.nmr.mgh.harvard.edu/registration.html',
                    required=True)
parser.add_argument('-v', '--version', action='version',
                    version='BIDS-App example version {}'.format(__version__))

args = parser.parse_args()

#
#
# run("bids-validator " + args.bids_dir)

layout = BIDSLayout(args.bids_dir)
subjects_to_analyze = []
# only for a subset of subjects
if args.participant_label:
    subjects_to_analyze = args.participant_label
# for all subjects
else:
    subject_dirs = glob(os.path.join(args.bids_dir, "sub-*"))
    subjects_to_analyze = [subject_dir.split("-")[-1] for subject_dir in subject_dirs]

# running participant level
if args.analysis_level == "participant":
    # find all T1s and skullstrip them
    for subject_label in subjects_to_analyze:
        t1ws = [f.filename for f in layout.get(subject=subject_label,
                                               type='T1w',
                                               extensions=["nii.gz", "nii"])]
        t2ws = [f.filename for f in layout.get(subject=subject_label,
                                               type='T2w',
                                               extensions=["nii.gz", "nii"])]
        assert (len(t1ws) > 0), "No T1w files found for subject %s!"%subject_label
        assert (len(t2ws) > 0), "No T2w files found for subject %s!"%subject_label
        fieldmap_set = layout.get_fieldmap(t1ws[0])
        if fieldmap_set and fieldmap_set["type"] == "phasediff":
            merged_file = "%s/tmp/%s/magfile.nii.gz"%(args.output_dir, subject_label)
            run("mkdir -p %s/tmp/%s/ && fslmerge -t %s %s %s"%(args.output_dir,
            subject_label,
            merged_file,
            fieldmap_set["magnitude1"],
            fieldmap_set["magnitude2"]))

            phasediff_metadata = layout.get_metadata(fieldmap_set["phasediff"])
            te_diff = phasediff_metadata["EchoTime2"] - phasediff_metadata["EchoTime1"]
            # HCP expects TE in miliseconds
            te_diff = te_diff*1000.0

            t1_spacing = layout.get_metadata(t1ws[0])["EffectiveEchoSpacing"]
            t2_spacing = layout.get_metadata(t2ws[0])["EffectiveEchoSpacing"]

            unwarpdir = layout.get_metadata(t1ws[0])["PhaseEncodingDirection"]
            unwarpdir = unwarpdir.replace("i","x").replace("j", "y").replace("k", "z")
            if len(unwarpdir) == 2:
                unwarpdir = "-" + unwarpdir[0]
            fmap_args = {"mag_file": merged_file,
                         "phasediff_file": fieldmap_set["phasediff"],
                         "te_diff": te_diff,
                         "t1_spacing": t1_spacing,
                         "t2_spacing": t2_spacing,
                         "unwarpdir": unwarpdir,
                         "avgrdcmethod": "SiemensFieldMap"}
        else: #TODO add support for GE and spin echo (TOPUP) fieldmaps
            fmap_args = {"mag_file": "NONE",
                         "phasediff_file": "NONE",
                         "te_diff": "NONE",
                         "t1_spacing": "NONE",
                         "t2_spacing": "NONE",
                         "unwarpdir": "NONE",
                         "avgrdcmethod": "NONE"}

        struct_stages_dict = {"PreFreeSurfer": partial(run_pre_freesurfer,
                                                output_dir=args.output_dir,
                                                subject_id="sub-%s"%subject_label,
                                                t1ws=t1ws,
                                                t2ws=t2ws,
                                                n_cpus=args.n_cpus,
                                                **fmap_args),
                       "FreeSurfer": partial(run_freesurfer,
                                             output_dir=args.output_dir,
                                             subject_id="sub-%s"%subject_label,
                                             n_cpus=args.n_cpus),
                       "PostFreeSurfer": partial(run_post_freesurfer,
                                                 output_dir=args.output_dir,
                                                 subject_id="sub-%s"%subject_label,
                                                 n_cpus=args.n_cpus)
                       }
        for stage, stage_func in struct_stages_dict.iteritems():
            if stage in args.stages:
                stage_func()

        bolds = [f.filename for f in layout.get(subject=subject_label,
                                                type='bold',
                                                extensions=["nii.gz", "nii"])]
        for fmritcs in bolds:
            fmriname = fmritcs.split("task-")[1].split("_")[0]
            assert fmriname

            fmriscout = fmritcs.replace("_bold", "_sbref")
            if not os.path.exists(fmriscout):
                fmriscout = "NONE"

            fieldmap_set = layout.get_fieldmap(fmritcs)
            print(fieldmap_set)
            if fieldmap_set and fieldmap_set["type"] == "epi":
                SEPhaseNeg = None
                SEPhasePos = None
                for fieldmap in fieldmap_set["epi"]:
                    enc_dir = layout.get_metadata(fieldmap)["PhaseEncodingDirection"]
                    if "-" in enc_dir:
                        SEPhaseNeg = fieldmap
                    else:
                        SEPhasePos = fieldmap
                echospacing = layout.get_metadata(fmritcs)["EffectiveEchoSpacing"]
                unwarpdir = layout.get_metadata(fmritcs)["PhaseEncodingDirection"]
                unwarpdir = unwarpdir.replace("i","x").replace("j", "y").replace("k", "z")
                if len(unwarpdir) == 2:
                    unwarpdir = "-" + unwarpdir[0]
                dcmethod = "TOPUP"
                biascorrection = "SEBASED"
            else:
                SEPhaseNeg = "NONE"
                SEPhasePos = "NONE"
                echospacing = "NONE"
                unwarpdir = "NONE"
                dcmethod = "NONE"
                biascorrection = "NONE"

            zooms = nibabel.load(fmritcs).get_header().get_zooms()
            fmrires = "%.3f"%min(zooms[:3])

            func_stages_dict = {"fMRIVolume": run_generic_fMRI_volume_processsing(path=args.output_dir,
                                                subject="sub-%s"%subject_label,
                                                fmriname=fmriname,
                                                fmritcs=fmritcs,
                                                fmriscout=fmriscout,
                                                SEPhaseNeg=SEPhaseNeg,
                                                SEPhasePos=SEPhasePos,
                                                echospacing=echospacing,
                                                unwarpdir=unwarpdir,
                                                fmrires=fmrires,
                                                dcmethod=dcmethod,
                                                biascorrection=biascorrection,
                                                n_cpus=args.n_cpus)
                           }
            for stage, stage_func in func_stages_dict.iteritems():
                if stage in args.stages:
                    stage_func()
