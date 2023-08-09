# -*- coding: utf-8 -*-
"""
===============================================
S01. Constructing the forward model

This script constructs the head model to be used
as a lead field matrix, in source modelling. 
This is based on the T1 MRI. This model will 
be aligned to head position of the subject in the
MEG system. 

written by Tara Ghafari
adapted from flux pipeline
==============================================
ToDos:
    1) 
    
Issues/ contributions to community:
    1) 
    
Questions:
    1)

Notes:
    Step 1: Computing source space
    Step 2: Forward model

"""
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
input_suffix = 'coreg-trans'
meg_suffix = 'meg'
surf_suffix = 'surf-src'
vol_suffix = 'vol-src'
bem_suffix = 'bem-sol'
fwd_suffix = 'fwd'
fs_sub = f'sub-{subject}'  # FreeSurfer subject name

space = 'volume'  # what to use for source modeling? surface or volume
# Specify specific file names
bids_root = r'Z:\Projects\mTBI_predict\Collected_Data\MNE-bids-data' #'-anonymized'  # RDS folder for bids formatted data
bids_path = BIDSPath(subject=subject, session=session,
                     task=task, run=run, root=bids_root, 
                     suffix=meg_suffix, extension=meg_extension)
deriv_folder = op.join(bids_root, 'derivatives', 'flux-pipeline',
                       'sub-' + subject, 'task-' + task)  # RDS folder for results
input_fname = bids_path.basename.replace(meg_suffix, input_suffix)
trans = op.join(deriv_folder, input_fname)

surf_fname = trans.replace(input_suffix, surf_suffix)  # only used for suffices that are not recognizable to bids 
vol_fname = surf_fname.replace(surf_suffix, vol_suffix)  # save in the bids folder
bem_fname = surf_fname.replace(surf_suffix, bem_suffix)  
fwd_fname = surf_fname.replace(surf_suffix, fwd_suffix)

fs_sub_dir = r'Z:\Projects\mTBI_predict\Collected_Data\MRI_data\sub-04'  # FreeSurfer directory (after running recon all)
surface = op.join(fs_sub_dir, fs_sub, 'bem', 'inner_skull.surf')

# Step 1: Compute source space according to BEM 
""" The source space is defined by a grid covering brain volume.
--volume vs surface is for next steps of analysis"""

if space == 'surface':
    # Surface-based source space
    spacing = 'oct6'  # 4098 sources per hemisphere, 4.9 mm spacing
    src = mne.setup_source_space(subject=fs_sub, subjects_dir=fs_sub_dir, 
                                 spacing=spacing, add_dist='patch')
    mne.write_source_spaces(surf_fname, src, overwrite=True)
    
elif space == 'volume':
    # Volumetric source space (BEM required)
    src = mne.setup_volume_source_space(subject=fs_sub,
                                        subjects_dir=fs_sub_dir,
                                        surface=surface,
                                        mri='T1.mgz',
                                        verbose=True)
    mne.write_source_spaces(vol_fname, src, overwrite=True)
    
# Visualize source space and BEM
mne.viz.plot_bem(subject=fs_sub, subjects_dir=fs_sub_dir,
                 brain_surfaces='white', src=src, orientation='coronal')

# Visualize sources in 3D space
if space == 'surface':
    fig = mne.viz.plot_alignment(subject=fs_sub, subjects_dir=fs_sub_dir,
                                 trans=trans, surfaces='white',
                                 coord_frame='head', src=src)
    mne.viz.set_3d_view(fig, azimuth=173.78, elevation=101.75,
                        distance=0.35, focalpoint=(-0.03, 0.01, 0.03))
    
# Step 2: Construct the forward model
""" 
The last step is to construct the forward model by assigning a lead-field 
to each source location in relation to the head position with respect to 
the sensors. This will result in the lead-field matrix.
"""
info = read_raw_bids(bids_path=bids_path, verbose=False).info
fwd = mne.make_forward_solution(info, trans, src, bem=bem_fname,
                                meg=True, eeg=False, verbose=True, 
                                mindist=5.) # could be 2.5
mne.write_forward_solution(fwd_fname, fwd)

# Print some details
print(f'\nNumber of vertices: {fwd["src"]}')
leadfield = fwd['sol']['data']  # size of leadfield
print("\nLeadfield size: %d sensors x %d dipoles" %leadfield.shape)


























