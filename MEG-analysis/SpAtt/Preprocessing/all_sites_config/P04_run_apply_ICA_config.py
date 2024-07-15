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

from config import Config

# Initialize the config
config = Config()

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
input_suffix = 'ann'
deriv_suffix = 'ica'
test_plot = False  # set to True if you want to plot the data for testing

# Specify specific file names
bids_path = BIDSPath(subject=config.session_info.subject, 
                     session=config.session_info.session, 
                     task=config.session_info.task, 
                     run=config.session_info.run, 
                     datatype=config.session_info.datatype,
                     suffix=config.session_info.meg_suffix, 
                     extension=config.session_info.extension,
                     root=config.directories.bids_root)

bids_fname = bids_path.basename.replace(config.directories.meg_suffix, input_suffix)  # only used for suffices that are not recognizable to bids 
input_fname = op.join(config.directories.deriv_folder, bids_fname)
deriv_fname = str(input_fname).replace(input_suffix, deriv_suffix)

# read annotated data + resample and filtering
"""
we down sample the data in order to make ICA run faster, 
highpass filter at 1Hz to remove slow drifts and lowpass 40Hz
because that's what we need
"""
raw_ann = mne.io.read_raw_fif(input_fname, 
                              allow_maxshield=True,
                              verbose=True,
                              preload=True)

print("Preparing data for ICA (resample and filter)")
raw_resmpld = raw_ann.copy().pick(["meg", "eog", "ecg"]).resample(200).filter(1, 40)

# Apply ICA and identify artifact components
ica = ICA(method=config.ica.method, 
          random_state=config.ica.random_state, 
          n_components=config.ica.n_components, 
          verbose=True)
ica.fit(raw_resmpld, 
        verbose=True)
ica.plot_sources(raw_resmpld, 
                 title='ICA')
ica.plot_components()

bad_components = get_bad_components_from_user()
print("You entered the following numbers:", bad_components)

# Load the dictionary containing rejected ICs of previous subjects
ICA_rej_dic = np.load(config.directories.ICA_rej_dict, allow_pickle=True).item()
ICA_rej_dic[f'sub-{config.session_info.subject}_ses-{config.session_info.session}'] = bad_components # save manually selected bad ICs to rejected dictionary
np.save(config.directories.ICA_rej_dict, ICA_rej_dic)

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
artifact_ICs = ICA_rej_dic[f'sub-{config.session_info.subject}_ses-{config.session_info.session}']

if test_plot:
    # Double check the manually selected artifactual ICs
    """ Plot original data against reconstructed 
    signal excluding artifact ICs + IC properties"""

    for exc in np.arange(len(artifact_ICs)):
        ica.plot_overlay(raw_resmpld, exclude=[artifact_ICs[exc]], picks='mag')  
    
    ica.plot_overlay(raw_resmpld, exclude=artifact_ICs, picks='mag') 
    ica.plot_properties(raw_resmpld, picks=artifact_ICs)

# Exclude ICA components
ica.exclude = artifact_ICs
raw_ica = raw_ann.copy()
ica.apply(raw_ica)

# Save the ICA cleaned data
raw_ica.save(deriv_fname, 
             overwrite=True)


# Filter data for the report
print("Reporting output of P04_run_apply_ICA_config")
html_report_fname = op.join(config.session_info.report_folder, 
                            f'report_{config.session_info.subject}_{config.session_info.session}_{config.session_info.task}_ICA.html')
report_html = mne.Report(title=f'sub-{config.session_info.subject}_{config.session_info.task}')

# only add excluded components to the report
fig_ica = ica.plot_components(picks=artifact_ICs, title='removed components', show=False)
    
report_html.add_figure(fig_ica, 
                  title="removed ICA components (eog, ecg)",
                    tags=('ica'), 
                    image_format="PNG")
report_html.add_raw(raw=raw_ica.filter(0, 60), 
               title='raw after ICA', 
                psd=True, 
                butterfly=False, 
                tags=('ica'))

report_html.save(html_report_fname, 
            overwrite=True, 
            open_browser=True)  

full_report_input = input("Do you want to add this to the full report (y/n)? ")
if full_report_input == 'y':
    report = mne.open_report(config.directories.report_fname)

    report.add_figure(fig_ica, title="removed ICA components (eog, ecg)",
                        tags=('ica'), image_format="PNG")
    report.add_raw(raw=raw_ica.filter(0, 60), title='raw after ICA', 
                    psd=True, butterfly=False, tags=('ica'))


    report.save(config.directories.report_fname, overwrite=True)
