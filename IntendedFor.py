#!/usr/bin/python
import json
import os
from glob import glob

"""
This script is designed to determine which field maps apply to discrete fMRI scans

Author - Timothy J Hendrickson
"""

def setup(subject_path):
	if "ses" in os.listdir(subject_path)[0]:
		for item in (os.listdir(subject_path)):
			session_path = subject_path + '/'+ item
			IntendedFor(session_path)
	IntendedFor(subject_path)

def IntendedFor(data_path):
	for fmap in glob(data_path+'/fmap/*.json'):
		with open(fmap, 'r') as f:
			fmap_json = json.load(f)
			f.close()
		if not "IntendedFor" in fmap_json:
			shim_fmap = fmap_json["ShimSetting"]
			func_list = []
			for func in glob(data_path+'/func/*bold.json'):
				with open(func, 'r') as g:
					func_json = json.load(g)
					shim_func = func_json["ShimSetting"]
					g.close()
				if shim_fmap == shim_func:
					func_nii = glob(data_path+'/func/' +func.split('/')[-1].split('.')[0]+".nii*")[0]
					if "ses" in data_path:
						func_nii = "/".join(func_nii.split("/")[-3:])
						func_list.append(func_nii)
					else:
						func_nii = "/".join(func_nii.split("/")[-2:])
						func_list.append(func_nii)
			entry = {"IntendedFor": func_list}

			fmap_json.update(entry)
			with open(fmap, 'w') as f:
				json.dump(fmap_json, f)
				f.close()
		else:
			print(fmap + " already exists for this session")
