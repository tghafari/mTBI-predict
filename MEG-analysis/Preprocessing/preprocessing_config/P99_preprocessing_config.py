import subprocess
import os.path as op

# Subject and session dictionary
sub_dict = {'subjects': [2016], 'sessions': ['05B']}

# Path to the scripts directory
scripts_dir = '/Volumes/jenseno-avtemporal-attention/Projects/mTBI-predict\
         /programming/github/mTBI-predict/MEG-analysis/SpAtt/Preprocessing\
         /preprocessing_config/scripts'

# List of scripts to execute in order
scripts = [
    'P02_apply_maxfilter_config.py']
# ,
#     'P03_artifact_annotation_config.py',
#     'P04_run_apply_ICA_config.py',
#     'P05_epoching_config.py'
# ]

def run_script(script, subject, session):
    """
    Run a script with subject and session as arguments.
    """
    script_path = op.join(scripts_dir, script)
    cmd = ['python', script_path, '--subject', str(subject), '--session', str(session)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error running {script} for subject {subject}, session {session}:")
        print(result.stderr)
    else:
        print(f"Successfully ran {script} for subject {subject}, session {session}")

# Iterate over all subject-session pairs and run the scripts
for subject, session in zip(sub_dict['subjects'], sub_dict['sessions']):
    print(f"\nProcessing subject {subject}, session {session}")
    for script in scripts:
        run_script(script, subject, session)
