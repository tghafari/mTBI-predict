# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 15:07:25 2024

@author: ppzdf
"""
import os
import os.path as op

import numpy as np
import mne
from mne_bids import BIDSPath, read_raw_bids, inspect_dataset
from matplotlib import pyplot as plt

#%%

subject = '2003'
session = '03N'
task = 'CRT'  # name of the task
run = '01'  # we have two runs for this subject, let's look at run = 1
suffix = 'meg'
fs_subject  = 'sub-' + subject

#%%

bids_root = r'R:\DRS-mTBI\Seb\mTBI_predict\BIDS'
deriv_root = r'R:\DRS-mTBI\Dan\mTBI_predict\derivatives'
subjects_dir = r"R:\DRS-mTBI\Dan\Practice\FreeSurfer_SUBJECTS"

bids_path = BIDSPath(subject=subject, session=session,
task=task, run=run, suffix=suffix, root=bids_root)

deriv_path = BIDSPath(subject=subject, session=session,
task=task, run=run, suffix=suffix, root=deriv_root)

#%%

data = mne.io.Raw(op.join(deriv_path.directory, 
                          deriv_path.basename + "_ica_preproc.fif"))
trans = op.join(deriv_path.directory, deriv_path.basename + "-trans.fif")
#%%

plot_bem_kwargs= dict(
    subject=fs_subject,
    subjects_dir=subjects_dir,
    brain_surfaces="white",
    orientation="coronal",
    slices=[50,100,150,200])

mne.viz.plot_bem(**plot_bem_kwargs)

#%%Surface source space

surf_file = op.join(subjects_dir, fs_subject, "bem", "inner_skull.surf")

src = mne.setup_source_space(
    fs_subject, spacing="oct6", add_dist=False, subjects_dir=subjects_dir)
src.plot(subjects_dir=subjects_dir)

mne.viz.plot_bem(src=src, **plot_bem_kwargs)

src_fname = deriv_path.basename + "-ica_src.fif"
src.save(op.join(deriv_path.directory, src_fname), overwrite=True)

#%%Volume Source Space

surf_file = op.join(subjects_dir, fs_subject, "bem", "inner_skull.surf")

src_vol = mne.setup_volume_source_space(
    fs_subject,
    subjects_dir=subjects_dir,
    #pos=8, 
    mri = 'T1.mgz',
    surface=surf_file,
    verbose = True
)
mne.viz.plot_bem(src=src_vol, **plot_bem_kwargs)

src_vol_fname = deriv_path.basename + "-ica_src_vol.fif"
src.save(op.join(deriv_path.directory, src_vol_fname), overwrite=True)

#%%

fig = mne.viz.plot_alignment(
    subject=fs_subject,
    subjects_dir=subjects_dir,
    trans=trans,
    surfaces="white",
    coord_frame="head",
    src=src,
)

mne.viz.set_3d_view(
    fig,
    azimuth=173.78,
    elevation=101.75,
    distance=0.30,
    focalpoint=(-0.03, -0.01, 0.03)
)

#%%Single Shell Conduction Model

conductivity = (0.3,)
model=mne.make_bem_model(
    subject=fs_subject,
    ico=4,
    conductivity=conductivity,
    subjects_dir=subjects_dir
)

bem = mne.make_bem_solution(model)

bem_fname = deriv_path.basename + "-ica_bem.fif"
mne.write_bem_solution(op.join(deriv_path.directory, bem_fname), bem, overwrite=True)

#%%computing forward solution

fwd = mne.make_forward_solution(
    data.info,
    trans=trans,
    src=src,
    bem=bem,
    meg=True,
    eeg=False,
    mindist = 5.0,
    )
print(fwd)

fwd_fname = deriv_path.basename + "-ica_fwd.fif"
mne.write_forward_solution(op.join(deriv_path.directory, fwd_fname),fwd, overwrite=True)
