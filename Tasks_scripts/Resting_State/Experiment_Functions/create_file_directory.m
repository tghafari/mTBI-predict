function cfgFile = create_file_directory(cfgExp)
%[fileDirStim,fileDirRes,fileDirCue] = create_file_directory(cfgExp)
%   cd to and creates subject directory according to OS

tmp = matlab.desktop.editor.getActive;
cd(fileparts(tmp.Filename));  % move to the current directory
cd ..  % move up one folder

addpath([cd, '\Experiment_Functions\']);  % add the sub-functions
addpath([cd, '\Eyelink\']);  % add Eyelink functions
addpath([cd, '\Results\']);  % add result folder

if strcmp(cfgExp.answer.pc,'win')
    cfgFile.res = [cd, '\Results\'] ; 
elseif strcmp(cfgExp.answer.pc,'MEG')
    cfgFile.res = [cd, '\Results\'] ; 
end

mkdir([cfgFile.res, 'sub-', cfgExp.answer.sub, filesep, 'ses-', cfgExp.answer.ses, filesep, 'meg', filesep]);  % make result directory with BIDS format
cfgFile.subDir = [cfgFile.res, 'sub-', cfgExp.answer.sub, filesep, 'ses-' cfgExp.answer.ses, filesep, 'meg', filesep];  % store subject directory address
cfgFile.BIDSname = ['sub-', cfgExp.answer.sub, '_', 'ses-', cfgExp.answer.ses, '_'...
    , 'task-', cfgExp.answer.task, '_', 'run-', cfgExp.answer.run];  % BIDS specific file name
cfgFile.edfFile = ['_eyetracking', '.edf'];  % eyetracking file name
cfgFile.logFile = ['_logfile', '.mat'];  % logfile file name
cfgFile.eyelink = ['e', cfgExp.answer.run, cfgExp.answer.sub];  % file name to use on eyelink pc

cd(fileparts(tmp.Filename));  % move back to the experiment_functions directory for io64.mexw64 file

end

