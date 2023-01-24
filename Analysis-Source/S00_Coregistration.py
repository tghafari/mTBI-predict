# -*- coding: utf-8 -*-
"""
===============================================
S00. Coregistration and preparing trans file

This script coregisteres the MEG file with MRI
and generates the trans file (which is necessary
                              for BIDS conversion)

written by Tara Ghafari
adapted from Oscar Ferrante
==============================================
ToDos:
    1) 
    
Issues/ contributions to community:
    1) 
    
Questions:
    1)
Notes:
    Step 1: Reconstructing MRI using FreeSurfer
    Step 2: Reconstructing the scalp surface
    Step 3: Getting Boundary Element Model (BEM)
    Step 4: Getting BEM solution
    Step 5: Coregistration (Manual prefered)
    
    Run recon_all on freesurfer before this script.
    Steps 1, 2, and 3 are also included in the my_recon.sh bash script
"""
import numpy as np
import os.path as op

import mne
from mne_bids import BIDSPath, read_raw_bids


# subject info 
site = 'Birmingham'
subject = '04'  # subject code in mTBI project
session = '01'  # data collection session within each run
run = '01'  # data collection run for each participant
pilot = 'P' # is the data collected 'P'ilot or 'T'ask?
task = 'SpAtt'
meg_extension = '.fif'
meg_suffix = 'meg'
deriv_suffix = 'coreg-trans'
bem_suffix = 'bem-sol'
fs_sub = f'sub-{subject}'  # FreeSurfer subject name

# Specify specific file names
bids_root = r'Z:\Projects\mTBI_predict\Collected_Data\MNE-bids-data' #'-anonymized'  # RDS folder for bids formatted data
bids_path = BIDSPath(subject=subject, session=session,
                     task=task, run=run, root=bids_root, 
                     suffix=meg_suffix, extension=meg_extension)
deriv_folder = op.join(bids_root, 'derivatives', 'flux-pipeline',
                       'sub-' + subject, 'task-' + task)  # RDS folder for results
deriv_fname = bids_path.basename.replace(meg_suffix, deriv_suffix)
bem_fname = deriv_fname.replace(deriv_suffix, bem_suffix)  # save in the bids folder

fs_sub_dir = r'Z:\Projects\mTBI_predict\Collected_Data\MRI_data\sub-04'  # FreeSurfer directory (after running recon all)
mr_figname = op.join(fs_sub_dir, 'fs_parsed.png')  # save figures in the MRI folder
bem_figname = mr_figname.replace('fs_parsed', 'bem_sol')
coreg_figname = mr_figname.replace('fs_parsed', 'final_coreg')

""" Steps 1, 2, and 3 - no need to run them here if you use bluebear"""
# Step 1: reconstruct the MRI file using freesurfer 
Brain = mne.viz.get_brain_class()
brain = Brain(fs_sub, hemi='lh', surf='pial',
              subjects_dir=fs_sub_dir, size=(800,600))
brain.save_image(mr_figname)

# Step 2: reconstruct the scalp surface
mne.bem.make_scalp_surface(subject=fs_sub, subjects_dir=fs_sub_dir,
                           force=True, overwrite=True, verbose=True,
                           mri='T1.mgz')  # mri should exist in subject_dir/subject/mri

# Step 3: reconstruct Boundary Element Model (BEM)
mne.bem.make_watershed_bem(subject=fs_sub, subjects_dir=fs_sub_dir,
                           overwrite=True, verbose=True)

""" Steps 4 and 5 should be run here"""
# Step 4: Get Boundary Element model (BEM) solution
""" run this section after the watershed_bem surfaces are read in freesurfer,
(using my_recon.sh batch script)"""

# Creat BEM model
conductivity = (.3,)  # for single layer
# conductivity = (.3, .006, .3)  # for three layers
model = mne.make_bem_model(subject=fs_sub, subjects_dir=fs_sub_dir,
                           ico=4, conductivity=conductivity)

# BEM solution is derived from the BEM model
bem = mne.make_bem_solution(model)
mne.write_bem_solution(bem_fname, bem, overwrite=True, verbose=True)
# Visualize the BEM
fig = mne.viz.plot_bem(subject=fs_sub, subjects_dir=fs_sub_dir,
                       orientation='coronal', brain_surfaces='white')
fig.savefig(bem_figname)

# Step 5: Coregistration
""" trans file is created here for later use in bids and then
the source-base analysis.
1) save the trans file in the MRI folder
2) rename and move the transfile to bids structure using
    01_bids_conversion... script
"""

## AUTOMATED COREGISTRATION ## 
info = read_raw_bids(bids_path=bids_path, verbose=False).info
plot_kwargs = dict(subject=fs_sub, subjects_dir=fs_sub_dir,
                   surfaces="head-dense", dig=True,
                   eeg=[], meg='sensors', show_axes=True,
                   coord_frame='meg')
view_kwargs = dict(azimuth=45, elevation=90, distance=.6,
                   focalpoint=(0.,0.,0.,))

# Set up the coregistration model
fiducials = "estimated"  # gets fiducials from fsaverage
coreg = mne.coreg.Coregistration(info, subject=fs_sub, 
                                 subjects_dir=fs_sub_dir,
                                 fiducials=fiducials)
mne.write_trans(deriv_fname, coreg.trans)
fig = mne.viz.plot_alignment(info, trans=coreg.trans, **plot_kwargs)

# Initial fit with fiducials
""" firstly fit with 3 fiducial points. This allows to find a good
initial solution before optimization using head shape points"""
coreg.fit_fiducials(verbose=True)
fig = mne.viz.plot_alignment(info, trans=coreg.trans, **plot_kwargs)

# Refining with ICP
""" secondly we refine the transformation using a few iterations of the
Iterative Closest Point (ICP) algorithm."""
coreg.fit_icp(n_iterations=6, nasion_weight=2., verbose=True)
fig = mne.viz.plot_alignment(info, trans=coreg.trans, **plot_kwargs)

# Omitting bad points
""" we now remove the points that are not on the scalp"""
coreg.omit_head_shape_points(distance=5. /1000)  # distance is in meters

# Final coregistration fit
coreg.fit_icp(n_iterations=20, nasion_weight=10., verbose=True)
coreg_fig = mne.viz.plot_alignment(info, trans=coreg.trans, **plot_kwargs)
mne.viz.set_3d_view(fig, **view_kwargs)
coreg_fig.savefig(coreg_figname)

dists = coreg.compute_dig_mri_distances() * 1e3  # in mm
print(f"Distance between HSP and MRI (mean/min/max):\n{np.mean(dists):.2f} mm "
      f"/ {np.min(dists):.2f} mm / {np.max(dists):.2f} mm")

### MANUAL COREGISTRATION ##
""" manually pick the fiducials and coregister MEG with MRI.
for instructions check out:https://www.youtube.com/watch?v=ALV5qqMHLlQ""" 

mne.gui.coregistration(subject=fs_sub, subjects_dir=fs_sub_dir)

















