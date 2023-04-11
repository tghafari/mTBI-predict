function cfgFile = create_file_directory(cfgExp)
%[fileDirStim,fileDirRes,fileDirCue] = create_file_directory(cfgExp)
%   cd to and creates subject directory according to OS

tmp = matlab.desktop.editor.getActive;
cd(fileparts(tmp.Filename));  % move to the current directory
cd ..  % move up one folder

addpath([cd, '\Experiment_Functions\']);  % add the sub-functions
addpath([cd, '\Eyelink\']);  % add Eyelink functions
addpath([cd, '\Stimuli\']);  % add stimulus images
addpath([cd, '\Results\']);  % add result folder

if strcmp(cfgExp.answer.pc,'win')
    cfgFile.res = [cd, '\Results\'] ; 
    cfgFile.stim = [cd, '\Stimuli\Visual_Stimuli\'];
    cfgFile.cue = [cd, '\Stimuli\Cue_Stimuli\'];
elseif strcmp(cfgExp.answer.pc,'MEG')
    cfgFile.res = [cd, '\Results\'] ; 
    cfgFile.stim = [cd, '\Stimuli\Visual_Stimuli\'];
    cfgFile.cue = [cd, '\Stimuli\Cue_Stimuli\'];
end

mkdir([cfgFile.res, 'sub-', cfgExp.answer.sub, filesep, 'ses-', cfgExp.answer.ses, filesep, 'meg', filesep]);  % make result directory with BIDS format
cfgFile.subDir = [cfgFile.res, 'sub-', cfgExp.answer.sub, filesep, 'ses-' cfgExp.answer.ses, filesep, 'meg', filesep];  % store subject directory address
if strcmp(cfgExp.answer.test,'train')
    cfgFile.BIDSname = ['sub-', cfgExp.answer.sub, '_', 'ses-', cfgExp.answer.ses, '_'...
     , 'train-', cfgExp.answer.task, '_', 'run-', cfgExp.answer.run];  % BIDS specific file name
else
cfgFile.BIDSname = ['sub-', cfgExp.answer.sub, '_', 'ses-', cfgExp.answer.ses, '_'...
    , 'task-', cfgExp.answer.task, '_', 'run-', cfgExp.answer.run];  % BIDS specific file name
end
cfgFile.edfFile = ['_eyetracking', '.edf'];  % eyetracking file name
cfgFile.logFile = ['_logfile', '.mat'];  % logfile file name
cfgFile.eyelink = ['e', cfgExp.answer.run, cfgExp.answer.sub];  % file name to use on eyelink pc

cd(fileparts(tmp.Filename));  % move back to the experiment_functions directory for io64.mexw64 file

end

