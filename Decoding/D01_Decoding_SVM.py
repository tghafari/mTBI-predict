# -*- coding: utf-8 -*-
"""
===============================================
C01. Classification using support vector machine

This code will classify two classes of trials 
using SVM with Multi-variate pattern analysis 
(MVPA) method.

written by Tara Ghafari
adapted from flux pipeline
==============================================
ToDos:
    1) 
    
Issues/ contributions to community:
    1) 
    
Questions:
    1)

"""

import os.path as op
import matplotlib.pyplot as plt

import mne
from mne.decoding import (SlidingEstimator, cross_val_multiscore, 
                          Vectorizer, LinearModel)
from mne_bids import BIDSPath
import sklearn.svm
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

# subject info 
site = 'Birmingham'
subject = '04'  # subject code in mTBI project
session = '01'  # data collection session within each run
run = '01'  # data collection run for each participant
pilot = 'P' # is the data collected 'P'ilot or 'T'ask?
task = 'SpAtt'
meg_extension = '.fif'
meg_suffix = 'meg'
input_suffix = 'epo'
deriv_suffix = 'svm'

rprt = False

# Specify specific file names
bids_root = r'Z:\MEG_data\MNE-bids-data' #'-anonymized'  # RDS folder for bids formatted data
bids_path = BIDSPath(subject=subject, session=session,
                     task=task, run=run, root=bids_root, 
                     suffix=meg_suffix, extension=meg_extension)
deriv_folder = op.join(bids_root, 'derivatives', 'flux-pipeline' ,
                       'sub-' + subject, 'task-' + task)  # RDS folder for results
bids_fname = bids_path.basename.replace(meg_suffix, input_suffix)  # only used for suffices that are not recognizable to bids 
input_fname = op.join(deriv_folder, bids_fname)
deriv_fname = str(input_fname).replace(input_suffix, deriv_suffix)

# Read epoched data 
"""lowpass at 10Hz before segmenting to reduce edge effects from filtering"""
epochs = mne.read_epochs(input_fname, verbose=True, preload=True).pick(['meg'])
epochs_rs = epochs['cue onset right','cue onset left']  # only select relevant epochs
epochs_rs.filter(0,10).resample(100).crop(tmin=-.1, tmax=.5) 

# Set up the classifier
"""make a scikit-learn applicable matrix"""
X = epochs_rs.get_data()  # X(features) is a 3D matrix of trials*channels*time points
print(X.shape)

"""convert the event values to 1 and 2"""
y = epochs_rs.events[:,2]  # will be used in decoding
y[y==101] = 1
y[y==102] = 2


# Decoding and classifiation
""" 1st) what transforms estimator uses? X -> vectorize to 2D -> standardize
    2nd) define the estimator: discriminate the experimental conditions
    as functions of time
    3rd) classify timepoint by timepoint using SVM => 5-fold cross-validatation
    """
    
clf = make_pipeline(Vectorizer(), StandardScaler(), 
                    LinearModel(sklearn.svm.SVC(kernel = 'linear')))
time_decode = SlidingEstimator(clf, scoring='roc_auc',
                               n_jobs=-1, verbose=True)
scores = cross_val_multiscore(time_decode, X, y, cv=5, n_jobs=-1).mean(axis=0)

# Plotting
fig_html, ax = plt.subplots()
ax.plot(epochs_rs.times, scores, label='score')
ax.axhline(.5, color='k', linestyle='--', label='chance')
ax.axvline(.0, color='k', linestyle='-')
ax.set_xlabel('Time')
ax.set_ylabel('AUC')
ax.set_title('Sensor space decoding')
ax.legend()
plt.ylim([.35, .65])

# save in the report
if rprt:
   report_root = r'Z:\Projects\mTBI predict\Results - Outputs\mne-Reports'  # RDS folder for results
   report_folder = op.join(report_root , 'sub-' + subject, 'task-' + task)
   report_fname = op.join(report_folder,
                          f'mneReport_sub-{subject}.html')
   
   report = mne.open_report(report_fname)
   report.add_figure(fig=fig_html, title='Decoding',
                     caption='Sensor space decoding', 
                     tags=('decoding'),
                      section='decoding'  # only in ver 1.1
                     )
   report.save(report_fname, overwrite=True, open_browser=True)






