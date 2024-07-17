



import subprocess
import os
import os.path as op
import sys

# Add the project root directory to the sys.path
#project_root = '/Volumes/jenseno-avtemporal-attention/Projects/mTBI-predict/programming/github/mTBI-predict/MEG-analysis/Preprocessing/preprocessing_config'
project_root =  op.dirname(op.abspath(__file__))
scripts_root = op.join(project_root, 'scripts')
config_root = op.join(project_root, 'config')
sys.path.append(project_root)
sys.path.append(scripts_root)
sys.path.append(config_root)

from config import Config

# Subject and session dictionary
sub_dict = {'subjects': [2016], 'sessions': ['05B']}

# List of scripts to execute in order
scripts = [
    # 'P02_apply_maxfilter_config.py',
    # 'P03_artifact_annotation_config.py',
    'P04_run_apply_ICA_config.py',
    # 'P05_epoching_config.py'
]

def run_preprocessing(script_path, script, subject, session):
    """
    Run a script with subject and session as arguments.
    """
    # Prepare the environment with PYTHONPATH set to the project root
    print("Reading environment")
    env = os.environ.copy()
    env['PYTHONPATH'] = project_root + os.pathsep + env.get('PYTHONPATH', '')

    # # Call the main function directly
    # print("1-Maxwell Filter")
    # apply_maxfilter(subject, session)
    # print(f"Successfully ran P02_apply_maxfilter_config.py for subject {subject}, session {session}")

    # Run the script using subprocess
    # cmd = ['python', script_path, '--subject', str(subject), '--session', str(session)]
    # result = subprocess.run([sys.executable, cmd], capture_output=True, text=True, env=env, check=True)

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