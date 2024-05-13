# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 15:04:33 2024

@author: ppysc6
"""
#%%
import os.path as op
import numpy as np
import mne
from mne_bids import BIDSPath, read_raw_bids
from mne.preprocessing import find_bad_channels_maxwell

### need the following line so 3d plotting works, for some reason
mne.viz.set_3d_options(depth_peeling=False, antialias=False)

#%% set up BIDS path
bids_root = r'C:\Users\waitta\Documents\ClusterDocs\BearTestSub\BIDS\task_BIDS'
deriv_root = r'C:\Users\waitta\Documents\ClusterDocs\BearTestSub\BIDS\task_BIDS\derivatives'

# scanning session info
subject = '2003'
session = '06A'
task = 'CRT'  # name of the task
run = '01'
suffix = 'meg'

bids_path = BIDSPath(subject=subject, session=session,
task=task, run=run, suffix=suffix, root=bids_root)

deriv_path = BIDSPath(subject=subject, session=session,
task=task, run=run, suffix=suffix, root=deriv_root)

#%% load data
#data = mne.io.Raw(op.join(bids_path.directory, suffix, bids_path.basename + ".fif"))

data = mne.io.Raw(op.join(deriv_path.directory, deriv_path.basename + "-raw.fif"))
data.pick("meg")

#%% Get FS reconstruction for subject or use fsaverage for quick testing

#subjects_dir = op.dirname(mne.datasets.fetch_fsaverage(verbose=True))   # for fsaverage
subjects_dir = r'C:\Users\waitta\Documents\ClusterDocs\BearTestSub\BIDS\task_BIDS\derivatives\freesurfer'

# Name of the subject directory in FS subjects_dir
fs_subject = "sub-2003_ses-06A"
#fs_subject = "fsaverage"

plot_bem_kwargs = dict(
    subject=fs_subject,
    subjects_dir=subjects_dir,
    brain_surfaces="white",
    orientation="coronal",
    slices=[50, 100, 150, 200])

mne.viz.plot_bem(**plot_bem_kwargs)

#%% coregistration

plot_kwargs = dict(
    subject=fs_subject,
    subjects_dir=subjects_dir,
    surfaces="head-dense",
    dig=True,
    meg="sensors",
    show_axes=True,
    coord_frame="meg",
)

coreg = mne.coreg.Coregistration(data.info, fs_subject, 
                            subjects_dir=subjects_dir)
mne.viz.plot_alignment(data.info, trans=coreg.trans, **plot_kwargs)
coreg.fit_fiducials()
coreg.set_grow_hair(0)
coreg.fit_icp(20)
coreg.omit_head_shape_points(5 / 1000)
coreg.fit_icp(20)
coreg.omit_head_shape_points(5 / 1000)
coreg.fit_icp(20)
coreg.omit_head_shape_points(5 / 1000)
coreg.fit_icp(20)
mne.viz.plot_alignment(data.info, trans=coreg.trans, **plot_kwargs)

trans_fname = deriv_path.basename + "-trans.fif"
coreg.trans.save(op.join(deriv_path.directory, trans_fname), overwrite=True)
#mne.gui.coregistration(subject=fs_subject, subjects_dir=subjects_dir)

#%% source space

surf_file = op.join(subjects_dir, fs_subject, "bem", "brain.surf")

src = mne.setup_volume_source_space(
    fs_subject, pos=8, subjects_dir=subjects_dir, surface=surf_file)
mne.viz.plot_bem(src=src, **plot_bem_kwargs)

#%% single shell conduction model

conductivity = (0.3,)
model = mne.make_bem_model(
    subject=fs_subject, ico=4,
    conductivity=conductivity,
    subjects_dir=subjects_dir)
bem = mne.make_bem_solution(model)

bem_fname = deriv_path.basename + "-bem.fif"
mne.write_bem_solution(op.join(deriv_path.directory, bem_fname), 
                       bem, overwrite=True)

#%% forward solution
trans_fname = deriv_path.basename + "-trans.fif"
transfile = op.join(deriv_path.directory, trans_fname) #manual transfile
fwd = mne.make_forward_solution(
    data.info,
    trans=transfile, #coreg.trans,
    src=src,
    bem=bem,
    meg=True,
    eeg=False
    )
print(fwd)

fwd_fname = deriv_path.basename + "-fwd.fif"
mne.write_forward_solution(op.join(deriv_path.directory, fwd_fname), 
                       fwd, overwrite=True)

# %%
