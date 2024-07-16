function [cfgStim, cfgExp, cfgTrigger] = read_visual_stim(cfgFile, cfgExp, cfgStim, cfgTrigger)
% [cfgStim, cfgExp, cfgTrigger] = read_visual_stim(cfgFile, cfgExp, cfgStim, cfgTrigger)
% randomly reads the visual stimuli
% inputs are the directory of stimuli images and number of trials/stim

fileDirStim = dir([cfgFile.stim, '*.bmp']);  % only use the files ending in .bmp (not unwanted files)
fileDirCue = dir([cfgFile.cue, '*.jpg']);

[~,idx] = sort(str2double(regexp({fileDirStim.name},'(?<=cube3D)\d+','match','once'))); % sort the file names increasingly  
cfgStim.fNameStimSortd = fileDirStim(idx);

cfgStim.visStim = cell(length(1:cfgStim.stimRotSpeed:length(cfgStim.fNameStimSortd)), 1);  % preallocation
cfgStim.cueStim = cell(cfgExp.numStim, 1);  % preallocation

% read stimulus images 
for spd = 1:cfgStim.stimRotSpeed:length(cfgStim.fNameStimSortd)
    cfgStim.visStim{spd} = imread(cfgStim.fNameStimSortd(spd).name);
end
cfgStim.visStim = cfgStim.visStim(~cellfun('isempty', cfgStim.visStim'));  % remove indices that are empty due to reading images based on speed

rng('shuffle')
cfgStim.cueRndIdx = randperm(cfgExp.numStim);  % random index for cue - 1:right, 2:left

% Make sure there's an equal number of 1 and 2 in cfgStim.cueRndIdx
cfgStim.cueRndIdx(mod(cfgStim.cueRndIdx, 2) == 0) = 2;
cfgStim.cueRndIdx(mod(cfgStim.cueRndIdx, 2) ~= 0) = 1;

for stim = 1:cfgExp.numStim
    cfgStim.cueStim{stim,1} = imread(fileDirCue(cfgStim.cueRndIdx(stim)).name);  % read cue randomly
end

% collect correct responses +
% cue, stim and dot triggers
cfgExp.cuesDir = cell(cfgExp.numStim, 1);  % preallocation
cfgTrigger.cuesDir = cell(cfgExp.numStim, 2);  % preallocation
cfgTrigger.dotDir = cell(cfgExp.numStim, 2);  % preallocation

cfgExp.cuesDir(find(cfgStim.cueRndIdx == 1), 1) = {'Right'};
cfgExp.cuesDir(find(cfgStim.cueRndIdx == 2), 1) = {'Left'};
cfgExp.cuesDir(find(cfgExp.corrResp == 0), 1) = {'no resp'};
cfgTrigger.cuesDir(find(cfgStim.cueRndIdx == 1), 1) = {'101'};  % MEG trigger codes are 101 -> cue right, 102 -> cue left
cfgTrigger.cuesDir(find(cfgStim.cueRndIdx == 2), 1) = {'102'};  % MEG trigger codes are 101 -> cue right, 102 -> cue left
cfgTrigger.cuesDir(find(cfgStim.cueRndIdx == 1), 2) = {'Right'};  % trigger message for Eyelink
cfgTrigger.cuesDir(find(cfgStim.cueRndIdx == 2), 2) = {'Left'};  
cfgTrigger.dotDir(find(cfgStim.cueRndIdx == 1), 1) = {'211'};  % MEG trigger codes are 211 -> dot right, 212 -> dot left
cfgTrigger.dotDir(find(cfgStim.cueRndIdx == 2), 1) = {'212'};  % MEG trigger codes are 211 -> dot right, 212 -> dot left
cfgTrigger.dotDir(find(cfgStim.cueRndIdx == 1), 2) = {'Right'};  % trigger message for Eyelink
cfgTrigger.dotDir(find(cfgStim.cueRndIdx == 2), 2) = {'Left'};  
cfgTrigger.dotDir(find(cfgExp.corrResp == 0), [1, 2]) = {'no resp'};

end