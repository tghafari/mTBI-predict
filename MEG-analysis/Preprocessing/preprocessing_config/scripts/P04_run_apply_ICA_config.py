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

import sys
import os.path as op
import argparse

import numpy as np

import mne
from mne.preprocessing import ICA
from mne_bids import BIDSPath

# Add the project root directory to the sys.path
project_root = op.abspath(op.join(op.dirname(__file__), '..'))
config_root = op.join(project_root, 'config')
sys.path.append(config_root)

from config import Config

def prepare_raw_data(input_fpath):
    """
    Read, resample, and filter the raw data.

    Args:
        input_fpath (str): Path to the annotated fif file.

    Returns:
        raw_resampled (mne.io.Raw): Resampled and filtered raw data.
    """
    raw_ann = mne.io.read_raw_fif(input_fpath, allow_maxshield=True, verbose=True, preload=True)
    print("Preparing data for ICA (resample and filter)")
    raw_resampled = raw_ann.copy().pick(["meg", "eog", "ecg"]).resample(200).filter(1, 40)
    return raw_ann, raw_resampled

def apply_ica(raw_resampled, method, random_state, n_components):
    """
    Apply ICA and identify artifact components.

    Args:
        raw_resampled (mne.io.Raw): Resampled and filtered raw data.

    Returns:
        ica (mne.preprocessing.ICA): Fitted ICA object.
    """
    ica = ICA(method=method, random_state=random_state, n_components=n_components, verbose=True)
    ica.fit(raw_resampled, verbose=True)
    ica.plot_sources(raw_resampled, title='ICA')
    ica.plot_components()
    return ica

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

def save_bad_components(bad_components, ICA_rej_dict_dir, subject, session):
    """
    Save the manually selected bad ICA components to the rejected dictionary.

    Args:
        bad_components (list): List of bad ICA components.
    """
    ICA_rej_dic = np.load(ICA_rej_dict_dir, allow_pickle=True).item()
    ICA_rej_dic[f'sub-{subject}_ses-{session}'] = bad_components
    np.save(ICA_rej_dict_dir, ICA_rej_dic)

def create_report(subject, session, task, report_folder, report_fname, ica, raw_ica, artifact_ICs):
    """
    Create and save the report after applying ICA.

    Args:
        ica (mne.preprocessing.ICA): Fitted ICA object.
        raw_ica (mne.io.Raw): ICA cleaned raw data.
        artifact_ICs (list): List of artifact ICA components.
    """

    html_report_fname = op.join(report_folder, f'report_{subject}_{session}_{task}_ica.html')
    report_html = mne.Report(title=f'Sub-{subject}_{task}')

    fig_ica = ica.plot_components(picks=artifact_ICs, title='removed components', show=False)
    report_html.add_figure(fig_ica, title="removed ICA components (eog, ecg)", tags=('ica'), image_format="PNG")
    report_html.add_raw(raw=raw_ica.filter(0, 60), title='raw after ICA', psd=True, butterfly=False, tags=('ica'))
    report_html.save(html_report_fname, overwrite=True, open_browser=True)
    
    full_report_input = input("Do you want to add this to the full report (y/n)? ")
    if full_report_input == 'y':
        report = mne.open_report(report_fname)
        report.add_figure(fig_ica, title="removed ICA components (eog, ecg)", tags=('ica'), image_format="PNG")
        report.add_raw(raw=raw_ica.filter(0, 60), title='raw after ICA', psd=True, butterfly=False, tags=('ica'))
        report.save(report_fname, overwrite=True)

def main(subject, session):
    # Initialize the config
    config = Config(site='Birmingham', subject=subject, session=session, task='SpAtt')

    # Fill these out
    input_suffix = 'ann'
    deriv_suffix = 'ica'

    input_fpath, deriv_fpath = config.get_bids_paths(input_suffix, deriv_suffix)

    # bids_path = BIDSPath(subject=config.session_info.subject, 
    #                      session=config.session_info.session, 
    #                      task=config.session_info.task, 
    #                      run=config.session_info.run, 
    #                      datatype=config.session_info.datatype,
    #                      suffix=config.session_info.meg_suffix, 
    #                      extension=config.session_info.extension,
    #                      root=config.directories.bids_root)
    
    # bids_fname = bids_path.basename.replace(config.session_info.meg_suffix, input_suffix)  
    # input_fpath = op.join(config.directories.deriv_folder, bids_fname)
    # deriv_fpath = input_fpath.replace(input_suffix, deriv_suffix)

    raw_ann, raw_resampled = prepare_raw_data(input_fpath)
    ica = apply_ica(raw_resampled, config.ica_params.ica_method, 
                    config.ica_params.random_state, config.ica_params.n_components)
    
    bad_components = get_bad_components_from_user()
    print("You entered the following numbers:", bad_components)
    
    save_bad_components(bad_components, 
                        config.directories.ICA_rej_dict_dir, 
                        config.session_info.subject,
                        config.session_info.session)
    
    ICA_rej_dic = np.load(config.directories.ICA_rej_dict_dir, allow_pickle=True).item()
    artifact_ICs = ICA_rej_dic[f'sub-{config.session_info.subject}_ses-{config.session_info.session}']
    
    if config.session_info.test_plot:
        for exc in np.arange(len(artifact_ICs)):
            ica.plot_overlay(raw_resampled, exclude=[artifact_ICs[exc]], picks='mag')
        ica.plot_overlay(raw_resampled, exclude=artifact_ICs, picks='mag')
        ica.plot_properties(raw_resampled, picks=artifact_ICs)
    
    ica.exclude = artifact_ICs
    raw_ica = raw_ann.copy()
    ica.apply(raw_ica)
    raw_ica.save(deriv_fpath, overwrite=True)
    
    create_report(ica, raw_ica, artifact_ICs)
    create_report(config.session_info.subject, config.session_info.session,
                  config.session_info.task, config.directories.report_folder,
                  config.directories.report_fname, ica, raw_ica, artifact_ICs)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Running ICA")
    parser.add_argument('--subject', type=str, required=True, help='Subject ID')
    parser.add_argument('--session', type=str, required=True, help='Session ID')
    
    args = parser.parse_args()
    main(args.subject, args.session)