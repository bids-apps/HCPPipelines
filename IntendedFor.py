#!/usr/bin/python
import json
import os
from glob import glob
import numpy

"""
This script is designed to determine which field maps apply to discrete fMRI scans

Author - Timothy J Hendrickson
"""
subject_path = "/home/naxos2-raid8/mangia-data/DATA_R01_rsfMRI/analyzed/BIDS_output/sub-patient03"
def setup(subject_path):
	if "ses" in os.listdir(subject_path)[0]:
		for item in (os.listdir(subject_path)):
			session_path = subject_path + '/'+ item
			IntendedFor(session_path)
	IntendedFor(subject_path)

def IntendedFor(data_path):
	for fmap in sorted(glob(data_path+'/fmap/*.json')):
		with open(fmap, 'r') as f:
			fmap_json = json.load(f)
			f.close()
		if "IntendedFor" in fmap_json:
			del fmap_json["IntendedFor"]
		shim_fmap = fmap_json["ShimSetting"]
		patient_pos_fmap = fmap_json["ImageOrientationPatientDICOM"]
		func_list = []
		for func in sorted(glob(data_path+'/func/*bold.json')):
			with open(func, 'r') as g:
				func_json = json.load(g)
				shim_func = func_json["ShimSetting"]
				patient_pos_func = func_json["ImageOrientationPatientDICOM"]
				g.close()
			if shim_fmap == shim_func:
				func_nii = glob(data_path+'/func/' +func.split('/')[-1].split('.')[0]+".nii*")[0]
				if "ses" in data_path:
					func_nii = "/".join(func_nii.split("/")[-3:])
					func_list.append(func_nii)
				else:
					func_nii = "/".join(func_nii.split("/")[-2:])
					func_list.append(func_nii)
			elif patient_pos_fmap == patient_pos_func:
				shim_func_np = numpy.array(shim_func)
				shim_fmap_np = numpy.array(shim_fmap)
				diff_shims = shim_fmap_np - shim_func_np
				print("difference between fieldmap and functional scan is " + str(sum(abs(diff_shims))))
				user_input = raw_input("Do you accept this difference? [y/n]: ")
				if user_input == 'y':
					func_nii = glob(data_path + '/func/' + func.split('/')[-1].split('.')[0] + ".nii*")[0]
					if "ses" in data_path:
						func_nii = "/".join(func_nii.split("/")[-3:])
						func_list.append(func_nii)
					else:
						func_nii = "/".join(func_nii.split("/")[-2:])
						func_list.append(func_nii)
				else:
					print(fmap + " does not have match yet...")
		entry = {"IntendedFor": func_list}

		fmap_json.update(entry)
		with open(fmap, 'w') as f:
			json.dump(fmap_json, f)
			f.close()

setup(subject_path)