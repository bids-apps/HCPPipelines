#!/usr/local/miniconda3/bin/python

import argparse
import os
import shutil
import nibabel
from glob import glob
from subprocess import Popen, PIPE
import subprocess
from bids import BIDSLayout
from functools import partial
from collections import OrderedDict


def run(command, env={}, cwd=None):
    merged_env = os.environ.copy()
    merged_env.update(env)
    merged_env.pop("DEBUG", None)
    print(command)
    process = Popen(command, stdout=PIPE, stderr=subprocess.STDOUT,
                    shell=True, env=merged_env, cwd=cwd)
    while True:
        line = process.stdout.readline()
        if line:
            print(line.decode('utf-8', errors='replace').rstrip())
        if not line and process.poll() is not None:
            break
    if process.returncode != 0:
        raise Exception("Non zero return code: %d" % process.returncode)


grayordinatesres = "2"  # This is currently the only option for which there is an atlas
lowresmesh = 32


def get_fieldmap(layout, target_file, return_list=False):
    """
    Find fieldmaps intended for target_file.
    Replaces layout.get_fieldmap() which was removed in pybids >= 0.9.

    return_list=False: returns a single dict {type, ...} or None
    return_list=True:  returns a list of dicts or []
    """
    bids_root = layout.root
    target_basename = os.path.basename(target_file)
    rel_target = os.path.relpath(target_file, bids_root)

    fmaps = layout.get(datatype='fmap', extension=['.nii.gz', '.nii'])

    matched = []
    for fmap in fmaps:
        intended = layout.get_metadata(fmap.path).get('IntendedFor', [])
        if isinstance(intended, str):
            intended = [intended]
        for intended_file in intended:
            if (intended_file.endswith(target_basename) or
                    intended_file == rel_target or
                    target_file.endswith(intended_file)):
                matched.append(fmap)
                break

    if not matched:
        return [] if return_list else None

    suffixes = set(f.suffix for f in matched)

    if 'phasediff' in suffixes:
        result = {'type': 'phasediff'}
        for f in matched:
            if f.suffix == 'phasediff':
                result['phasediff'] = f.path
            elif f.suffix in ('magnitude1', 'magnitude2'):
                result[f.suffix] = f.path
        return [result] if return_list else result

    if 'epi' in suffixes:
        epi_files = [f.path for f in matched if f.suffix == 'epi']
        if return_list:
            return [{'type': 'epi', 'epi': p} for p in epi_files]
        else:
            return {'type': 'epi', 'epi': epi_files}

    return [] if return_list else None


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
        '--gdcoeffs={gdcoeffs} ' + \
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

    for subj_dir_name in ["fsaverage", "lh.EC_average", "rh.EC_average"]:
        dest = os.path.join(args["subjectDIR"], subj_dir_name)
        if not os.path.exists(dest):
            shutil.copytree(os.path.join(os.environ["SUBJECTS_DIR"], subj_dir_name), dest)

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
        '--regname="{regname}" ' + \
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
        '--gdcoeffs={gdcoeffs} ' + \
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
        '--regname="{regname}"'
    cmd = cmd.format(**args)
    run(cmd, cwd=args["path"], env={"OMP_NUM_THREADS": str(args["n_cpus"])})


def run_generic_fMRI_ICAFIX_processsing(**args):
    args.update(os.environ)
    cmd = '/opt/fix/hcp_fix {path}/{subject}/MNINonLinear/Results/{fmriname}/{fmriname}.nii.gz 2000'
    cmd = cmd.format(**args)
    run(cmd, cwd=args["path"], env={"OMP_NUM_THREADS": str(args["n_cpus"])})
    cmd = '/opt/fix/zhh_fix {path}/{subject}/MNINonLinear/Results/{fmriname}/{fmriname}.nii.gz 2000'
    cmd = cmd.format(**args)
    run(cmd, cwd=args["path"], env={"OMP_NUM_THREADS": str(args["n_cpus"])})


def run_diffusion_processsing(**args):
    args.update(os.environ)
    cmd = '{HCPPIPEDIR}/DiffusionPreprocessing/DiffPreprocPipeline.sh ' + \
        '--posData="{posData}" ' + \
        '--negData="{negData}" ' + \
        '--path="{path}" ' + \
        '--subject="{subject}" ' + \
        '--echospacing="{echospacing}" ' + \
        '--PEdir={PEdir} ' + \
        '--gdcoeffs={gdcoeffs} ' + \
        '--printcom=""'
    cmd = cmd.format(**args)
    run(cmd, cwd=args["path"], env={"OMP_NUM_THREADS": str(args["n_cpus"])})


__version__ = open('/version').read()

parser = argparse.ArgumentParser(description='HCP Pipelines BIDS App (T1w, T2w, fMRI)')
parser.add_argument('bids_dir', help='The directory with the input dataset '
                    'formatted according to the BIDS standard.')
parser.add_argument('output_dir', help='The directory where the output files '
                    'should be stored.')
parser.add_argument('analysis_level', help='Level of the analysis that will be performed.',
                    choices=['participant'])
parser.add_argument('--participant_label', nargs="+",
                    help='Label(s) of participant(s) to analyze (without "sub-" prefix).')
parser.add_argument('--n_cpus', default=1, type=int,
                    help='Number of CPUs/cores available to use.')
parser.add_argument('--stages', nargs="+",
                    choices=['PreFreeSurfer', 'FreeSurfer', 'PostFreeSurfer',
                             'fMRIVolume', 'fMRISurface', 'ICAFIX', 'DiffusionPreprocessing'],
                    default=['PreFreeSurfer', 'FreeSurfer', 'PostFreeSurfer',
                             'fMRIVolume', 'fMRISurface', 'ICAFIX', 'DiffusionPreprocessing'],
                    help='Which stages to run.')
parser.add_argument('--coreg', choices=['MSMSulc', 'FS'], default='MSMSulc',
                    help='Coregistration method to use.')
parser.add_argument('--gdcoeffs', default="NONE",
                    help='Gradient coefficients file.')
parser.add_argument('--license_key', required=True,
                    help='FreeSurfer license key.')
parser.add_argument('-v', '--version', action='version',
                    version='HCP Pipelines BIDS App version {}'.format(__version__))

args = parser.parse_args()

# Write FreeSurfer license
with open(os.path.join(os.environ["FREESURFER_HOME"], "license.txt"), "w") as f:
    f.write("user@example.com\n12345\n *{}\nFS5J/2c1agg4E\n".format(args.license_key))

run("bids-validator " + args.bids_dir)

layout = BIDSLayout(args.bids_dir, derivatives=False)

if args.participant_label:
    subjects_to_analyze = args.participant_label
else:
    subject_dirs = glob(os.path.join(args.bids_dir, "sub-*"))
    subjects_to_analyze = [os.path.basename(d).split("-")[-1] for d in subject_dirs]

if args.analysis_level == "participant":
    for subject_label in subjects_to_analyze:
        # ── Structural files ──────────────────────────────────────────────
        t1ws = [f.path for f in layout.get(subject=subject_label,
                                            suffix='T1w',
                                            extension=['.nii.gz', '.nii'])]
        t2ws = [f.path for f in layout.get(subject=subject_label,
                                            suffix='T2w',
                                            extension=['.nii.gz', '.nii'])]
        assert len(t1ws) > 0, "No T1w files found for subject %s!" % subject_label
        assert len(t2ws) > 0, "No T2w files found for subject %s!" % subject_label

        available_resolutions = ["0.7", "0.8", "1"]
        t1_zooms = nibabel.load(t1ws[0]).header.get_zooms()
        t1_res = float(min(t1_zooms[:3]))
        t1_template_res = min(available_resolutions, key=lambda x: abs(float(x) - t1_res))
        t2_zooms = nibabel.load(t2ws[0]).header.get_zooms()
        t2_res = float(min(t2_zooms[:3]))
        t2_template_res = min(available_resolutions, key=lambda x: abs(float(x) - t2_res))

        # ── Structural fieldmap ───────────────────────────────────────────
        fieldmap_set = get_fieldmap(layout, t1ws[0])
        fmap_args = {"fmapmag": "NONE", "fmapphase": "NONE", "echodiff": "NONE",
                     "t1samplespacing": "NONE", "t2samplespacing": "NONE",
                     "unwarpdir": "NONE", "avgrdcmethod": "NONE",
                     "SEPhaseNeg": "NONE", "SEPhasePos": "NONE",
                     "echospacing": "NONE", "seunwarpdir": "NONE"}

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
                merged_file = "%s/tmp/%s/magfile.nii.gz" % (args.output_dir, subject_label)
                run("mkdir -p %s/tmp/%s/ && fslmerge -t %s %s %s" % (
                    args.output_dir, subject_label, merged_file,
                    fieldmap_set["magnitude1"], fieldmap_set["magnitude2"]))
                phasediff_metadata = layout.get_metadata(fieldmap_set["phasediff"])
                te_diff = (phasediff_metadata["EchoTime2"] - phasediff_metadata["EchoTime1"]) * 1000.0
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
                fmap_meta = layout.get_metadata(fieldmap_set["epi"][0])
                if "EffectiveEchoSpacing" in fmap_meta:
                    echospacing = fmap_meta["EffectiveEchoSpacing"]
                elif "TotalReadoutTime" in fmap_meta:
                    print("BIDS App wrapper: Did not find EffectiveEchoSpacing, calculating from TotalReadoutTime")
                    total_readout_time = fmap_meta["TotalReadoutTime"]
                    phase_len = nibabel.load(fieldmap_set["epi"][0]).shape[{"x": 0, "y": 1}[seunwarpdir]]
                    echospacing = total_readout_time / float(phase_len - 1)
                else:
                    raise RuntimeError("EffectiveEchoSpacing or TotalReadoutTime not defined for fieldmap.")
                fmap_args.update({"SEPhaseNeg": SEPhaseNeg, "SEPhasePos": SEPhasePos,
                                  "echospacing": "%.6f" % echospacing,
                                  "seunwarpdir": seunwarpdir,
                                  "avgrdcmethod": "TOPUP"})

        # ── Run structural stages ─────────────────────────────────────────
        struct_stages_dict = OrderedDict([
            ("PreFreeSurfer", partial(run_pre_freesurfer,
                                      path=args.output_dir,
                                      subject="sub-%s" % subject_label,
                                      t1ws=t1ws, t2ws=t2ws,
                                      n_cpus=args.n_cpus,
                                      t1_template_res=t1_template_res,
                                      t2_template_res=t2_template_res,
                                      gdcoeffs=args.gdcoeffs, **fmap_args)),
            ("FreeSurfer", partial(run_freesurfer,
                                   path=args.output_dir,
                                   subject="sub-%s" % subject_label,
                                   n_cpus=args.n_cpus)),
            ("PostFreeSurfer", partial(run_post_freesurfer,
                                       path=args.output_dir,
                                       subject="sub-%s" % subject_label,
                                       grayordinatesres=grayordinatesres,
                                       lowresmesh=lowresmesh,
                                       n_cpus=args.n_cpus,
                                       regname=args.coreg)),
        ])
        for stage, stage_func in struct_stages_dict.items():
            if stage in args.stages:
                stage_func()

        # ── Functional runs ───────────────────────────────────────────────
        bolds = [f.path for f in layout.get(subject=subject_label,
                                             suffix='bold',
                                             extension=['.nii.gz', '.nii'])]
        for fmritcs in bolds:
            fmriname = "_".join(fmritcs.split("sub-")[-1].split("_")[1:]).split(".")[0]
            assert fmriname

            fmriscout = fmritcs.replace("_bold", "_sbref")
            if not os.path.exists(fmriscout):
                fmriscout = "NONE"

            fieldmap_set = get_fieldmap(layout, fmritcs, return_list=True)
            if fieldmap_set and len(fieldmap_set) == 2 and all(item["type"] == "epi" for item in fieldmap_set):
                SEPhaseNeg = None
                SEPhasePos = None
                for fieldmap in fieldmap_set:
                    enc_dir = fieldmap['epi'].split('_dir-')[1].split('_')[0]
                    if "AP" in enc_dir:
                        SEPhaseNeg = fieldmap['epi']
                    else:
                        SEPhasePos = fieldmap['epi']
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

            zooms = nibabel.load(fmritcs).header.get_zooms()
            fmrires = float(min(zooms[:3]))
            fmrires = "2"  # hardcoded: only 2mm atlas available for grayordinate projection

            func_stages_dict = OrderedDict([
                ("fMRIVolume", partial(run_generic_fMRI_volume_processsing,
                                       path=args.output_dir,
                                       subject="sub-%s" % subject_label,
                                       fmriname=fmriname, fmritcs=fmritcs,
                                       fmriscout=fmriscout,
                                       SEPhaseNeg=SEPhaseNeg, SEPhasePos=SEPhasePos,
                                       echospacing=echospacing, unwarpdir=unwarpdir,
                                       fmrires=fmrires, dcmethod=dcmethod,
                                       biascorrection=biascorrection,
                                       n_cpus=args.n_cpus, gdcoeffs=args.gdcoeffs)),
                ("fMRISurface", partial(run_generic_fMRI_surface_processsing,
                                        path=args.output_dir,
                                        subject="sub-%s" % subject_label,
                                        fmriname=fmriname, fmrires=fmrires,
                                        n_cpus=args.n_cpus,
                                        grayordinatesres=grayordinatesres,
                                        lowresmesh=lowresmesh,
                                        regname=args.coreg)),
                ("ICAFIX", partial(run_generic_fMRI_ICAFIX_processsing,
                                   path=args.output_dir,
                                   subject="sub-%s" % subject_label,
                                   fmriname=fmriname, fmrires=fmrires,
                                   n_cpus=args.n_cpus,
                                   grayordinatesres=grayordinatesres,
                                   lowresmesh=lowresmesh)),
            ])
            for stage, stage_func in func_stages_dict.items():
                if stage in args.stages:
                    stage_func()
