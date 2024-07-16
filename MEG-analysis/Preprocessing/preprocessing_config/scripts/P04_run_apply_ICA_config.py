# -*- coding: utf-8 -*-
"""
===============================================
07. Run and apply ICA

This code will run ICA to find ocular and cardiac
artifacts and then input which components
to remove and removes them from the data: 
1. decomposition, 2. manual identification, 
3. project out

written by Tara Ghafari
adapted from flux pipeline
==============================================
"""

import os.path as op
import numpy as np

import mne
from mne.preprocessing import ICA
from mne_bids import BIDSPath

from config import Config

# Initialize the config
config = Config()

def get_bad_components_from_user():
    """
    Get the number of bad ICA components from the user to exclude from the data.

    Returns:
        list: List of bad ICA components.
    """
    
    numbers = []
    while True:
        user_input = input("Enter the number of bad ICA components one by one (or press 'd' to finish): ")
        if user_input.lower() == 'd':
            break
        try:
            number = int(user_input)  # Convert the input to an integer
            numbers.append(number)
        except ValueError:
            print("Invalid input. Please enter a valid number.")
    return numbers

def prepare_raw_data(input_fname):
    """
    Read, resample, and filter the raw data.

    Args:
        input_fname (str): Path to the input file.

    Returns:
        raw_resampled (mne.io.Raw): Resampled and filtered raw data.
    """
    raw_ann = mne.io.read_raw_fif(input_fname, allow_maxshield=True, verbose=True, preload=True)
    print("Preparing data for ICA (resample and filter)")
    raw_resampled = raw_ann.copy().pick(["meg", "eog", "ecg"]).resample(200).filter(1, 40)
    return raw_ann, raw_resampled

def apply_ica(raw_resampled):
    """
    Apply ICA and identify artifact components.

    Args:
        raw_resampled (mne.io.Raw): Resampled and filtered raw data.

    Returns:
        ica (mne.preprocessing.ICA): Fitted ICA object.
    """
    ica = ICA(method=config.ica.method, random_state=config.ica.random_state, n_components=config.ica.n_components, verbose=True)
    ica.fit(raw_resampled, verbose=True)
    ica.plot_sources(raw_resampled, title='ICA')
    ica.plot_components()
    return ica

def save_bad_components(bad_components):
    """
    Save the manually selected bad ICA components to the rejected dictionary.

    Args:
        bad_components (list): List of bad ICA components.
    """
    ICA_rej_dic = np.load(config.directories.ICA_rej_dict, allow_pickle=True).item()
    ICA_rej_dic[f'sub-{config.session_info.subject}_ses-{config.session_info.session}'] = bad_components
    np.save(config.directories.ICA_rej_dict, ICA_rej_dic)

def create_report(ica, raw_ica, artifact_ICs):
    """
    Create and save the report after applying ICA.

    Args:
        ica (mne.preprocessing.ICA): Fitted ICA object.
        raw_ica (mne.io.Raw): ICA cleaned raw data.
        artifact_ICs (list): List of artifact ICA components.
    """
    html_report_fname = op.join(config.directories.report_folder, f'report_{config.session_info.subject}_{config.session_info.session}_{config.session_info.task}_ICA.html')
    report_html = mne.Report(title=f'sub-{config.session_info.subject}_{config.session_info.task}')
    
    fig_ica = ica.plot_components(picks=artifact_ICs, title='removed components', show=False)
    report_html.add_figure(fig_ica, title="removed ICA components (eog, ecg)", tags=('ica'), image_format="PNG")
    report_html.add_raw(raw=raw_ica.filter(0, 60), title='raw after ICA', psd=True, butterfly=False, tags=('ica'))
    report_html.save(html_report_fname, overwrite=True, open_browser=True)
    
    full_report_input = input("Do you want to add this to the full report (y/n)? ")
    if full_report_input == 'y':
        report = mne.open_report(config.directories.report_fname)
        report.add_figure(fig_ica, title="removed ICA components (eog, ecg)", tags=('ica'), image_format="PNG")
        report.add_raw(raw=raw_ica.filter(0, 60), title='raw after ICA', psd=True, butterfly=False, tags=('ica'))
        report.save(config.directories.report_fname, overwrite=True)

def main():
    """
    Main function to run the ICA pipeline.
    """
    bids_path = BIDSPath(subject=config.session_info.subject, 
                         session=config.session_info.session, 
                         task=config.session_info.task, 
                         run=config.session_info.run, 
                         datatype=config.session_info.datatype,
                         suffix=config.session_info.meg_suffix, 
                         extension=config.session_info.extension,
                         root=config.directories.bids_root)
    
    bids_fname = bids_path.basename.replace(config.session_info.meg_suffix, 'ann')
    input_fname = op.join(config.directories.deriv_folder, bids_fname)
    deriv_fname = str(input_fname).replace('ann', 'ica')

    raw_ann, raw_resampled = prepare_raw_data(input_fname)
    ica = apply_ica(raw_resampled)
    
    bad_components = get_bad_components_from_user()
    print("You entered the following numbers:", bad_components)
    
    save_bad_components(bad_components)
    
    ICA_rej_dic = np.load(config.directories.ICA_rej_dict, allow_pickle=True).item()
    artifact_ICs = ICA_rej_dic[f'sub-{config.session_info.subject}_ses-{config.session_info.session}']
    
    if config.session_info.test_plot:
        for exc in np.arange(len(artifact_ICs)):
            ica.plot_overlay(raw_resampled, exclude=[artifact_ICs[exc]], picks='mag')
        ica.plot_overlay(raw_resampled, exclude=artifact_ICs, picks='mag')
        ica.plot_properties(raw_resampled, picks=artifact_ICs)
    
    ica.exclude = artifact_ICs
    raw_ica = raw_ann.copy()
    ica.apply(raw_ica)
    raw_ica.save(deriv_fname, overwrite=True)
    
    create_report(ica, raw_ica, artifact_ICs)

if __name__ == "__main__":
    main()
