function cfgStim = read_visual_stim(cfgFile, cfgExp, cfgStim)
% cfgStim = read_visual_stim(cfgFile, cfgExp, cfgStim)
% randomly reads the visual stimuli
% inputs are the directory of stimuli images and number of trials/stim

fileDirStim = dir([cfgFile.stim, '*.bmp']);  % only use the files ending in .bmp (not unwanted files)
fileDirCue = dir([cfgFile.cue, '*.jpg']);

[~,idx] = sort(str2double(regexp({fileDirStim.name},'(?<=cube3D)\d+','match','once'))); % sort the file names increasingly  
cfgStim.fNameStimSortd = fileDirStim(idx);

cfgStim.visStim = cell(length(1:cfgStim.stimRotSpeed:length(cfgStim.fNameStimSortd)), 1);  % preallocation
% cfgStim.visStimR = cell(length(fileDirStim) - 3, 1);  % preallocation
% cfgStim.visStimL = cell(length(fileDirStim) - 3, 1);  % preallocation
cfgStim.cueStim = cell(cfgExp.numStim, 1);  % preallocation


% read right and left images separately
for spd = 1:cfgStim.stimRotSpeed:length(cfgStim.fNameStimSortd)
    cfgStim.visStim{spd} = imread(cfgStim.fNameStimSortd(spd).name);
%     cfgStim.visStimR{spd-2} = imread(fileDirStim(spd).name);  % in case you'd want to have different stim for left and right
%     cfgStim.visStimL{spd-2} = imread(fileDirStim(spd).name);
end
cfgStim.visStim = cfgStim.visStim(~cellfun('isempty', cfgStim.visStim'));  % remove indices that are empty due to reading images based on speed
% cfgStim.visStimR = cfgStim.visStimR(~cellfun('isempty', cfgStim.visStimR'));  
% cfgStim.visStimL= cfgStim.visStimL(~cellfun('isempty', cfgStim.visStimL'));

rng('shuffle')
cfgStim.cueRndIdx = randi(2, cfgExp.numStim, 1);  % random index for cue - 1:left, 2:right
for stim = 1:cfgExp.numStim
    cfgStim.cueStim{stim,1} = imread(fileDirCue(cfgStim.cueRndIdx(stim)).name);  % read cue randomly
end

end