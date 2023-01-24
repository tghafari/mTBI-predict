# -*- coding: utf-8 -*-
"""
===============================================
B01. Time frequency representation of power (low freq)

This code will calculate TFR of powe for each 
trial and then averages over trials to characterize 
the modulation of oscillatory activity < 30Hz. 
Also, modulation index is calculated.

written by Tara Ghafari
adapted from flux pipeline
==============================================
ToDos:
    1) use anonymized data (sub =1)
    2) create a new script for modulation and
    lateralization indices
    3) cue right and left are mixed for sub-P03
    4) consider right>left and left>right for epochs
    and plot alpha desynchronisation accordingly
    
Issues/ contributions to community:
    1) mne.read_epochs with preload=True raises 
    an [Erno 22] invalid argument, error
    2) plot_topo should include a parameter 'ax'
    3) show=False does not work in plot_topo
    
Questions:
    1) alpha is low on both occipital cortices
    in attention left?

"""

import os.path as op
import numpy as np
import matplotlib.pyplot as plt

import mne
from mne_bids import BIDSPath

site = 'Birmingham'
subject = '04'  # subject code in mTBI project
session = '01'  # data collection session within each run
run = '01'  # data collection run for each participant
pilot = 'P' # is the data collected 'P'ilot or 'T'ask?
task = 'SpAtt'
meg_extension = '.fif'
meg_suffix = 'meg'
input_suffix = 'epo'
deriv_suffix = 'tfr'

rprt = False

# Specify specific file names
bids_root = r'Z:\Projects\mTBI_predict\Collected_Data\MNE-bids-data' #'-anonymized'  # RDS folder for bids formatted data
bids_path = BIDSPath(subject=subject, session=session,
                     task=task, run=run, root=bids_root, 
                     suffix=meg_suffix, extension=meg_extension)
deriv_folder = op.join(bids_root, 'derivatives', 'flux-pipeline' ,
                       'sub-' + subject, 'task-' + task)  # RDS folder for results
bids_fname = bids_path.basename.replace(meg_suffix, input_suffix)  # only used for suffices that are not recognizable to bids 
input_fname = op.join(deriv_folder, bids_fname)
deriv_fname = str(input_fname).replace(input_suffix, deriv_suffix)

# Read epoched data
epochs = mne.read_epochs(input_fname, verbose=True, preload=True)

# Set the parameters for slow freq analysis and run for attention left and right 
freqs = np.arange(2,31,1)  # the frequency range over which we perform the analysis
n_cycles = freqs / 2  # the length of sliding window in cycle units. 
time_bandwidth = 2.0  # '(2deltaTdeltaF) number of DPSS tapers to be used + 1.'
                      # 'it relates to the temporal (deltaT) and spectral (deltaF)' 
                      # 'smoothing'
                      # 'the more tapers, the more smooth'->useful for high freq data
picks='grad'  # all plots from tfrs will be on picks

tfr_slow_left = mne.time_frequency.tfr_multitaper(epochs['cue onset right'],  # left and right switched only for Ruwan
                                                  freqs=freqs, n_cycles=n_cycles,
                                                  time_bandwidth=time_bandwidth,
                                                  picks=picks,
                                                  use_fft=True, return_itc=False,
                                                  average=True, decim=2,
                                                  n_jobs=4, verbose=True)  # 'jobs allows for parallel execution for' 
                                                                           # 'multicore CPUs'
                                                
tfr_slow_right = mne.time_frequency.tfr_multitaper(epochs['cue onset left'],  # left and right switched only for Ruwan
                                                   freqs=freqs, n_cycles=n_cycles,
                                                   time_bandwidth=time_bandwidth,
                                                   picks=picks,
                                                   use_fft=True, return_itc=False,
                                                   average=True, decim=2,
                                                   n_jobs=4, verbose=True)
# Plot TFR on all sensors 
""" pick which sensors to show later""" 
tfr_slow_left.plot_topo(tmin=-.5, tmax=1.0, 
                        baseline=[-.5,-.3], mode='percent',
                        fig_facecolor='w', font_color='k',
                        vmin=-1, vmax=1, 
                        title='TFR of power < 30Hz-left')
tfr_slow_right.plot_topo(tmin=-.5, tmax=1.0,
                         baseline=[-.5,-.3], mode='percent',
                         fig_facecolor='w', font_color='k',
                         vmin=-1, vmax=1, 
                         title='TFR of power < 30Hz-right')

# Plot TFR for representative sensors
fig_tfr, axis = plt.subplots(2, 2, figsize = (7, 7))
sensors = ['MEG1733','MEG1943','MEG2513','MEG2133']
#'MEG2333','MEG2342'
for sensor in sensors:
    if sensors.index(sensor) < len(sensors)/2:
        tfr_slow_right.plot(picks=sensor, baseline=[-.5,-.2],
                            mode='percent', tmin=-.5, tmax=1.0,
                            vmin=-.75, vmax=.75, 
                            axes=axis[sensors.index(sensor),0], show=False)
    else:   
        tfr_slow_left.plot(picks=sensor, baseline=[-.5,-.2],
                           mode='percent', tmin=-.5, tmax=1.0,
                           vmin=-.75, vmax=.75,
                           axes=axis[sensors.index(sensor)-2,1], show=False)
        
axis[0,0].set_title(' \nattention right-left sensors')
axis[0,1].set_title(' \nattention left-right sensors')

fig_tfr.set_tight_layout(True)
plt.show()      
                      
# Plot alpha topographically
""" fill tmin and tmax using the representative sensors"""

fig, axis = plt.subplots(1, 2, figsize=(7, 4))
tfr_slow_left.plot_topomap(tmin=.35, tmax=.75, fmin=8, fmax=12,
                           vmin=-.5, vmax=.5,
                           baseline=(-.5, -.3), mode='percent', axes=axis[0],
                           title='Left', show=False)
tfr_slow_right.plot_topomap(tmin=.35, tmax=.75, fmin=8, fmax=12,
                            vmin=-.5, vmax=.5,
                            baseline=(-.5, -.3), mode='percent', axes=axis[1],
                            title='Right', show=False)
fig.set_tight_layout(True)
plt.show()

# Compare power modulation for attention right and left (always R- L)
tfr_slow_modulation_power= tfr_slow_left.copy()
tfr_slow_modulation_power.data = (tfr_slow_right.data - tfr_slow_left.data) / (tfr_slow_right.data + tfr_slow_left.data)

tfr_slow_modulation_power.plot_topo(tmin=-.5, tmax=1.0, vmin=-.6, vmax=.6, 
                                    fig_facecolor='w', font_color='k',
                                    title='attention right - attention left')

# Plot ami on topoplot
fig_hlm = tfr_slow_modulation_power.plot_topomap(tmin=.35, tmax=.75, fmin=9, fmax=14, 
                                                 vmin=-.1, vmax=.1,                                           
                                                 title='alpha modulation index')
if rprt:
   report_root = r'Z:\Projects\mTBI predict\Results - Outputs\mne-Reports'  # RDS folder for results
   report_folder = op.join(report_root , 'sub-' + subject, 'task-' + task)
   report_fname = op.join(report_folder,
                          f'mneReport_sub-{subject}.hdf5')
   
   report = mne.open_report(report_fname)
   report.add_figure(fig=fig_tfr, title='TFR on ROI',
                     caption='Time Frequency Representation on \
                     right and left sensors', 
                     tags=('tfr'),
                      section='TFR'  # only in ver 1.1
                     )
   report.add_figure(fig=fig_hlm, title='alpha modulation index',
                     caption='Alpha modulation index (att right - att left)', 
                     tags=('AMI'),
                      section='TFR'
                     )

   report.save(report_fname, overwrite=True, open_browser=True)