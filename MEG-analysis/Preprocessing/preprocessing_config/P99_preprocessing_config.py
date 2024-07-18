"""
===============================================
P99. Preprocessing_config

Instructions for users:

1. Project Setup:
   Ensure the project directory structure is as follows:
   - project_root/
     - scripts/
     - config/
     - (other project files and directories)

2. Environment Configuration:
   Modify the `project_root` variable to point to the root directory of your project.
   This script automatically adds the project root, scripts, and config directories to the PYTHONPATH.

3. Subject and Session Configuration:
   Edit the `sub_dict` dictionary to include the subjects and sessions you want to process. 
   For example:
   sub_dict = {'subjects': ['2015', '2016'], 'sessions': ['03B', '04B']}

4. Scripts to Execute:
   List of the `scripts` in the order they should be executed.

5. Running the Script:
   Run this script in mne environment from the command line:

   python P99_preprocessing_config.py

This will iterate over all subject-session pairs and execute the listed scripts for each pair.

6. Error Handling:
    If any script encounters an error, it will print the error message and try to continue with the next script.
    Successfully executed scripts will print a success message.

written by Tara Ghafari
t.ghafari@bham.ac.uk
"""

import subprocess
import os
import os.path as op
import sys

# Add the project root directory to the sys.path
# project_root = '/Volumes/jenseno-avtemporal-attention/Projects/mTBI-predict/programming/github/mTBI-predict/MEG-analysis/Preprocessing/preprocessing_config'
project_root =  op.dirname(op.abspath(__file__))
scripts_root = op.join(project_root, 'scripts')
config_root = op.join(project_root, 'config')
sys.path.append(project_root)
sys.path.append(scripts_root)
sys.path.append(config_root)

from config import Config

# Subject and session dictionary
sub_dict =  {'subjects': ['2015', '2015', '2015'], 'sessions': ['03B', '05B', '06B']}

# List of scripts to execute in order
scripts = [
    'P02_apply_maxfilter_config.py',
    'P03_artifact_annotation_config.py',
    'P04_run_apply_ICA_config.py',
    'P05_epoching_config.py'
]

def run_preprocessing(script_path, script, subject, session):
    """
    Run a script with script_path, script, subject and session as arguments.
    
    Parameters:
    - script_path (str): path to the script to run
    - script (str): name of the script
    - subject (str): subject identifier
    - session (str): session identifier
    
    This function sets the necessary environment variable (PYTHONPATH) and
    executes the script using the subprocess module. It captures and prints
    any errors encountered during the execution.
    """
    # Prepare the environment with PYTHONPATH set to the project root
    print("Reading environment")
    env = os.environ.copy()
    env['PYTHONPATH'] = project_root + os.pathsep + env.get('PYTHONPATH', '')

    cmd = [sys.executable, script_path, '--subject', str(subject), '--session', str(session)]
    result = subprocess.run(cmd, env=env)

    if result.returncode != 0:
        print(f"Error running {script} for subject {subject}, session {session}:")
        print(result.stderr)
    else:
        print(f"Successfully ran {script} for subject {subject}, session {session}")

# Iterate over all subject-session pairs and run the scripts
for subject, session in zip(sub_dict['subjects'], sub_dict['sessions']):
    for script in scripts:
        print(f"\nRunning {script} on subject {subject}, session {session}")
        script_path = op.join(scripts_root, script)
        run_preprocessing(script_path, script, subject, session)