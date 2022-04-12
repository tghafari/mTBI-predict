function cfgExp = initialise_variables(cfgExp)
% cfgExp = initialise_variables(cfgExp)
% Introduces variables of interest for SpAtt task
% to change any repetition you should edit this function

cfgExp.numBlock = 4;  % total number of blocks 
cfgExp.numTrial = 30;  % number of trials in each block
cfgExp.numStim = cfgExp.numTrial * cfgExp.numBlock;  % number of stimuli in total
cfgExp.ITIDur =  1000 + (2000 - 1000) .* rand(cfgExp.numStim,1);  % duration of ITI in ms
cfgExp.cueDur = 200;  % duration of cue presentation in ms
cfgExp.ISIDur = 1000;  % interval between cue and grating (stimulus)
cfgExp.stimDur = 1000 + (3000 - 1000) .* rand(cfgExp.numStim,1);  % duration of visual stimulus in ms
cfgExp.dotDur = 100;  % duration of red dot presentation
cfgExp.corrResp = ones(cfgExp.numStim,1);  % 1=>target present 0=>catch trials
cfgExp.corrResp(2:10:end,:) = 0; 
cfgExp.respTimOut = 500;  % time during which subject can respond in ms

if strcmp(cfgExp.answer.pc,'MEG'), cfgExp.MEGLab = 1; else, cfgExp.MEGLab = 0; end  % MEG lab computer-> 1 PC-> 0
if strcmp(cfgExp.answer.task,'task'), cfgExp.task = 1; else, cfgExp.task = 0; end  % are we collecting data and running the task?
if strcmp(cfgExp.answer.task,'train'), cfgExp.train = 1; else, cfgExp.train = 0; end  % are we training the participant?

end

% generate N random numbers in the interval (a,b): r = a + (b-a).*rand(N,1).