# -*- coding: utf-8 -*-
"""
===========
Config file
===========

Configurate the parameters of the mTBI-predict study.

"""


import os
import os.path as op
import pandas as pd




class Config:
    """
    Configuration class for setting up directory paths and other parameters 
    for preprocessing MEG data.

    Attributes:
        site (str): Site name, e.g., 'Birmingham'.
        subject (str): Subject code, e.g., '2013'.
        session (str): Data collection session, e.g., '02B'.
        run (str): Data collection run, default is '01'.
        task (str): Task name, e.g., 'SpAtt'.
        datatype (str): Data type, default is 'meg'.
        meg_suffix (str): Suffix for file names, default is 'meg'.
        extension (str): File extension, default is '.fif'.
        platform (str): Platform type, e.g., 'mac', 'windows', or 'bluebear'.
    """

    def __init__(self, site=None, subject=None, session=None, run='01', task=None, datatype='meg', meg_suffix='meg', extension='.fif', platform='mac',
                 method='sss', threshold_muscle=None, min_length_good=.2, filter_freq=[110,140], ica_method = 'fastica', n_components = 0.99, 
                 max_iter = 800, random_state = 1688, epo_tmin=None, epo_tmax=None):
        """
        Initialize the Config class with provided parameters.

        Args:
            site (str): Site name.
            subject (str): Subject code.
            session (str): Data collection session.
            run (str): Data collection run, default is '01'.
            task (str): Task name.
            datatype (str): Data type, default is 'meg'.
            meg_suffix (str): Suffix for file names, default is 'meg'.
            extension (str): File extension, default is '.fif'.
            platform (str): Platform type, e.g., 'mac', 'windows', or 'bluebear'.
        """
        self.site = site
        self.subject = subject
        self.session = session
        self.run = run
        self.task = task
        self.datatype = datatype
        self.meg_suffix = meg_suffix
        self.extension = extension
        self.platform = platform

        self.method = method

        self.threshold_muscle = threshold_muscle  # decided individually based on the plot in P03
        self.min_length_good = min_length_good  # min acceptable duration for muscle artifact
        self.filter_freq = filter_freq  # filter frequency for muscle artifact

        self.ica_method = ica_method  # the method of ica
        self.n_components = n_components  # number of components that ica will generate or the precentage of variability to be explained
        self.random_state = random_state
        self.max_iter = max_iter

        self.epo_tmin = epo_tmin  # Set epoch timewindow
        self.epo_tmax = epo_tmax

        self.set_directories()
        self.set_maxwell_filter()
        
        if self.subject and self.task:
            self.create_deriv_folder()

    def set_directories(self):
        """
        Set directories based on the platform type.
        
        Raises:
            ValueError: If an invalid platform is provided.
        """
        if self.platform == 'bluebear':
            self.rds_dir = '/rds/projects/j/jenseno-avtemporal-attention'
            self.camcan_dir = '/rds/projects/q/quinna-camcan/dataman/data_information'
        elif self.platform == 'windows':
            self.rds_dir = 'Z:'
            self.camcan_dir = 'X:/dataman/data_information'
        elif self.platform == 'mac':
            self.rds_dir = '/Volumes/jenseno-avtemporal-attention'
            self.camcan_dir = '/Volumes/quinna-camcan/dataman/data_information'
        else:
            raise ValueError("Invalid platform. Choose 'bluebear', 'mac', or 'windows'.")

        self.mTBI_root = op.join(self.rds_dir, 'Projects/mTBI-predict')
        self.bids_root = op.join(self.mTBI_root, 'collected-data', 'BIDS', 'task_BIDS')
        self.deriv_root = op.join(self.bids_root, 'derivatives')
        self.report_root = op.join(self.mTBI_root, 'results-outputs/mne-reports')  # RDS folder for reports
        
        self.deriv_folder = None
        if self.subject and self.task:
            self.deriv_folder = op.join(self.deriv_root, f'sub-{self.subject}', f'task-{self.task}')

        self.report_folder = None
        if self.subject and self.session and self.task:
            self.report_folder = op.join(self.report_root , f'sub-{self.subject}', f'ses{self.session}', f'task-{self.task}')
            self.report_fname = op.join(self.report_folder,
                           f'report_sub-{self.subject}_{self.session}_{self.task}_full.hdf5')
            self.ICA_rej_dict = op.join(self.report_folder, f'group-analysis/task-{self.task}/rejected-ICs/{self.task}_rejected_ICS_all.npy')

    def create_deriv_report_folder(self):
        """
        Create the derivatives folder and report folder 
        if they do not exist.
        """
        if not op.exists(self.deriv_folder):
            os.makedirs(self.deriv_folder)
            
        if not op.exists(self.report_folder):
            os.makedirs(self.report_folder)
    
    def set_maxwell_filter(self):
        """
        Set the maxwell filter based on method.

        Raises:
            ValueError: If an invalid method is provided.
        """
        if self.method == 'tsss':
            self.st_duration = 10
        elif self.method == 'sss':
            self.st_duration = None
        else:
            raise ValueError("Invalid method. Choose 'sss', or 'tsss'.")
        

# these should be saved in a separate file I think       
# =============================================================================
# SESSION-SPECIFIC SETTINGS 
# =============================================================================
# Create an instance of the class for each subject
session_info = Config(site='Birmingham', 
                      subject='2013', 
                      session='02B', 
                      task='SpAtt')

# =============================================================================
# MAXWELL FILTERING SETTINGS
# =============================================================================




# =============================================================================
# ARTIFACT ANNOTATION SETTINGS
# =============================================================================

# Set muscle artifact threshold (z-scores)
# IMPORTTANT: This threshold is data dependent, check the optimal threshold by 
# plotting "scores_muscle"
threshold_muscle = Config(threshold_muscle=10)

# =============================================================================
# ICA SETTINGS
# =============================================================================


# =============================================================================
# EPOCHING SETTINGS
# =============================================================================
epoch_info = Config(tmin=-.7, 
                    tmax=1.7)

# =============================================================================
#  FACTOR AND CONDITIONS OF INTEREST
# =============================================================================

 