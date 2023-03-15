function [cfgStim, cfgTrigger, cfgExp] = read_visual_stim(cfgFile, cfgStim, cfgExp, cfgTrigger)
% [cfgStim, cfgTrigger, cfgExp] = read_visual_stim(cfgFile, cfgStim, cfgExp, cfgTrigger)
% reads face images into cfgStim struct and
% randomises them for presentation

fileDirStim = dir([cfgFile.stim, '*.bmp']);

for fl = 1:length(fileDirStim)  % select only images with emotions of interest
    if contains(fileDirStim(fl).name, 'f_ne_c', 'IgnoreCase', true)
        cfgStim.faces.neutral.f{fl} = imread([fileDirStim(fl).folder filesep fileDirStim(fl).name]);
    elseif contains(fileDirStim(fl).name, 'f_ha_c', 'IgnoreCase', true)
        cfgStim.faces.happy.f{fl} = imread([fileDirStim(fl).folder filesep fileDirStim(fl).name]);
    elseif contains(fileDirStim(fl).name, 'f_an_c', 'IgnoreCase', true)
        cfgStim.faces.angry.f{fl} = imread([fileDirStim(fl).folder filesep fileDirStim(fl).name]);
    elseif contains(fileDirStim(fl).name, 'm_ne_c', 'IgnoreCase', true)
        cfgStim.faces.neutral.m{fl} = imread([fileDirStim(fl).folder filesep fileDirStim(fl).name]);
    elseif contains(fileDirStim(fl).name, 'm_ha_c', 'IgnoreCase', true)
        cfgStim.faces.happy.m{fl} = imread([fileDirStim(fl).folder filesep fileDirStim(fl).name]);
    elseif contains(fileDirStim(fl).name, 'm_an_c', 'IgnoreCase', true)
        cfgStim.faces.angry.m{fl} = imread([fileDirStim(fl).folder filesep fileDirStim(fl).name]);
    end
end

cfgStim.faces.neutral.f = cfgStim.faces.neutral.f(~cellfun('isempty', cfgStim.faces.neutral.f));  % remove empty indices  
cfgStim.faces.happy.f = cfgStim.faces.happy.f(~cellfun('isempty', cfgStim.faces.happy.f));  % remove empty indices  
cfgStim.faces.angry.f = cfgStim.faces.angry.f(~cellfun('isempty', cfgStim.faces.angry.f));  % remove empty indices  
cfgStim.faces.neutral.m = cfgStim.faces.neutral.m(~cellfun('isempty', cfgStim.faces.neutral.m));  % remove empty indices 
cfgStim.faces.happy.m = cfgStim.faces.happy.m(~cellfun('isempty', cfgStim.faces.happy.m));  % remove empty indices 
cfgStim.faces.angry.m = cfgStim.faces.angry.m(~cellfun('isempty', cfgStim.faces.angry.m));  % remove empty indices 
cfgStim.faces.neutral.m = cfgStim.faces.neutral.m(:,1:length(cfgStim.faces.neutral.f));  % equate number of f and m stimuli
cfgStim.faces.happy.m = cfgStim.faces.happy.m(:,1:length(cfgStim.faces.neutral.f));  % equate number of f and m stimuli
cfgStim.faces.angry.m = cfgStim.faces.angry.m(:,1:length(cfgStim.faces.neutral.f));  % equate number of f and m stimuli
numIDs = length(cfgStim.faces.neutral.m);  % temporarily used for matrix sizes

% store images and triggers in variables: 1->images, 2->sex trigger 4->emotion trigger
% 6->id trigger
visStim_m(:,1) = repmat([cfgStim.faces.neutral.m, cfgStim.faces.happy.m, cfgStim.faces.angry.m]...
    , 1, cfgExp.numRep)';  % put all m faces in one matrix and repeat according to cfgExp
visStim_m(:,2) = repmat([repmat({'neutral'}, numIDs, 1); repmat({'happy'}, numIDs, 1)...
    ; repmat({'angry'}, numIDs, 1)]', 1, cfgExp.numRep)';  % mark the emotion 
visStim_m(:,3) = num2cell(repmat([repmat(cfgTrigger.faceNeutral, numIDs, 1); repmat(cfgTrigger.faceHappy, numIDs, 1)...
    ; repmat(cfgTrigger.faceAngry, numIDs, 1)]', 1, cfgExp.numRep))';  % emotion trigger
visStim_m(:,4) = repmat({'faceID'}, length(visStim_m), 1);  % mark the gender
visStim_m(:,5) = num2cell(repmat([cfgTrigger.faceIDNeutral(1:numIDs), cfgTrigger.faceIDHappy(1:numIDs)...
    , cfgTrigger.faceIDAngry(1:numIDs)], 1, cfgExp.numRep)');  % male face IDs for trigger
visStim_m(:,6) = repmat({'m'}, length(visStim_m), 1);  % mark the gender
visStim_m(:,7) = num2cell(repmat(cfgTrigger.faceMale, length(visStim_m), 1));  % sex trigger

visStim_f(:,1) = repmat([cfgStim.faces.neutral.f, cfgStim.faces.happy.f, cfgStim.faces.angry.f]...
    , 1, cfgExp.numRep)';  % put all f faces in one matrix and repeat according to cfgExp
visStim_f(:,2) = repmat([repmat({'neutral'}, numIDs, 1); repmat({'happy'}, numIDs, 1)...
    ; repmat({'angry'}, numIDs, 1)]', 1, cfgExp.numRep)';  % mark the emotion 
visStim_f(:,3) = num2cell(repmat([repmat(cfgTrigger.faceNeutral, numIDs, 1); repmat(cfgTrigger.faceHappy, numIDs, 1)...
    ; repmat(cfgTrigger.faceAngry, numIDs, 1)]', 1, cfgExp.numRep))';  % emotion trigger
visStim_f(:,4) = repmat({'faceID'}, length(visStim_f), 1);  % mark the gender
visStim_f(:,5) = num2cell(repmat([cfgTrigger.faceIDNeutral(numIDs+1:numIDs*2), cfgTrigger.faceIDHappy(numIDs+1:numIDs*2)...
    , cfgTrigger.faceIDAngry(numIDs+1:numIDs*2)], 1, cfgExp.numRep)');  % female face IDs for trigger
visStim_f(:,6) = repmat({'f'}, length(visStim_f), 1);  % mark the sex
visStim_f(:,7) = num2cell(repmat(cfgTrigger.faceFemale, length(visStim_f), 1));  % sex trigger

rng('shuffle')  % randomize face stimuli with gender marks
cfgStim.visStim = [visStim_f; visStim_m];
cfgStim.visStim = cfgStim.visStim(randperm(length(cfgStim.visStim)),:);
cfgTrigger.faceTrigAll = cfgStim.visStim(:,2:end);

% collect correct responses for questions in the corresponding row
cfgExp.corrResp = cell(cfgExp.numStim, 3);
cfgExp.corrResp(find(cfgExp.quesPres),1) = cfgStim.visStim(find(cfgExp.quesPres), 6);
cfgExp.corrResp(find(contains(cfgStim.visStim(:,6),'m')), 2) = {'RightArrow'};
cfgExp.corrResp(find(contains(cfgStim.visStim(:,6),'f')), 2) = {'LeftArrow'};
cfgExp.corrResp(find(contains(cfgStim.visStim(:,6),'m')), 3) = {'7&'};
cfgExp.corrResp(find(contains(cfgStim.visStim(:,6),'f')), 3) = {'4$'};
cfgExp.corrResp(find(cfgExp.quesPres == 0), :) = {'no resp'};


end