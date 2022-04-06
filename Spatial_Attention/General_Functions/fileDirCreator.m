function filedir = fileDirCreator(answer)
%[fileDirStim,fileDirRes,fileDirCue] = fileDirCreator(answer)
%   cd to and creates subject directory according to OS

tmp = matlab.desktop.editor.getActive;
cd(fileparts(tmp.Filename));  % move to the current directory
cd ..  % move up one folder

addpath([cd, '\Experiment_Functions\']);  % add the sub-functions
addpath([cd, '\General_Functions\']);  % add the more generic sub-functions
addpath([cd, '\Eyelink\']);  % add Eyelink functions
addpath([cd, '\Stimuli\']);  % add stimulus images
addpath([cd, '\Results\']);  % add result folder

if strcmp(answer.pc,'mac')  % needs modification in case of using mac at all
    filedir.res  = 'Projects/mTBI predict/Programming/Matlab/Results/';
    filedir.stim = [cd, '/Stimuli/Visual_Stimuli/']; 
    filedir.cue = [cd, '/Stimuli/Cue/'];
elseif strcmp(answer.pc,'win')
    filedir.res = [cd, '\Results\'] ; 
    filedir.stim = [cd, '\Stimuli\Visual_Stimuli\'];
    filedir.cue = [cd, '\Stimuli\Cue_Stimuli\'];
elseif strcmp(answer.pc,'MEG')
    filedir.res = [cd, '\Results\'] ; 
    filedir.stim = [cd, '\Stimuli\Visual_Stimuli\'];
    filedir.cue = [cd, '\Stimuli\Cue_Stimuli\'];
end

mkdir([filedir.res, answer.code, answer.date]);

end

