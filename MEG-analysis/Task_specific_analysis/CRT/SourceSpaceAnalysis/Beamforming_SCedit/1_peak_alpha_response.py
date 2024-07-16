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

data = mne.io.Raw(op.join(deriv_path.directory, deriv_path.basename + "-raw.fif"))
src = op.join(deriv_path.directory, deriv_path.basename + "-src.fif")
fwd = op.join(deriv_path.directory, deriv_path.basename + "-fwd.fif")
sfreq = data.info["sfreq"]

#%% events

events = mne.find_events(data, stim_channel="STI101", min_duration=5/sfreq)   # for stim pres

#%% epoch based on trigger

event_id = [101] #[101, 102] #  # trigger of interest
tmin, tmax = -0.8, 1.2
epochs = mne.Epochs(
    data,
    events,
    event_id,
    tmin,
    tmax,
    baseline=(-0.4, -0.1),
    preload=True,
    reject=dict(mag=4e-12),
    reject_by_annotation=True)

#%% compute covariance of all data, unfiltered

cov = mne.compute_covariance(epochs)
cov.plot(epochs.info)
rank = mne.compute_rank(epochs, tol=1e-6, tol_kind='relative')

#%% make forward solution
fwd = op.join(deriv_path.directory, deriv_path.basename + "-fwd.fif")
fwd = mne.read_forward_solution(fwd)

#%% make working noise covariance

n_channels = cov.data.shape[0]
noise_cov_diag = np.zeros(n_channels)
for chantype in ["grad", "mag"]:
    # Indices of this channel type
    type_data = epochs.copy().pick(chantype, exclude="bads")
    inds = []
    for chan in type_data.info["ch_names"]:
        inds.append(cov.ch_names.index(chan))

    # Mean variance of channels of this type
    variance = np.mean(np.diag(cov.data)[inds])
    noise_cov_diag[inds] = variance

bads = [b for b in epochs.info["bads"] if b in cov.ch_names]
noise_cov = mne.Covariance(noise_cov_diag, cov.ch_names, bads, 
                           epochs.info["projs"], nfree=1e10)

#%% calculate beamformer weights

filters = mne.beamformer.make_lcmv(
    epochs.info,
    fwd,
    cov,
    reg=0.05,
    noise_cov=noise_cov,
    pick_ori="max-power",
    weight_norm="unit-noise-gain",
    rank=rank,#"info",
    reduce_rank=True,
    )

#%% get pseudo T

# filter epochs
fband = [13, 30]
epochs_filt = epochs.copy().filter(fband[0], fband[1])

# compute active and control covariance of filtered data        
act_min, act_max = 0.2, 0.6
con_min, con_max = 0.8, 1.1

active_cov = mne.compute_covariance(epochs_filt, tmin=act_min, tmax=act_max, method="shrunk", rank=rank)
control_cov = mne.compute_covariance(epochs_filt, tmin=con_min, tmax=con_max, method="shrunk", rank=rank)
control_cov.plot(epochs.info)
active_cov.plot(epochs.info)

# pseudo T
stc_active = mne.beamformer.apply_lcmv_cov(active_cov, filters)
stc_base = mne.beamformer.apply_lcmv_cov(control_cov, filters)
pseudoT = (stc_active - stc_base) / (stc_active + stc_base)
#pseudoT = mne.read_source_estimate(op.join(deriv_path.directory, 'pseudoTtheta-vl.stc'))
#pseudoT.save(op.join(deriv_path.directory,'pseudoTtheta'))

# for plotting
subjects_dir = r'C:\Users\waitta\Documents\ClusterDocs\BearTestSub\BIDS\task_BIDS\derivatives\freesurfer' #'R:\DRS-mTBI\Seb\mTBI_predict\FreeSurfer_SUBJECTS'
fs_subject = 'sub-2003_ses-06A' #"sub-2001_ses-04A" #"sub-2001"

pseudoT.plot_3d(src=fwd['src'], subject=fs_subject, subjects_dir=subjects_dir,
                background='white',
                views=["dorsal", "med", "lat"],
                view_layout="horizontal",
                alpha=0.2,
                size=[1000, 320],
                time_viewer=False,
                show_traces=False,
                colorbar=False,
                )

#%% extract absolute max voxel TFS/timecourse

stc_epochs = mne.beamformer.apply_lcmv_epochs(epochs, filters,
                                              return_generator=True)
 
peak = pseudoT.get_peak(mode="neg", vert_as_index=True)[0]

n_epochs = (len(epochs))
epoch_len = np.shape(epochs[0])[2]

epoch_peak_data = np.zeros((n_epochs,1,epoch_len))
for s,stc_epoch in enumerate(stc_epochs):
    epoch_peak_data[s,0,:] = stc_epoch.data[peak]

# make source epoch object
ch_names = ["peak"]
ch_types = ["misc"]
source_info = mne.create_info(ch_names=ch_names, sfreq=epochs.info["sfreq"],
                              ch_types=ch_types)
source_epochs = mne.EpochsArray(epoch_peak_data, source_info,
                                tmin=epochs.tmin)

# TFR
baseline = (-0.5, -0.2)
freqs = np.arange(1,30)
n_cycles = freqs/2
power = mne.time_frequency.tfr_morlet(source_epochs, freqs=freqs, n_cycles=n_cycles,
                                           use_fft=True, picks="all"
                                           )
power[0].plot(picks="all", baseline=baseline)

# timecourse
### trial averaged timecourse
source_epochs_filt = source_epochs.copy().filter(fband[0], fband[1], picks="all")
source_epochs_hilb = source_epochs_filt.copy().apply_hilbert(envelope=True, picks="all")
peak_timecourse = source_epochs_hilb.average(picks="all").apply_baseline(baseline)

# calculate MRBD (beta desync) or other during-stimulus response
stimulus_win = (0.2, 0.6)
stimulus_ind = np.logical_and(peak_timecourse.times > stimulus_win[0], 
                          peak_timecourse.times < stimulus_win[1])
stimulus_response = np.mean(peak_timecourse.get_data()[0][stimulus_ind])

# calculate PMBR (beta rebound) or other poststimulus response
poststim_win = (0.7, 1)
poststim_ind = np.logical_and(peak_timecourse.times > poststim_win[0], 
                          peak_timecourse.times < poststim_win[1])
poststim_response = np.mean(peak_timecourse.get_data()[0][poststim_ind])

from matplotlib import pyplot as plt
plt.figure()
plt.plot(peak_timecourse.times, peak_timecourse.get_data()[0], color="black")
plt.ylabel("Oscillatory Power (A.U)")
plt.xlabel("Time (s)")
plt.axhline(stimulus_response, alpha=0.5, color="blue")
plt.axhline(poststim_response, alpha=0.5, color="red")
plt.legend(["Data", "Stim Response", "Poststim Response"])


# %%
