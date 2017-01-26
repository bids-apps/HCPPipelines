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
from collections import OrderedDict

def run(command, env={}, cwd=None):
    merged_env = os.environ
    merged_env.update(env)
    merged_env.pop("DEBUG", None)
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

grayordinatesres = "2" # This is currently the only option for which the is an atlas
lowresmesh = 32

def run_pre_freesurfer(**args):
    args.update(os.environ)
    args["t1"] = "@".join(t1ws)
    args["t2"] = "@".join(t2ws)

    cmd = '{HCPPIPEDIR}/PreFreeSurfer/PreFreeSurferPipeline.sh ' + \
    '--path="{path}" ' + \
    '--subject="{subject}" ' + \
    '--t1="{t1}" ' + \
    '--t2="{t2}" ' + \
    '--t1template="{HCPPIPEDIR_Templates}/MNI152_T1_{t1_template_res:.1f}mm.nii.gz" ' + \
    '--t1templatebrain="{HCPPIPEDIR_Templates}/MNI152_T1_{t1_template_res:.1f}mm_brain.nii.gz" ' + \
    '--t1template2mm="{HCPPIPEDIR_Templates}/MNI152_T1_2mm.nii.gz" ' + \
    '--t2template="{HCPPIPEDIR_Templates}/MNI152_T2_{t2_template_res:.1f}mm.nii.gz" ' + \
    '--t2templatebrain="{HCPPIPEDIR_Templates}/MNI152_T2_{t2_template_res:.1f}mm_brain.nii.gz" ' + \
    '--t2template2mm="{HCPPIPEDIR_Templates}/MNI152_T2_2mm.nii.gz" ' + \
    '--templatemask="{HCPPIPEDIR_Templates}/MNI152_T1_{t1_template_res:.1f}mm_brain_mask.nii.gz" ' + \
    '--template2mmmask="{HCPPIPEDIR_Templates}/MNI152_T1_2mm_brain_mask_dil.nii.gz" ' + \
    '--brainsize="150" ' + \
    '--fnirtconfig="{HCPPIPEDIR_Config}/T1_2_MNI152_2mm.cnf" ' + \
    '--fmapmag="{fmapmag}" ' + \
    '--fmapphase="{fmapphase}" ' + \
    '--fmapgeneralelectric="NONE" ' + \
    '--echodiff="{echodiff}" ' + \
    '--SEPhaseNeg="{SEPhaseNeg}" ' + \
    '--SEPhasePos="{SEPhasePos}" ' + \
    '--echospacing="{echospacing}" ' + \
    '--seunwarpdir="{seunwarpdir}" ' + \
    '--t1samplespacing="{t1samplespacing}" ' + \
    '--t2samplespacing="{t2samplespacing}" ' + \
    '--unwarpdir="{unwarpdir}" ' + \
    '--gdcoeffs="NONE" ' + \
    '--avgrdcmethod={avgrdcmethod} ' + \
    '--topupconfig="{HCPPIPEDIR_Config}/b02b0.cnf" ' + \
    '--printcom=""'
    cmd = cmd.format(**args)
    run(cmd, cwd=args["path"], env={"OMP_NUM_THREADS": str(args["n_cpus"])})

def run_freesurfer(**args):
    args.update(os.environ)
    args["subjectDIR"] = os.path.join(args["path"], args["subject"], "T1w")
    cmd = '{HCPPIPEDIR}/FreeSurfer/FreeSurferPipeline.sh ' + \
      '--subject="{subject}" ' + \
      '--subjectDIR="{subjectDIR}" ' + \
      '--t1="{path}/{subject}/T1w/T1w_acpc_dc_restore.nii.gz" ' + \
      '--t1brain="{path}/{subject}/T1w/T1w_acpc_dc_restore_brain.nii.gz" ' + \
      '--t2="{path}/{subject}/T1w/T2w_acpc_dc_restore.nii.gz" ' + \
      '--printcom=""'
    cmd = cmd.format(**args)

    if not os.path.exists(os.path.join(args["subjectDIR"], "fsaverage")):
        shutil.copytree(os.path.join(os.environ["SUBJECTS_DIR"], "fsaverage"),
                        os.path.join(args["subjectDIR"], "fsaverage"))
    if not os.path.exists(os.path.join(args["subjectDIR"], "lh.EC_average")):
        shutil.copytree(os.path.join(os.environ["SUBJECTS_DIR"], "lh.EC_average"),
                        os.path.join(args["subjectDIR"], "lh.EC_average"))
    if not os.path.exists(os.path.join(args["subjectDIR"], "rh.EC_average")):
        shutil.copytree(os.path.join(os.environ["SUBJECTS_DIR"], "rh.EC_average"),
                        os.path.join(args["subjectDIR"], "rh.EC_average"))

    run(cmd, cwd=args["path"], env={"NSLOTS": str(args["n_cpus"]),
                                    "OMP_NUM_THREADS": str(args["n_cpus"])})

def run_post_freesurfer(**args):
    args.update(os.environ)
    cmd = '{HCPPIPEDIR}/PostFreeSurfer/PostFreeSurferPipeline.sh ' + \
      '--path="{path}" ' + \
      '--subject="{subject}" ' + \
      '--surfatlasdir="{HCPPIPEDIR_Templates}/standard_mesh_atlases" ' + \
      '--grayordinatesdir="{HCPPIPEDIR_Templates}/91282_Greyordinates" ' + \
      '--grayordinatesres="{grayordinatesres:s}" ' + \
      '--hiresmesh="164" ' + \
      '--lowresmesh="{lowresmesh:d}" ' + \
      '--subcortgraylabels="{HCPPIPEDIR_Config}/FreeSurferSubcorticalLabelTableLut.txt" ' + \
      '--freesurferlabels="{HCPPIPEDIR_Config}/FreeSurferAllLut.txt" ' + \
      '--refmyelinmaps="{HCPPIPEDIR_Templates}/standard_mesh_atlases/Conte69.MyelinMap_BC.164k_fs_LR.dscalar.nii" ' + \
      '--regname="FS" ' + \
      '--printcom=""'
    cmd = cmd.format(**args)
    run(cmd, cwd=args["path"], env={"OMP_NUM_THREADS": str(args["n_cpus"])})

def run_generic_fMRI_volume_processsing(**args):
    args.update(os.environ)
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
      '--fmrires={fmrires:s} ' + \
      '--dcmethod={dcmethod} ' + \
      '--gdcoeffs="NONE" ' + \
      '--topupconfig={HCPPIPEDIR_Config}/b02b0.cnf ' + \
      '--printcom="" ' + \
      '--biascorrection={biascorrection} ' + \
      '--mctype="MCFLIRT"'
    cmd = cmd.format(**args)
    run(cmd, cwd=args["path"], env={"OMP_NUM_THREADS": str(args["n_cpus"])})

def run_generic_fMRI_surface_processsing(**args):
    print(args)
    args.update(os.environ)
    cmd = '{HCPPIPEDIR}/fMRISurface/GenericfMRISurfaceProcessingPipeline.sh ' + \
      '--path={path} ' + \
      '--subject={subject} ' + \
      '--fmriname={fmriname} ' + \
      '--lowresmesh="{lowresmesh:d}" ' + \
      '--fmrires={fmrires:s} ' + \
      '--smoothingFWHM={fmrires:s} ' + \
      '--grayordinatesres="{grayordinatesres:s}" ' + \
      '--regname="FS"'
    cmd = cmd.format(**args)
    run(cmd, cwd=args["path"], env={"OMP_NUM_THREADS": str(args["n_cpus"])})

def run_diffusion_processsing(**args):
    # print(args)
    args.update(os.environ)
    cmd = '{HCPPIPEDIR}/DiffusionPreprocessing/DiffPreprocPipeline.sh ' + \
      '--posData="{posData}" ' +\
      '--negData="{negData}" ' + \
      '--path="{path}" ' + \
      '--subject="{subject}" ' + \
      '--echospacing="{echospacing}" '+ \
      '--PEdir={PEdir} ' + \
      '--gdcoeffs="NONE" ' + \
      '--dwiname="{dwiname}" ' + \
      '--printcom=""'
    cmd = cmd.format(**args)
    print('\n',cmd, '\n')
    run(cmd, cwd=args["path"], env={"OMP_NUM_THREADS": str(args["n_cpus"])})

def generate_level1_fsf(**args):
    print(args)
    args.update(os.environ)
    cmd = '{HCPPIPEDIR}/Examples/Scripts/generate_level_1_fsf_dev.sh ' + \
        '--studyfolder={studyfolder} ' + \
        '--subject={subject} ' + \
        '--taskname={taskname} ' + \
        '--templatedir={HCPPIPEDIR}/{templatedir} ' + \
        '--outdir={outdir} ' + \
        '--dir={dir}'
    cmd = cmd.format(**args)
    print('\n', cmd, '\n')
    # run(cmd, cwd=args["path"], env={"OMP_NUM_THREADS": str(args["n_cpus"])})

def generate_level2_fsf(**args):
    print(args)
    args.update(os.environ)
    cmd = '{HCPPIPEDIR}/Examples/Scripts/generate_level_2_fsf_dev.sh ' + \
        '--studyfolder={studyfolder} ' + \
        '--subject={subject} ' + \
        '--taskname={taskname} ' + \
        '--templatedir={HCPPIPEDIR}/{templatedir} ' + \
        '--outdir={outdir} '
    cmd = cmd.format(**args)
    print('\n', cmd, '\n')
    # run(cmd, cwd=args["path"], env={"OMP_NUM_THREADS": str(args["n_cpus"])})

def run_task_fmri_analysis(**args):
    print(args)
    args.update(os.environ)
    cmd = '{HCPPIPEDIR}/TaskfMRIAnalysis/TaskfMRIAnalysis.sh ' + \
        '--path={path} ' + \
        '--subject={subject} ' + \
        '--lvl1tasks={lvl1tasks} ' + \
        '--lvl1fsfs={lvl1fsfs} ' + \
        '--lvl2task={lvl2task} ' + \
        '--lvl2fsf={lvl2fsf} ' + \
        '--lowresmesh={lowresmesh} ' + \
        '--grayordinatesres="{grayordinatesres:s}" ' + \
        '--confound={confound} ' + \
        '--finalsmoothingFWHM={finalsmoothingFWHM} ' + \
        '--temporalfilter={temporalfilter} ' + \
        '--vba={vba} ' + \
        '--regname={regname} ' + \
        '--parcellation={parcellation} ' + \
        '--parcellationfile={parcellationfile} ' + \
        '--printcom=""'
    cmd = cmd.format(**args)
    print('\n', cmd, '\n')
    # run(cmd, cwd=args["path"], env={"OMP_NUM_THREADS": str(args["n_cpus"])})

__version__ = open('/version').read()

parser = argparse.ArgumentParser(description='HCP Pipelines BIDS App (T1w, T2w, fMRI)')
parser.add_argument('bids_dir', help='The directory with the input dataset '
                    'formatted according to the BIDS standard.')
parser.add_argument('output_dir', help='The directory where the output files '
                    'should be stored. If you are running group level analysis '
                    'this folder should be prepopulated with the results of the'
                    'participant level analysis.')
parser.add_argument('analysis_level', help='Level of the analysis that will be performed. '
                    'Multiple participant level analyses can be run independently '
                    '(in parallel) using the same output_dir.',
                    choices=['participant'])
parser.add_argument('--participant_label', help='The label of the participant that should be analyzed. The label '
                   'corresponds to sub-<participant_label> from the BIDS spec '
                   '(so it does not include "sub-"). If this parameter is not '
                   'provided all subjects should be analyzed. Multiple '
                   'participants can be specified with a space separated list.',
                   nargs="+")
parser.add_argument('--n_cpus', help='Number of CPUs/cores available to use.',
                   default=1, type=int)
parser.add_argument('--stages', help='Which stages to run. Space separated list.',
                   nargs="+", choices=['PreFreeSurfer', 'FreeSurfer',
                                       'PostFreeSurfer', 'fMRIVolume',
                                       'fMRISurface', 'DiffusionPreprocessing'],
                   default=['PreFreeSurfer', 'FreeSurfer', 'PostFreeSurfer',
                            'fMRIVolume', 'fMRISurface',
                            'DiffusionPreprocessing', 'TaskfMRIAnalysis'])
parser.add_argument('--license_key', help='FreeSurfer license key - letters and numbers after "*" in the email you received after registration. To register (for free) visit https://surfer.nmr.mgh.harvard.edu/registration.html',
                    required=True)
parser.add_argument('-v', '--version', action='version',
                    version='HCP Pielines BIDS App version {}'.format(__version__))

args = parser.parse_args()

#
#
run("bids-validator " + args.bids_dir)

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

        available_resolutions = [0.7, 0.8, 1.0]
        t1_zooms = nibabel.load(t1ws[0]).get_header().get_zooms()
        t1_res = float(min(t1_zooms[:3]))
        t1_template_res = min(available_resolutions, key=lambda x:abs(x-t1_res))
        t2_zooms = nibabel.load(t2ws[0]).get_header().get_zooms()
        t2_res = float(min(t2_zooms[:3]))
        t2_template_res = min(available_resolutions, key=lambda x:abs(x-t2_res))

        fieldmap_set = layout.get_fieldmap(t1ws[0])
        fmap_args = {"fmapmag": "NONE",
                     "fmapphase": "NONE",
                     "echodiff": "NONE",
                     "t1samplespacing": "NONE",
                     "t2samplespacing": "NONE",
                     "unwarpdir": "NONE",
                     "avgrdcmethod": "NONE",
                     "SEPhaseNeg": "NONE",
                     "SEPhasePos": "NONE",
                     "echospacing": "NONE",
                     "seunwarpdir": "NONE"}

        if fieldmap_set:
            t1_spacing = layout.get_metadata(t1ws[0])["RealDwellTime"]
            t2_spacing = layout.get_metadata(t2ws[0])["RealDwellTime"]

            unwarpdir = layout.get_metadata(t1ws[0])["PhaseEncodingDirection"]
            unwarpdir = unwarpdir.replace("i","x").replace("j", "y").replace("k", "z")
            if len(unwarpdir) == 2:
                unwarpdir = "-" + unwarpdir[0]

            fmap_args.update({"t1samplespacing": "%.8f"%t1_spacing,
                              "t2samplespacing": "%.8f"%t2_spacing,
                              "unwarpdir": unwarpdir})

            if fieldmap_set["type"] == "phasediff":
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

                fmap_args.update({"fmapmag": merged_file,
                                  "fmapphase": fieldmap_set["phasediff"],
                                  "echodiff": "%.6f"%te_diff,
                                  "avgrdcmethod": "SiemensFieldMap"})
            elif fieldmap_set["type"] == "epi":
                SEPhaseNeg = None
                SEPhasePos = None
                for fieldmap in fieldmap_set["epi"]:
                    enc_dir = layout.get_metadata(fieldmap)["PhaseEncodingDirection"]
                    if "-" in enc_dir:
                        SEPhaseNeg = fieldmap
                    else:
                        SEPhasePos = fieldmap

                seunwarpdir = layout.get_metadata(fieldmap_set["epi"][0])["PhaseEncodingDirection"]
                seunwarpdir = seunwarpdir.replace("-", "").replace("i","x").replace("j", "y").replace("k", "z")

                #TODO check consistency of echo spacing instead of assuming it's all the same
                if "EffectiveEchoSpacing" in layout.get_metadata(fieldmap_set["epi"][0]):
                    echospacing = layout.get_metadata(fieldmap_set["epi"][0])["EffectiveEchoSpacing"]
                elif "TotalReadoutTime" in layout.get_metadata(fieldmap_set["epi"][0]):
                    # HCP Pipelines do not allow users to specify total readout time directly
                    # Hence we need to reverse the calculations to provide echo spacing that would
                    # result in the right total read out total read out time
                    # see https://github.com/Washington-University/Pipelines/blob/master/global/scripts/TopupPreprocessingAll.sh#L202
                    print("BIDS App wrapper: Did not find EffectiveEchoSpacing, calculating it from TotalReadoutTime")
                    # TotalReadoutTime = EffectiveEchoSpacing * (len(PhaseEncodingDirection) - 1)
                    total_readout_time = layout.get_metadata(fieldmap_set["epi"][0])["TotalReadoutTime"]
                    phase_len = nibabel.load(fieldmap_set["epi"][0]).shape[{"x": 0, "y": 1}[seunwarpdir]]
                    echospacing = TotalReadoutTime / float(phase_len - 1)
                else:
                    raise RuntimeError("EffectiveEchoSpacing or TotalReadoutTime defined for the fieldmap intended for T1w image. Please fix your BIDS dataset.")

                fmap_args.update({"SEPhaseNeg": SEPhaseNeg,
                                  "SEPhasePos": SEPhasePos,
                                  "echospacing": "%.6f"%echospacing,
                                  "seunwarpdir": seunwarpdir,
                                  "avgrdcmethod": "TOPUP"})
        #TODO add support for GE fieldmaps

        struct_stages_dict = OrderedDict([("PreFreeSurfer", partial(run_pre_freesurfer,
                                                path=args.output_dir,
                                                subject="sub-%s"%subject_label,
                                                t1ws=t1ws,
                                                t2ws=t2ws,
                                                n_cpus=args.n_cpus,
                                                t1_template_res=t1_template_res,
                                                t2_template_res=t2_template_res,
                                                **fmap_args)),
                       ("FreeSurfer", partial(run_freesurfer,
                                             path=args.output_dir,
                                             subject="sub-%s"%subject_label,
                                             n_cpus=args.n_cpus)),
                       ("PostFreeSurfer", partial(run_post_freesurfer,
                                                 path=args.output_dir,
                                                 subject="sub-%s"%subject_label,
                                                 grayordinatesres=grayordinatesres,
                                                 lowresmesh=lowresmesh,
                                                 n_cpus=args.n_cpus))
                       ])
        for stage, stage_func in struct_stages_dict.iteritems():
            if stage in args.stages:
                stage_func()

        bolds = [f.filename for f in layout.get(subject=subject_label,
                                                type='bold',
                                                extensions=["nii.gz", "nii"])]
        for fmritcs in bolds:
            fmriname = "_".join(fmritcs.split("sub-")[-1].split("_")[1:-1]).split(".")[0]
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
            fmrires = float(min(zooms[:3]))
            fmrires = "2" # https://github.com/Washington-University/Pipelines/blob/637b35f73697b77dcb1d529902fc55f431f03af7/fMRISurface/scripts/SubcorticalProcessing.sh#L43
            # While running '/usr/bin/wb_command -cifti-create-dense-timeseries /scratch/users/chrisgor/hcp_output2/sub-100307/MNINonLinear/Results/EMOTION/EMOTION_temp_subject.dtseries.nii -volume /scratch/users/chrisgor/hcp_output2/sub-100307/MNINonLinear/Results/EMOTION/EMOTION.nii.gz /scratch/users/chrisgor/hcp_output2/sub-100307/MNINonLinear/ROIs/ROIs.2.nii.gz':
            # ERROR: label volume has a different volume space than data volume


            func_stages_dict = OrderedDict([("fMRIVolume", partial(run_generic_fMRI_volume_processsing,
                                                      path=args.output_dir,
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
                                                      n_cpus=args.n_cpus)),
                                ("fMRISurface", partial(run_generic_fMRI_surface_processsing,
                                                       path=args.output_dir,
                                                       subject="sub-%s"%subject_label,
                                                       fmriname=fmriname,
                                                       fmrires=fmrires,
                                                       n_cpus=args.n_cpus,
                                                       grayordinatesres=grayordinatesres,
                                                       lowresmesh=lowresmesh))
                                ])
            for stage, stage_func in func_stages_dict.iteritems():
                if stage in args.stages:
                    stage_func()

        # dwis = layout.get(subject=subject_label, type='dwi',
        #                                          extensions=["nii.gz", "nii"])

        # print(dwis)

        posData = []
        negData = []
        PEdir = "None"
        dwiname = "Diffusion"
        dirnums = []

        numruns = set(layout.get(target='run', return_type='id',
                                 subject=subject_label, type='dwi',
                                 extensions=["nii.gz", "nii"]))

        for session in numruns:
            acqs = set(layout.get(target='acquisition', return_type='id',
                                  subject=subject_label, type='dwi',
                                  extensions=["nii.gz", "nii"]))
            for acq in acqs:
                y = [int(s) for s in acq[0:len(acq)] if s.isdigit()]
                y = [str(s) for s in y]
                y = ''.join(y)
                dirnums.append(y)
            for dirnum in set(dirnums):
                dwiname = "Diffusion" + "_dir-" + dirnum + "_" + session + "_corr"
                for acq in acqs:
                    if "AP" or "PA" in acqs:
                        PEdir = 2
                    elif "LR" or "RL" in acqs:
                        PEdir = 1
                    else:
                        RuntimeError("Acquisition direction not specified on dwi file")
                    pos = "EMPTY"
                    neg = "EMPTY"
                    gdcoeffs = "None"
                    dwis = layout.get(subject=subject_label,
                                      type='dwi', acquisition=acq, run=session,
                                      extensions=["nii.gz", "nii"])
                    assert len(dwis) <= 2
                    for dwi in dwis:
                        dwi = dwi.filename
                        if "-" in layout.get_metadata(dwi)["PhaseEncodingDirection"]:
                            neg = dwi
                            negData.append(neg)
                        else:
                            pos = dwi
                            posData.append(pos)

                # print(negData)
                # print(posData)
                # print(dwiname)

                for posfile, negfile in zip(posData, negData):
                    echospacing = layout.get_metadata(posfile)["EffectiveEchoSpacing"] * 1000
                    dwi_stage_dict = OrderedDict([("DiffusionPreprocessing", partial(run_diffusion_processsing,
                                                                                     posData=posfile,
                                                                                     negData=negfile,
                                                                                     path=args.output_dir,
                                                                                     subject="sub-%s" % subject_label,
                                                                                     echospacing=echospacing,
                                                                                     PEdir=PEdir,
                                                                                     gdcoeffs="NONE",
                                                                                     dwiname=dwiname,
                                                                                     n_cpus=args.n_cpus))])

                    for stage, stage_func in dwi_stage_dict.iteritems():
                        if stage in args.stages:
                            stage_func()



