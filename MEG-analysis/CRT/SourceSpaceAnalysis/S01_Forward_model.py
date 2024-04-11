# -*- coding: utf-8 -*-
"""
===============================================
S01. Constructing the forward model

This script constructs the head model to be used
as a lead field matrix, in source modelling. 
This is based on the T1 MRI. This model will 
be aligned to head position of the subject in the
MEG system. 

written by Alice Waitt
originally written by Tara Ghafari
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
#%%
import os.path as op

import mne
from mne_bids import BIDSPath, read_raw_bids

# subject info 
site = 'Aston'
subject = '2001'  # subject code in mTBI project
session = '04A'  # data collection session within each run
run = '01'  # data collection run for each participant
pilot = 'T' # is the data collected 'P'ilot or 'T'ask?
task = 'CRT' #'rest'

meg_extension = '.fif'
input_suffix = 'trans'
meg_suffix = 'meg'
surf_suffix = 'surf-src'
vol_suffix = 'vol-src'
bem_suffix = 'bem-sol'
fwd_suffix = 'fwd'
fs_sub = 'T1_2001' #f'sub-{subject}'  # FreeSurfer subject name

space = 'volume'  # what to use for source modeling? surface or volume

platform = 'laptop' #'bluebear' # are you using 'bluebear', 'windows' or 'laptop'?

#%%
# Specify specific file names
if platform == 'bluebear':
    rds_dir = r'/rds/projects/s/sidhuc-mtbi-data' #r'\\its-rds.bham.ac.uk\rdsprojects\s\sidhuc-mtbi-data' #'/rds/projects/j/jenseno-avtemporal-attention'
    data_root = op.join(rds_dir, r'Alice_Aston_testing')
    #mTBI_root = op.join(rds_dir, r'Projects/mTBI-predict')
    #data_root = op.join(mTBI_root, 'collected-data')
elif platform == 'laptop':
    rds_dir = r'C:\Users\waitta\Documents\ClusterDocs'
    data_root = op.join(rds_dir, 'BearTestSub')
#elif platform == 'windows':
#    rds_dir = 'Z:'
#    data_root = r'C:\Users\waitta\Documents\ClusterDocs\BearTestSub' #r'/clinical/vol113/raw-sub-data/'
#r'/clinical/vol113/pilot_data/P002/MEG/20230622_p002/230622'

# Specify specific file names
bids_root = op.join(data_root, 'BIDS', 'task_BIDS')  # RDS folder for bids formatted data
bids_path = BIDSPath(subject=subject, session=session,
                     task=task, run=run, root=bids_root, 
                     suffix=meg_suffix, extension=meg_extension)
deriv_folder = op.join(bids_root ,  'derivatives', 'sub-' + subject, 'ses-' +session, 'task-' + task,'run-' + run) # RDS folder for results
input_fname = bids_path.basename.replace(meg_suffix, input_suffix)
trans = op.join(deriv_folder, input_fname)
surf_fname = trans.replace(input_suffix, surf_suffix)  # only used for suffices that are not recognizable to bids 
vol_fname = surf_fname.replace(surf_suffix, vol_suffix)  # save in the bids folder
bem_fname = surf_fname.replace(surf_suffix, bem_suffix)  
fwd_fname = surf_fname.replace(surf_suffix, fwd_suffix)

fs_sub_dir = op.join(bids_root, 'sub-' + subject, 'ses-' + session, 'anat')  # FreeSurfer directory (after running recon all)
surface = op.join(fs_sub_dir, fs_sub, 'bem', 'inner_skull.surf')

#%%
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

#%% 
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
    
#%%
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
print(f"Before: {src}")
print(f'After:  {fwd["src"]}')

leadfield = fwd['sol']['data']  # size of leadfield
print("\nLeadfield size: %d sensors x %d dipoles" %leadfield.shape)
