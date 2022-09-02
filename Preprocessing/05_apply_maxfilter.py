# -*- coding: utf-8 -*-
"""
===============================================
05. Applying MaxFilter

this code uses MaxFilter to reduce artifacts from
environmental sources and sensor noise

written by Tara Ghafari
adapted from flux pipeline
==============================================
ToDos:
    
Questions:
    1) why do we copy raw file?
    2) where is the copy() stored in variables?
    3) how come there are more gradio and magneto sensors after filtering?
"""

import os
import os.path as op
import matplotlib.pyplot as plt

import mne
from mne_bids import BIDSPath, read_raw_bids

# fill these out
site = 'Birmingham'
subject = '1'  # subject code in mTBI project
session = '01'  # data collection session within each run
run = '01'  # data collection run for each participant
pilot = 'P' # is the data collected 'P'ilot or 'T'ask?
task = 'SpAtt'


# specify specific file names
bids_root = r'Z:\MEG_data\MNE-bids-data-anonymized'  # RDS folder for bids formatted data
deriv_root = op.join(bids_root, 'derivatives', 'flux-pipeline' )  # RDS folder for results
if not op.exists(op.join(deriv_root , 'sub-' + subject, 'task-' + task)):
    deriv_folder = os.mkdir(op.join(deriv_root , 'sub-' + subject, 'task-' + task))
else:
    deriv_folder = op.join(deriv_root , 'sub-' + subject, 'task-' + task)
    
bids_path = BIDSPath(subject=subject, session=session,
                     task=task, run=run, root=bids_root)
bids_fname = op.join('sub-' + subject + '_ses-' + session + '_task-' + task + 
                     '_run-' + run)  # type of data should be added to the end of this name

# Define the fine calibration and cross-talk compensation files 
crosstalk_file = op.join(bids_root, 'sub-' + subject, 'ses-' + session, 'meg',
                         'sub-' + subject +'_ses-' + session + 
                         '_acq-crosstalk_meg.fif')  #'reduces interference' 
                                                    #'between Elekta's co-located' 
                                                    #'magnetometer and'
                                                    #'paired gradiometer sensor units'
calibration_file = op.join(bids_root, 'sub-' + subject, 'ses-' + session, 'meg',
                           'sub-' + subject + '_ses-' + session +
                           '_acq-calibration_meg.dat')  #'encodes site-specific'
                                                        #'information about sensor' 
                                                        #'orientations and calibration'
 

# read and raw data
raw = read_raw_bids(bids_path=bids_path, extra_params={'preload':True},
                    verbose=True)  #'fif files will be read with'
                                   #'allow_maxshield=True by default'   

# Identify and show faulty sensors using max filtering
auto_noisy_chs, auto_flat_chs, auto_scores = mne.preprocessing.find_bad_channels_maxwell(
    raw.copy(), cross_talk=crosstalk_file, calibration=calibration_file,
    return_scores=True, verbose=True)

print('noisy = ', auto_noisy_chs)
print('flat = ', auto_flat_chs)
len(auto_noisy_chs) + len(auto_flat_chs)

# set noisy and flat channels as 'bads' in the data set
raw.info['bads'] = []
raw.info['bads'].extend(auto_noisy_chs + auto_flat_chs)
print('bads = ', raw.info['bads'])
len(raw.info['bads'])

# we might need to change MEGIN magnetometer coil types (type 3022 and 3023 to 3024) 
# to ensure compatibility across systems
raw.fix_mag_coil_types()

# Apply the Maxfilter with fine calibration and cross-talk reduction
raw_sss = mne.preprocessing.maxwell_filter(raw,
                                           cross_talk=crosstalk_file,
                                           calibration=calibration_file,
                                           verbose=True)

# Plot power spectra of raw data and after maxwell filterting for comparison
fig, ax = plt.subplots(2,2)

fig = raw.plot_psd(ax=ax[:,0], fmax=60, n_fft=1000, show=False)
fig = raw_sss.plot_psd(ax=ax[:,1], fmax=60, n_fft=1000, show=False)

ax[1,0].set_xlabel(' \nPSD before filtering')
ax[1,1].set_xlabel(' \nPSD after filtering')
fig.set_tight_layout(True)
plt.show()

# Save the maxfiltered file
raw_sss.save(op.join(deriv_folder, bids_fname + '-sss.fif'), overwrite=True)















































