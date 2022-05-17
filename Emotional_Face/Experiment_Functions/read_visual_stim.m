function cfgStim = read_visual_stim(cfgFile, cfgStim, cfgExp)
% cfgStim = read_visual_stim(cfgFile, cfgStim, cfgExp)
% reads face images into cfgStim struct and
% randomises them for presentation

fileDirStim = dir([cfgFile.stim, '*.bmp']);

for fl = 1:length(fileDirStim)  % select only images with emotions of interest
    if contains(fileDirStim(fl).name, 'f_ne_c', 'IgnoreCase', true)
        cfgStim.faces.neutral.f{fl} = imread(fileDirStim(fl).name);
    elseif contains(fileDirStim(fl).name, 'f_ha_c', 'IgnoreCase', true)
        cfgStim.faces.happy.f{fl} = imread(fileDirStim(fl).name);
    elseif contains(fileDirStim(fl).name, 'f_an_c', 'IgnoreCase', true)
        cfgStim.faces.angry.f{fl} = imread(fileDirStim(fl).name);
    elseif contains(fileDirStim(fl).name, 'm_ne_c', 'IgnoreCase', true)
        cfgStim.faces.neutral.m{fl} = imread(fileDirStim(fl).name);
    elseif contains(fileDirStim(fl).name, 'm_ha_c', 'IgnoreCase', true)
        cfgStim.faces.happy.m{fl} = imread(fileDirStim(fl).name);
    elseif contains(fileDirStim(fl).name, 'm_an_c', 'IgnoreCase', true)
        cfgStim.faces.angry.m{fl} = imread(fileDirStim(fl).name);
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

% store images in temp variables
visStim_f(:,2) = repmat([cfgStim.faces.neutral.f,cfgStim.faces.happy.f,cfgStim.faces.angry.f]...
    , 1, cfgExp.numRep)';  % put all f faces in one matrix and repeat according to cfgExp
visStim_f(:,1) = repmat({'f'}, length(visStim_f), 1);  % mark the gender

visStim_m(:,2) = repmat([cfgStim.faces.neutral.m,cfgStim.faces.happy.m,cfgStim.faces.angry.m]...
    , 1, cfgExp.numRep);  % put all f faces in one matrix and repeat according to cfgExp
visStim_m(:,1) = repmat({'m'}, length(visStim_m), 1);  % mark the gender

rng('shuffle')  % randomize face stimuli with gender marks
cfgStim.visStim = [visStim_f; visStim_m];
cfgStim.visStim = cfgStim.visStim(randperm(length(cfgStim.visStim)),:);

% collect correct responses for questions in the corresponding row
cfgExp.corrResp = cell(cfgExp.numStim, 1);
cfgExp.corrResp(find(cfgExp.quesPres)) = cfgStim.visStim(find(cfgExp.quesPres), 1);
cfgExp.corrResp(find(cfgExp.quesPres == 0)) = {'no resp'};

end