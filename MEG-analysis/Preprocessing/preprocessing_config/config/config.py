# -*- coding: utf-8 -*-
"""
===========
Config file
===========

Configurate the parameters of the mTBI-predict study.

written by Tara Ghafari
"""

import os
import os.path as op

class Config:
    """
    Configuration class for setting up directory paths and other parameters 
    for preprocessing MEG data.
    """

    class SessionInfo:
        def __init__(self, site=None, subject=None, session=None, run='01', task=None, datatype='meg', meg_suffix='meg', extension='.fif', platform='mac'):
            self.site = site
            self.subject = subject
            self.session = session
            self.run = run
            self.task = task
            self.datatype = datatype
            self.meg_suffix = meg_suffix
            self.extension = extension

    class ICAConfig:
        def __init__(self, n_components=0.99, random_state=97, ica_method='fastica', max_iter=800):
            self.n_components = n_components
            self.random_state = random_state
            self.ica_method = ica_method
            self.max_iter = max_iter

    class ArtifactConfig:
        def __init__(self, threshold_muscle=None, min_length_good=0.2, filter_freq=[110, 140]):
            self.threshold_muscle = threshold_muscle
            self.min_length_good = min_length_good
            self.filter_freq = filter_freq

    class DirectoryConfig:
        def __init__(self, platform='mac', site=None, subject=None, session=None, task=None):
            self.platform = platform
            self.set_directories()
            if subject and task:
                self.create_deriv_report_folder(site, subject, session, task)
        
        def set_directories(self):
            """
            Set directories based on the platform type.
            
            Raises:
                ValueError: If an invalid platform is provided.
            """
            platform_dirs = {
                'bluebear': {
                    'rds_dir': '/rds/projects/j/jenseno-avtemporal-attention',
                    'camcan_dir': '/rds/projects/q/quinna-camcan/dataman/data_information'
                },
                'windows': {
                    'rds_dir': 'Z:',
                    'camcan_dir': 'X:/dataman/data_information'
                },
                'mac': {
                    'rds_dir': '/Volumes/jenseno-avtemporal-attention',
                    'camcan_dir': '/Volumes/quinna-camcan/dataman/data_information'
                }
            }

            if self.platform not in platform_dirs:
                raise ValueError("Invalid platform. Choose 'bluebear', 'mac', or 'windows'.")

            dirs = platform_dirs[self.platform]
            self.rds_dir = dirs['rds_dir']
            self.camcan_dir = dirs['camcan_dir']

            self.mTBI_root = op.join(self.rds_dir, 'Projects/mTBI-predict')
            self.bids_root = op.join(self.mTBI_root, 'collected-data', 'BIDS', 'task_BIDS')
            self.deriv_root = op.join(self.bids_root, 'derivatives')
            self.report_root = op.join(self.mTBI_root, 'results-outputs/mne-reports')

        def create_deriv_report_folder(self, site, subject, session, task):
            """
            Create the derivatives folder and report folder if they do not exist.
            """
            self.deriv_folder = op.join(self.deriv_root, f'sub-{subject}', f'task-{task}')
            if not op.exists(self.deriv_folder):
                os.makedirs(self.deriv_folder)

            self.report_folder = op.join(self.report_root, f'sub-{subject}', f'ses{session}', f'task-{task}')
            if not op.exists(self.report_folder):
                os.makedirs(self.report_folder)

            self.report_fname = op.join(self.report_folder, f'report_sub-{subject}_{session}_{task}_full.hdf5')
            self.ICA_rej_dict = op.join(self.report_folder, f'group-analysis/task-{task}/rejected-ICs/{task}_rejected_ICS_all.npy')

    class EpochConfig:
        def __init__(self, epo_tmin=None, epo_tmax=None):
            self.epo_tmin = epo_tmin
            self.epo_tmax = epo_tmax

    def __init__(self, site=None, subject=None, session=None, run='01', task=None, datatype='meg', meg_suffix='meg', extension='.fif', platform='mac', 
                 maxwell_method='sss', threshold_muscle=None, min_length_good=.2, filter_freq=[110,140], n_components=0.99, random_state=97, 
                 ica_method='fastica', max_iter=800, epo_tmin=None, epo_tmax=None):
        
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
        maxwell_method (str): method of maxwell filter, e.g., 'sss' or 'tsss'.
        threshold_muscle (float): the threshold of rejecting artifact based on muscle activity.
        min_length_good (float): The shortest allowed duration of “good data” (in seconds), e.g., 0.2.
        filter_freq (array_like): lower and upper frequencies of the band-pass filter for muscle activity.
        n_components (int, float): number of PCAs or min number of components to explain the variance. Default is 99%.
        random_state (int): Seed for random number generator, default is 97.
        ica_method (str): The ICA method to use in the fit method, default is 'fastica'.
        max_iter (int): Maximum number of iterations during fit, default is 800.
        epo_tmin (float): tmin for epoching, e.g., for spatial attention epo_tmin = -0.7
        epo_tmax (float): tmax for epoching, e.g., for spatial attention epo_tmax = 1.7
        """
                
        # Config sub-classes
        self.session_info = self.SessionInfo(site, subject, session, run, task, datatype, meg_suffix, extension)
        self.ica = self.ICAConfig(n_components, random_state, ica_method, max_iter)
        self.artifact = self.ArtifactConfig(threshold_muscle, min_length_good, filter_freq)
        self.directories = self.DirectoryConfig(platform, site, subject, session, task)
        self.epoch = self.EpochConfig(epo_tmin, epo_tmax)

        self.set_maxwell_filter()

    def set_maxwell_filter(self):
        """
        Set the maxwell filter based on the method.

        Raises:
            ValueError: If an invalid method is provided.
        """
        if self.maxwell_method == 'tsss':
            self.st_duration = 10
        elif self.maxwell_method == 'sss':
            self.st_duration = None
        else:
            raise ValueError("Invalid maxwell_method. Choose 'sss', or 'tsss'.")

# EXAMPLES
"""
# =============================================================================
# SESSION-SPECIFIC SETTINGS 
# =============================================================================
# Create an instance of the class for each subject
session_info = Config(site='Birmingham', 
                      subject='2013', 
                      session='02B', 
                      task='SpAtt')

# =============================================================================
# ARTIFACT ANNOTATION SETTINGS
# =============================================================================
# Set muscle artifact threshold (z-scores)
# IMPORTTANT: This threshold is data dependent, check the optimal threshold by 
# plotting "scores_muscle"
artifact_info = Config.ArtifactConfig(threshold_muscle=10)

# =============================================================================
# EPOCHING SETTINGS
# =============================================================================
epoch_info = Config.EpochConfig(epo_tmin=-.7, epo_tmax=1.7)
"""