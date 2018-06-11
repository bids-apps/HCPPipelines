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
import nibabel as nip
from bids.grabbids import BIDSLayout
from functools import partial
from collections import OrderedDict
from IntendedFor import setup
import pdb


def run(command, env={}, cwd=None):
    merged_env = os.environ
    merged_env.update(env)
    merged_env.pop("DEBUG", None)
    print(command)
    process = Popen(command, stdout=PIPE, stderr=subprocess.STDOUT,
                    shell=True, env=merged_env, cwd=cwd)
    while True:
        line = process.stdout.readline()
        print(line)
        line = str(line)[:-1]
        if line == '' and process.poll() != None:
            break
    if process.returncode != 0:
        raise Exception("Non zero return code: %d"%process.returncode)

    #change ownership of completed processing
    #change_owner ='chown -R `stat -c "%u:%g" ' + args.output_dir + '` ' + args.output_dir
    #os.system(change_owner)

grayordinatesres = "2" # This is currently the only option for which the is an atlas
lowresmesh = 32
dlabel_file = "/360CortSurf_19Vol_parcel.dlabel.nii"

def run_pre_freesurfer(**args):
    args.update(os.environ)
    args["t1"] = "@".join(t1ws)
    args["t2"] = "@".join(t2ws)

    cmd = '{HCPPIPEDIR}/PreFreeSurfer/PreFreeSurferPipeline.sh ' + \
    '--path="{path}" ' + \
    '--subject="{subject}" ' + \
    '--t1="{t1}" ' + \
    '--t2="{t2}" ' + \
    '--t1template="{HCPPIPEDIR_Templates}/MNI152_T1_{t1_template_res}mm.nii.gz" ' + \
    '--t1templatebrain="{HCPPIPEDIR_Templates}/MNI152_T1_{t1_template_res}mm_brain.nii.gz" ' + \
    '--t1template2mm="{HCPPIPEDIR_Templates}/MNI152_T1_2mm.nii.gz" ' + \
    '--t2template="{HCPPIPEDIR_Templates}/MNI152_T2_{t2_template_res}mm.nii.gz" ' + \
    '--t2templatebrain="{HCPPIPEDIR_Templates}/MNI152_T2_{t2_template_res}mm_brain.nii.gz" ' + \
    '--t2template2mm="{HCPPIPEDIR_Templates}/MNI152_T2_2mm.nii.gz" ' + \
    '--templatemask="{HCPPIPEDIR_Templates}/MNI152_T1_{t1_template_res}mm_brain_mask.nii.gz" ' + \
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
    args.update(os.environ)
    cmd = '{HCPPIPEDIR}/DiffusionPreprocessing/DiffPreprocPipeline.sh ' + \
      '--posData="{posData}" ' +\
      '--negData="{negData}" ' + \
      '--path="{path}" ' + \
      '--subject="{subject}" ' + \
      '--echospacing="{echospacing}" '+ \
      '--PEdir={PEdir} ' + \
      '--gdcoeffs="NONE" ' + \
      '--printcom=""'
    cmd = cmd.format(**args)
    run(cmd, cwd=args["path"], env={"OMP_NUM_THREADS": str(args["n_cpus"])})


def run_taskfMRI_processing(**args)

def run_ICAFIX_processing(**args):
    args.update(os.environ)
    cmd = '{FSL_FIXDIR}/hcp_fix ' + \
        '{path}/{subject}/MNINonLinear/Results/{fmriname}/{fmriname}.nii.gz ' + \
        '{high_pass} ' + \
        '{training_data}'
    cmd = cmd.format(**args)
    run(cmd, cwd=args["path"], env={"OMP_NUM_THREADS": str(args["n_cpus"]),
                                    "XAPPLRESDIR": "/usr/local/R2014a/v83/X11/app-defaults"})

def run_PostFix_processing(**args):
    args.update(os.environ)
    cmd = '{HCPPIPEDIR}/PostFix/PostFix.sh ' + \
          '--path="{path}" ' + \
          '--subject="{subject}" ' + \
          '--fmri-name={fmriname} ' + \
          '--high-pass={high_pass} ' + \
          '--template-scene-dual-screen={HCPPIPEDIR}/PostFix/PostFixScenes/ICA_Classification_DualScreenTemplate.scene ' + \
          '--template-scene-single-screen={HCPPIPEDIR}/PostFix/PostFixScenes/ICA_Classification_SingleScreenTemplate.scene'
    cmd = cmd.format(**args)
    run(cmd, cwd=args["path"], env={"OMP_NUM_THREADS": str(args["n_cpus"]),
                                    "XAPPLRESDIR": "/usr/local/R2013a/v81/X11/app-defaults",
                                    "matlab_compiler_runtime": "/usr/local/R2013a/v81"})

def run_RestingStateStats_processing(**args):
    args.update(os.environ)
    cmd = '{HCPPIPEDIR}/RestingStateStats/RestingStateStats.sh ' + \
    '--path="{path}" ' + \
    '--subject="{subject}" ' + \
    '--fmri-name={fmriname} ' + \
    '--high-pass={high_pass} ' + \
    '--reg-name="NONE" ' + \
    '--low-res-mesh="{lowresmesh:d}" ' + \
    '--final-fmri-res={fmrires:s} ' + \
    '--brain-ordinates-res="{grayordinatesres:s}" ' + \
    '--smoothing-fwhm={fmrires:s} ' + \
    '--output-proc-string="finished" ' + \
    '--dlabel-file={dlabel_file} ' + \
    '--matlab-run-mode=0 ' + \
    '--bc-mode="REVERT" ' + \
    '--out-string="stats" ' + \
    '--wm="NONE" ' + \
    '--csf="NONE"'
    cmd = cmd.format(**args)
    run(cmd, cwd=args["path"], env={"OMP_NUM_THREADS": str(args["n_cpus"]),
                                "XAPPLRESDIR": "/usr/local/R2013a/v81/X11/app-defaults",
                                "matlab_compiler_runtime": "/usr/local/R2013a/v81"})



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
                                       'fMRISurface', 'ICAFIX', 'PostFix', 'RestingStateStats', 'DiffusionPreprocessing'],
                   default=['PreFreeSurfer', 'FreeSurfer', 'PostFreeSurfer',
                            'fMRIVolume', 'fMRISurface', 'ICAFIX', 'PostFix', 'RestingStateStats',
                            'DiffusionPreprocessing'])
parser.add_argument('--license_key', help='FreeSurfer license key - letters and numbers after "*" in the email you received after registration. To register (for free) visit https://surfer.nmr.mgh.harvard.edu/registration.html',
                    default='CUSSPUD/4LAA')
parser.add_argument('-v', '--version', action='version',
                    version='HCP Pipelines BIDS App version {}'.format(__version__))

args = parser.parse_args()




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
    for subject_label in subjects_to_analyze:
        # before do anything else add IntendedFor field to fieldmap
        setup(os.path.join(args.bids_dir, "sub-"+subject_label))

        # if subject label has sessions underneath those need to be outputted into different directories
        if glob(os.path.join(args.bids_dir, "sub-" + subject_label, "ses-*")):
            ses_dirs = glob(os.path.join(args.bids_dir, "sub-" + subject_label, "ses-*"))
            ses_to_analyze = [ses_dir.split("-")[-1] for ses_dir in ses_dirs]
            for ses_label in ses_to_analyze:
                if not os.path.exists(os.path.join(args.output_dir, "sub-" + subject_label, "ses-" + ses_label)):
                    os.makedirs(os.path.join(args.output_dir, "sub-" + subject_label, "ses-" + ses_label))
                t1ws = [f.filename for f in layout.get(subject=subject_label, session=ses_label,
                                                       type='T1w',
                                                       extensions=["nii.gz", "nii"])]
                t2ws = [f.filename for f in layout.get(subject=subject_label, session=ses_label,
                                                       type='T2w',
                                                       extensions=["nii.gz", "nii"])]
                assert (len(t1ws) > 0), "No T1w files found for subject %s and session %s!" % (subject_label, ses_label)
                assert (len(t2ws) > 0), "No T2w files found for subject %s and session %s!" % (subject_label, ses_label)

                available_resolutions = ["0.7", "0.8", "1"]
                t1_zooms = nibabel.load(t1ws[0]).get_header().get_zooms()
                t1_res = float(min(t1_zooms[:3]))
                t1_template_res = min(available_resolutions, key=lambda x: abs(float(x) - t1_res))
                t2_zooms = nibabel.load(t2ws[0]).get_header().get_zooms()
                t2_res = float(min(t2_zooms[:3]))
                t2_template_res = min(available_resolutions, key=lambda x: abs(float(x) - t2_res))

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
                    t1_spacing = layout.get_metadata(t1ws[0])["EffectiveEchoSpacing"]
                    t2_spacing = layout.get_metadata(t2ws[0])["EffectiveEchoSpacing"]

                    unwarpdir = layout.get_metadata(t1ws[0])["PhaseEncodingDirection"]
                    unwarpdir = unwarpdir.replace("i", "x").replace("j", "y").replace("k", "z")
                    if len(unwarpdir) == 2:
                        unwarpdir = unwarpdir[0] + "-"

                    fmap_args.update({"t1samplespacing": "%.8f" % t1_spacing,
                                      "t2samplespacing": "%.8f" % t2_spacing,
                                      "unwarpdir": unwarpdir})

                    if fieldmap_set["type"] == "phasediff":
                        merged_file = "%s/tmp/%s/%s/magfile.nii.gz" % (args.output_dir, subject_label, ses_label)
                        run("mkdir -p %s/tmp/%s/%s && fslmerge -t %s %s %s" % (args.output_dir,
                                                                             subject_label,
                                                                             ses_label,
                                                                             merged_file,
                                                                             fieldmap_set["magnitude1"],
                                                                             fieldmap_set["magnitude2"]))

                        phasediff_metadata = layout.get_metadata(fieldmap_set["phasediff"])
                        te_diff = phasediff_metadata["EchoTime2"] - phasediff_metadata["EchoTime1"]
                        # HCP expects TE in miliseconds
                        te_diff = te_diff * 1000.0

                        fmap_args.update({"fmapmag": merged_file,
                                          "fmapphase": fieldmap_set["phasediff"],
                                          "echodiff": "%.6f" % te_diff,
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
                        seunwarpdir = seunwarpdir.replace("-", "").replace("i", "x").replace("j", "y").replace("k", "z")

                        # TODO check consistency of echo spacing instead of assuming it's all the same
                        if "EffectiveEchoSpacing" in layout.get_metadata(fieldmap_set["epi"][0]):
                            echospacing = layout.get_metadata(fieldmap_set["epi"][0])["EffectiveEchoSpacing"]
                        elif "TotalReadoutTime" in layout.get_metadata(fieldmap_set["epi"][0]):
                            # HCP Pipelines do not allow users to specify total readout time directly
                            # Hence we need to reverse the calculations to provide echo spacing that would
                            # result in the right total read out total read out time
                            # see https://github.com/Washington-University/Pipelines/blob/master/global/scripts/TopupPreprocessingAll.sh#L202
                            print(
                                "BIDS App wrapper: Did not find EffectiveEchoSpacing, calculating it from TotalReadoutTime")
                            # TotalReadoutTime = EffectiveEchoSpacing * (len(PhaseEncodingDirection) - 1)
                            total_readout_time = layout.get_metadata(fieldmap_set["epi"][0])["TotalReadoutTime"]
                            phase_len = nibabel.load(fieldmap_set["epi"][0]).shape[{"x": 0, "y": 1}[seunwarpdir]]
                            echospacing = total_readout_time / float(phase_len - 1)
                        else:
                            raise RuntimeError(
                                "EffectiveEchoSpacing or TotalReadoutTime not defined for the fieldmap intended for T1w image. Please fix your BIDS dataset.")

                        fmap_args.update({"SEPhaseNeg": SEPhaseNeg,
                                          "SEPhasePos": SEPhasePos,
                                          "echospacing": "%.6f" % echospacing,
                                          "seunwarpdir": seunwarpdir,
                                          "avgrdcmethod": "TOPUP"})
                # TODO add support for GE fieldmaps

                struct_stages_dict = OrderedDict([("PreFreeSurfer", partial(run_pre_freesurfer,
                                                                            path=args.output_dir + "/sub-%s" % (subject_label),
                                                                            subject="ses-%s" % (ses_label),
                                                                            t1ws=t1ws,
                                                                            t2ws=t2ws,
                                                                            n_cpus=args.n_cpus,
                                                                            t1_template_res=t1_template_res,
                                                                            t2_template_res=t2_template_res,
                                                                            **fmap_args)),
                                                  ("FreeSurfer", partial(run_freesurfer,
                                                                         path=args.output_dir + "/sub-%s" % (subject_label),
                                                                         subject="ses-%s" % (ses_label),
                                                                         n_cpus=args.n_cpus)),
                                                  ("PostFreeSurfer", partial(run_post_freesurfer,
                                                                             path=args.output_dir + "/sub-%s" % (subject_label),
                                                                             subject="ses-%s" % (ses_label),
                                                                             grayordinatesres=grayordinatesres,
                                                                             lowresmesh=lowresmesh,
                                                                             n_cpus=args.n_cpus))
                                                  ])
                for stage, stage_func in struct_stages_dict.iteritems():
                    if stage in args.stages:
                        stage_func()

                bolds = [f.filename for f in layout.get(subject=subject_label, session=ses_label,
                                                        type='bold',
                                                        extensions=["nii.gz", "nii"])]
                for fmritcs in bolds:
                    fmriname = fmritcs.split("%s/func/" % ses_label)[-1].split(".")[0]
                    assert fmriname
                    fmriscout = fmritcs.replace("_bold", "_sbref")
                    if not os.path.exists(fmriscout):
                        fmriscout = "NONE"

                    fieldmap_set = layout.get_fieldmap(fmritcs, return_list=True)
                    if fieldmap_set:
                        for item in fieldmap_set:

                            if item["type"] == "epi":

                                fieldmap = item["epi"]
                                enc_dir = layout.get_metadata(fieldmap)["PhaseEncodingDirection"]
                                if "-" in enc_dir:
                                    SEPhaseNeg = fieldmap
                                else:
                                    SEPhasePos = fieldmap
                                echospacing = layout.get_metadata(fmritcs)["EffectiveEchoSpacing"]
                                unwarpdir = layout.get_metadata(fmritcs)["PhaseEncodingDirection"]
                                unwarpdir = unwarpdir.replace("i", "x").replace("j", "y").replace("k", "z")
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
                    reptime = float("%.1f" % zooms[3])
                    fmrires = "2"

                    # determine which fix training data to use based on resolution and TR

                    if zooms[:3] == (2.0, 2.0, 2.0) and (reptime == 0.8 or reptime == 0.7 or reptime == 1.0):
                        highpass = "2000"
                        training_data = "HCP_hp2000.RData"

                    func_stages_dict = OrderedDict([("fMRIVolume", partial(run_generic_fMRI_volume_processsing,
                                                                           path=args.output_dir + "/sub-%s" % (subject_label),
                                                                           subject="ses-%s" % (ses_label),
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
                                                                            path=args.output_dir + "/sub-%s" % (subject_label),
                                                                            subject="ses-%s" % (ses_label),
                                                                            fmriname=fmriname,
                                                                            fmrires=fmrires,
                                                                            n_cpus=args.n_cpus,
                                                                            grayordinatesres=grayordinatesres,
                                                                            lowresmesh=lowresmesh))])
                    if 'rest' in fmriname:
                        rest_stages_dict = OrderedDict([("ICAFIX", partial(run_ICAFIX_processing,
                                                                           path=args.output_dir + "/sub-%s" % (subject_label),
                                                                           n_cpus=args.n_cpus,
                                                                           subject="ses-%s" % (ses_label),
                                                                           fmriname=fmriname,
                                                                           high_pass=highpass,
                                                                           training_data=training_data)),
                                                        ("PostFix", partial(run_PostFix_processing,
                                                                            path=args.output_dir + "/sub-%s" % (subject_label),
                                                                            n_cpus=args.n_cpus,
                                                                            subject="ses-%s" % (ses_label),
                                                                            fmriname=fmriname,
                                                                            high_pass=highpass)),
                                                        ("RestingStateStats", partial(run_RestingStateStats_processing,
                                                                                     path=args.output_dir + "/sub-%s" % (subject_label),
                                                                                     n_cpus=args.n_cpus,
                                                                                     subject="ses-%s" % (ses_label),
                                                                                     fmriname=fmriname,
                                                                                     high_pass=highpass,
                                                                                     lowresmesh=lowresmesh,
                                                                                     fmrires=fmrires,
                                                                                     grayordinatesres=grayordinatesres,
                                                                                     dlabel_file=dlabel_file))])
                    else:
                        task_stages_dict = OrderedDict([("TaskfMRIAnalysis", partial(run_taskfMRI_processing,
                                                                                     path=args.output_dir + "/sub-%s" % (
                                                                                     subject_label),
                                                                                     n_cpus=args.n_cpus,
                                                                                     subject="ses-%s" % (ses_label),
                                                                                     fmriname=fmriname,
                                                                                     ))])

                for stage, stage_func in func_stages_dict.iteritems():
                    if stage in args.stages:
                        stage_func()
                for stage, stage_func in rest_stages_dict.iteritems():
                    if stage in args.stages:
                        stage_func()


                dwis = layout.get(subject=subject_label, type='dwi', extensions=["nii.gz", "nii"])

                pos = []
                neg = []
                PEdir = None; echospacing = None

                for idx, dwi in enumerate(dwis):
                    metadata = layout.get_metadata(dwi.filename)
                    # get phaseencodingdirection
                    phaseenc = metadata['PhaseEncodingDirection']
                    acq = 1 if phaseenc[0]=='i' else 2
                    if not PEdir:
                        PEdir = acq
                    if PEdir != acq:
                        raise RuntimeError("Not all dwi images have the same encoding direction (both LR and AP). Not implemented.")
                    # get pos/neg
                    if len(phaseenc)>1:
                        neg.append(dwi.filename)
                    else:
                        pos.append(dwi.filename)
                    # get echospacing
                    if not echospacing:
                        echospacing = metadata['EffectiveEchoSpacing']*1000.
                    if echospacing != metadata['EffectiveEchoSpacing']*1000.:
                        raise RuntimeError("Not all dwi images have the same echo spacing. Not implemented.")

                posdata = "@".join(pos)
                negdata = "@".join(neg)

                dif_stages_dict = OrderedDict([("DiffusionPreprocessing", partial(run_diffusion_processsing,
                                                                                 path=args.output_dir + "/sub-%s" % (subject_label),
                                                                                 n_cpus=args.n_cpus,
                                                                                 subject="ses-%s" % (ses_label),
                                                                                 posData=posdata,
                                                                                 negData=negdata,
                                                                                 echospacing=echospacing,
                                                                                 PEdir=PEdir))])

                for stage, stage_func in dif_stages_dict.iteritems():
                    if stage in args.stages:
                        stage_func()
        else:
            t1ws = [f.filename for f in layout.get(subject=subject_label,
                                                   type='T1w',
                                                   extensions=["nii.gz", "nii"])]
            t2ws = [f.filename for f in layout.get(subject=subject_label,
                                                   type='T2w',
                                                   extensions=["nii.gz", "nii"])]
            assert (len(t1ws) > 0), "No T1w files found for subject %s!"%subject_label
            assert (len(t2ws) > 0), "No T2w files found for subject %s!"%subject_label

            available_resolutions = ["0.7", "0.8", "1"]
            t1_zooms = nibabel.load(t1ws[0]).get_header().get_zooms()
            t1_res = float(min(t1_zooms[:3]))
            t1_template_res = min(available_resolutions, key=lambda x:abs(float(x)-t1_res))
            t2_zooms = nibabel.load(t2ws[0]).get_header().get_zooms()
            t2_res = float(min(t2_zooms[:3]))
            t2_template_res = min(available_resolutions, key=lambda x:abs(float(x)-t2_res))

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
                t1_spacing = layout.get_metadata(t1ws[0])["EffectiveEchoSpacing"]
                t2_spacing = layout.get_metadata(t2ws[0])["EffectiveEchoSpacing"]

                unwarpdir = layout.get_metadata(t1ws[0])["PhaseEncodingDirection"]
                unwarpdir = unwarpdir.replace("i","x").replace("j", "y").replace("k", "z")
                if len(unwarpdir) == 2:
                    unwarpdir = unwarpdir[0]+"-"

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
                        echospacing = total_readout_time / float(phase_len - 1)
                    else:
                        raise RuntimeError("EffectiveEchoSpacing or TotalReadoutTime not defined for the fieldmap intended for T1w image. Please fix your BIDS dataset.")

                    fmap_args.update({"SEPhaseNeg": SEPhaseNeg,
                                      "SEPhasePos": SEPhasePos,
                                      "echospacing": "%.6f"%echospacing,
                                      "seunwarpdir": seunwarpdir,
                                      "avgrdcmethod": "TOPUP"})
            #TODO add support for GE fieldmaps

            struct_stages_dict = OrderedDict([("PreFreeSurfer", partial(run_pre_freesurfer,
                                                    path=args.output_dir,
                                                    subject="sub-%s" %subject_label,
                                                    t1ws=t1ws,
                                                    t2ws=t2ws,
                                                    n_cpus=args.n_cpus,
                                                    t1_template_res=t1_template_res,
                                                    t2_template_res=t2_template_res,
                                                    **fmap_args)),
                           ("FreeSurfer", partial(run_freesurfer,
                                                 path=args.output_dir,
                                                 subject="sub-%s" %subject_label,
                                                 n_cpus=args.n_cpus)),
                           ("PostFreeSurfer", partial(run_post_freesurfer,
                                                     path=args.output_dir,
                                                     subject="sub-%s" %subject_label,
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
                fmriname = "_".join(fmritcs.split("sub-")[-1].split("_")[1:]).split(".")[0]
                assert fmriname
                fmriscout = fmritcs.replace("_bold", "_sbref")
                if not os.path.exists(fmriscout):
                    fmriscout = "NONE"

                fieldmap_set = layout.get_fieldmap(fmritcs, return_list=True)
                if fieldmap_set:
                    for item in fieldmap_set:

                        if item["type"] == "epi":

                            fieldmap = item["epi"]
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
                reptime = float("%.1f" % zooms[3])
                fmrires = float(min(zooms[:3]))
                fmrires = "2"

                # determine which fix training data to use based on resolution and TR

                if zooms[:3] == (2.0, 2.0, 2.0) and (reptime == 0.8 or reptime == 0.7 or reptime == 1.0):
                    highpass = "2000"
                    training_data = "HCP_hp2000.RData"

                func_stages_dict = OrderedDict([("fMRIVolume", partial(run_generic_fMRI_volume_processsing,
                                                                       path=args.output_dir,
                                                                       subject="sub-%s" % (subject_label),
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
                                                                        subject="sub-%s" % (subject_label),
                                                                        fmriname=fmriname,
                                                                        fmrires=fmrires,
                                                                        n_cpus=args.n_cpus,
                                                                        grayordinatesres=grayordinatesres,
                                                                        lowresmesh=lowresmesh))])
                if 'rest' in fmriname:
                    rest_stages_dict = OrderedDict([("ICAFIX", partial(run_ICAFIX_processing,
                                                                       path=args.output_dir,
                                                                       subject="sub-%s" % (subject_label),
                                                                       n_cpus=args.n_cpus,
                                                                       fmriname=fmriname,
                                                                       high_pass=highpass,
                                                                       training_data=training_data)),
                                                    ("PostFix", partial(run_PostFix_processing,
                                                                        path=args.output_dir,
                                                                        subject="sub-%s" % (subject_label),
                                                                        n_cpus=args.n_cpus,
                                                                        fmriname=fmriname,
                                                                        high_pass=highpass)),
                                                    ("RestingStateStats", partial(run_RestingStateStats_processing,
                                                                                  path=args.output_dir,
                                                                                  subject="sub-%s" % (subject_label),
                                                                                  n_cpus=args.n_cpus,
                                                                                  fmriname=fmriname,
                                                                                  high_pass=highpass,
                                                                                  lowresmesh=lowresmesh,
                                                                                  fmrires=fmrires,
                                                                                  grayordinatesres=grayordinatesres,
                                                                                  dlabel_file=dlabel_file))])

            for stage, stage_func in func_stages_dict.iteritems():
                if stage in args.stages:
                    stage_func()
            for stage, stage_func in rest_stages_dict.iteritems():
                if stage in args.stages:
                    stage_func()

            dwis = layout.get(subject=subject_label, type='dwi', extensions=["nii.gz", "nii"])

            pos = []
            neg = []
            PEdir = None;
            echospacing = None

            for idx, dwi in enumerate(dwis):
                metadata = layout.get_metadata(dwi.filename)
                # get phaseencodingdirection
                phaseenc = metadata['PhaseEncodingDirection']
                acq = 1 if phaseenc[0] == 'i' else 2
                if not PEdir:
                    PEdir = acq
                if PEdir != acq:
                    raise RuntimeError(
                        "Not all dwi images have the same encoding direction (both LR and AP). Not implemented.")
                # get pos/neg
                if len(phaseenc) > 1:
                    neg.append(dwi.filename)
                else:
                    pos.append(dwi.filename)
                # get echospacing
                if not echospacing:
                    echospacing = metadata['EffectiveEchoSpacing'] * 1000.
                if echospacing != metadata['EffectiveEchoSpacing'] * 1000.:
                    raise RuntimeError("Not all dwi images have the same echo spacing. Not implemented.")

            posdata = "@".join(pos)
            negdata = "@".join(neg)

            dif_stages_dict = OrderedDict([("DiffusionPreprocessing", partial(run_diffusion_processsing,
                                                                              path=args.output_dir,
                                                                              subject="sub-%s" % (subject_label),
                                                                              n_cpus=args.n_cpus,
                                                                              posData=posdata,
                                                                              negData=negdata,
                                                                              echospacing=echospacing,
                                                                              PEdir=PEdir))])

            for stage, stage_func in dif_stages_dict.iteritems():
                if stage in args.stages:
                    stage_func()
