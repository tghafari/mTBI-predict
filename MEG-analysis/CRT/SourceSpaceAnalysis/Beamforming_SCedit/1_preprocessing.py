# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 15:04:33 2024

@author: ppysc6

edited by Alice Waitt for Aston

"""
#%%
import os.path as op
import numpy as np
import mne
from mne_bids import BIDSPath, read_raw_bids
from mne.preprocessing import find_bad_channels_maxwell
import matplotlib.pyplot as plt


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

#data = mne.io.Raw(op.join(deriv_path.directory, deriv_path.basename + ".fif"))
data = mne.io.Raw(op.join(bids_path.directory, suffix, bids_path.basename + ".fif"))

#%% filter

data.load_data().filter(l_freq=1, h_freq=45)

#%% load in files for maxfilter

#cal_file = op.join(deriv_path.directory, 
#                        deriv_path.basename + "-cal.dat")
#crosstalk_file = op.join(deriv_path.directory, 
#                        deriv_path.basename + "-cross.fif")

#cal_file = op.join(bids_path.directory, suffix,
#                        bids_path.basename + "-cal.dat")
#crosstalk_file = op.join(bids_path.directory, suffix,
#                       bids_path.basename + "-cross.fif")

crosstalk_file = op.join(bids_path.directory, suffix, 'sub-' + subject +'_ses-' + session + 
                         '_acq-crosstalk_meg.fif') 
cal_file = op.join(bids_path.directory, suffix, 'sub-' + subject +'_ses-' + session + 
                           '_acq-calibration_meg.dat')  

#%% noisy channels

data.plot()

#%% SSS

data_sss = mne.preprocessing.maxwell_filter(
    data, cross_talk=crosstalk_file, calibration=cal_file, verbose=True
)

#%% mark SQUID resets  #does this even happen in megin data? don't think needed.

squid_annot, bad_chan = mne.preprocessing.annotate_amplitude(
                                    data_sss, 
                                    peak=dict(mag=10e-12, grad=10000e-13), 
                                    picks='meg',
                                    bad_percent=5, 
                                    min_duration=0.005)
squid_annot.onset = squid_annot.onset - 2  # remove 2 s before 
squid_annot.duration = [4] * len(squid_annot.duration)  # stretch out annotation
#data.info["bads"].extend(bad_chan)

#%% annotate smaller muscle artefacts etc (DONT USE ZSCORE HERE)

muscle_annot, bad_chan = mne.preprocessing.annotate_amplitude(
                                    data_sss, peak=dict(mag=4e-12, grad=10000e-10), 
                                    picks='meg',
                                    bad_percent=5, 
                                    min_duration=1/1000)
muscle_annot.onset = muscle_annot.onset - 0.2
muscle_annot.duration = muscle_annot.duration + 0.4

#%% add up annotations

data.set_annotations(squid_annot + muscle_annot)
data.plot()

#%% plot psd

data.plot_psd(fmax=45).show()

#%% ICA (LEFT CLICK ON CARDIAC AND BLINKING TIMECOURSES)

#ica = mne.preprocessing.ICA(n_components=20)
#ica.fit(data, reject_by_annotation=True)
#ica.plot_components()
#ica.plot_sources(data)

#%% remove bad components (THE ONES YOU CLICKED ON IN PREVIOUS PLOT)

#ica.apply(data)

#%% save

preproc_fname = deriv_path.basename + "-raw.fif"
data_sss.save(op.join(deriv_path.directory, preproc_fname), overwrite=True)
# %%
