"""
===============================================
P99. Run Preprocessing 1

This code will run preprocessing based on
site until ica.
Before each step it will ask if the user want to
see the output and in the end asks for the
bad IC components.

P99 Run Preprocessing 2 will apply ica and 
do the epoching based on the task.

written by Tara Ghafari
adapted from oscfer88 [https://github.com/Cogitate-consortium/MEEG/tree/master/MNE-python_pipeline_v3]
==============================================
"""


import P01_look_at_data
import P02_maxwell_filtering
import P03_artifact_annotation
import P04_run_ica

from config import subject_list

subject_id = subject_list[0]

P01_maxwell_filtering_bids.run_maxwell_filter(subject_id)
P02_find_bad_eeg_bids.find_bad_eeg(subject_id)
P03_artifact_annotation_bids.artifact_annotation(subject_id)
P04_extract_events_bids.run_events(subject_id)
P05_run_ica_bids.run_ica(subject_id)
