# -*- coding: utf-8 -*-
"""
===============================================
07. Run and apply ICA

This code will run ICA to find occular and cardiac
artifacts and then input which components
to remove and removes them from the data : 
1. decomposition, 2. manual identification, 
3. project out

written by Tara Ghafari
adapted from flux pipeline
==============================================
ToDos:
    1) 
    2) 
    
Issues:
    1) read_raw_bids doesn't read annotated
    data
    
Questions:
    1) 

"""

import os.path as op
import os
import numpy as np

import mne
from mne.preprocessing import ICA
from mne_bids import BIDSPath


def get_bad_components_from_user():
    """this function will get the number of bad ICA components
    from the user to exclude from the data."""
    numbers = []
    while True:
        user_input = input("Enter the number of bad ICA components one by one (or press 'd' to finish): ")
        if user_input.lower() == 'd':
            break
        try:
            number = int(user_input)  # Convert the input to a integer
            numbers.append(number)
        except ValueError:
            print("Invalid input. Please enter a valid number.")
    return numbers


# fill these out
meg_extension = '.fif'
meg_suffix = 'meg'
input_suffix = 'ann'
deriv_suffix = 'ica'

summary_rprt = True  # do you want to add evokeds figures to the summary report?
test_plot = False  # do you want to plot the data to test (True) or just generate report (False)?



# Specify specific file names
bids_path = BIDSPath(subject=subject, session=session,
                     task=task, run=run, root=bids_root, 
                     suffix=meg_suffix, extension=meg_extension)
bids_fname = bids_path.basename.replace(meg_suffix, input_suffix)  # only used for suffices that are not recognizable to bids 
input_fname = op.join(deriv_folder, bids_fname)
deriv_fname = str(input_fname).replace(input_suffix, deriv_suffix)

# read annotated data + resample and filtering
"""
we down sample the data in order to make ICA run faster, 
highpass filter at 1Hz to remove slow drifts and lowpass 40Hz
because that's what we need
"""
raw_ann = mne.io.read_raw_fif(input_fname, allow_maxshield=True,
                              verbose=True, preload=True)
raw_resmpld = raw_ann.copy().pick(["meg", "eog", "ecg"])
raw_resmpld.resample(200)
raw_resmpld.filter(1, 40)

# Apply ICA and identify artifact components
ica = ICA(method='fastica', random_state=97, n_components=30, verbose=True)
ica.fit(raw_resmpld, verbose=True)
ica.plot_sources(raw_resmpld, title='ICA')
ica.plot_components()

bad_components = get_bad_components_from_user()
print("You entered the following numbers:", bad_components)

ICA_rej_dic = {f'sub-{subject}_ses-{session}':bad_components} # manually selected bad ICs or from sub config file 
"""200102B: [3, 13]
200204B: [1, 11]
200302B: [7, 9]
200401B: [1]
200403B: [0, 1, 2, 3]
200404B: [0]
200504B: [0, 2]
200605B: [1, 5]
200705B: [0, 9]
200802B: [0, 1]
201005B: [1, 2]"""
artifact_ICs = ICA_rej_dic[f'sub-{subject}_ses-{session}']

if test_plot:
    # Double check the manually selected artifactual ICs
    """ Plot original data against reconstructed 
    signal excluding artifact ICs + Ic properties"""

    for exc in np.arange(len(artifact_ICs)):
        ica.plot_overlay(raw_resmpld, exclude=[artifact_ICs[exc]], picks='mag')  
    
    ica.plot_overlay(raw_resmpld, exclude=artifact_ICs, picks='mag')  # all
    ica.plot_properties(raw_resmpld, picks=artifact_ICs)

# Exclude ICA components
ica.exclude = artifact_ICs
raw_ica = raw_ann.copy()
ica.apply(raw_ica)

# Save the ICA cleaned data
raw_ica.save(deriv_fname, overwrite=True)

if test_plot:
    # plot a few frontal channels before and after ICA
    chs = ['MEG0311', 'MEG0121', 'MEG1211', 'MEG1411', 'MEG0342', 'MEG1432']
    ch_idx = [raw_ann.ch_names.index(ch) for ch in chs]
    raw_ann.plot(order=ch_idx, duration=5, title='before')
    raw_ica.plot(order=ch_idx, duration=5, title='after')

# only add excluded components to the report
fig_ica = ica.plot_components(picks=artifact_ICs, title='removed components', show=False)

# Filter data for the report
if summary_rprt:
    report_root = op.join(mTBI_root, 'results-outputs/mne-reports')  # RDS folder for reports
   
    if not op.exists(op.join(report_root , 'sub-' + subject, 'ses-' + session, 'task-' + task)):
        os.makedirs(op.join(report_root , 'sub-' + subject, 'ses-' + session, 'task-' + task))
    report_folder = op.join(report_root , 'sub-' + subject, 'ses-' + session, 'task-' + task)

    report_fname = op.join(report_folder, 
                        f'mneReport_sub-{subject}_{session}_{task}_1.hdf5')    # it is in .hdf5 for later adding images
    html_report_fname = op.join(report_folder, f'report_preproc_{session}_{task}_1.html')
    
    report = mne.open_report(report_fname)
    report.add_figure(fig_ica, title="removed ICA components (eog, ecg)",
                      tags=('ica'), image_format="PNG")
    report.add_raw(raw=raw_ica.filter(0, 60), title='raw after ICA', 
                   psd=True, butterfly=False, tags=('ica'))
    report.save(report_fname, overwrite=True)
    report.save(html_report_fname, overwrite=True, open_browser=True)  # to check how the report looks




