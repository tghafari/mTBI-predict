function [cfgExp, cfgOutput] = initialise_exp_variables(cfgExp)
% [cfgExp, cfgOutput] = initialise_exp_variables(cfgExp)
% Introduces variables of interest for SpAtt task
% to change any repetition you should edit this function

rng('shuffle')
% total time: ~7.5 minute (2 to 2.5 sec each trial, ~2.5 min each block)
cfgExp.trgRstTm = 0.005;  % reset time for triggers
cfgExp.trgSftTm = 0.003;  % safe time after resetting the triggers
timeBalancer = cfgExp.trgRstTm + cfgExp.trgSftTm;  % time that needs to be removed to compensate for trigger duration
cfgExp.numBlock = 3;  % total number of blocks (3)
cfgExp.numRep = 2;  % number of repetitions of each specific visual stimuli (2)
cfgExp.numImg = 18;  % number of face images for each gender (2) and emotion (3: neu, hap, ang) (18)
cfgExp.numTrial = cfgExp.numImg * cfgExp.numRep * 2 * 3 / cfgExp.numBlock;  % number of trials in each block
cfgExp.numStim = cfgExp.numTrial * cfgExp.numBlock;  % number of stimuli/trials in total
cfgExp.ISIDur = 750 + (1000 - 750) .* rand(cfgExp.numStim, 1) - (2 * timeBalancer);  % interval between two images in ms (fixation dot duration) (subtract triggers: faceOn, trialOn)
cfgExp.stimDur = 750 + (1000 - 750) .* rand(cfgExp.numStim, 1) - (3 * timeBalancer);  % duration of face presentation in ms (subtract trigger duration: ID, Sex, faceOff) 
cfgExp.numQu = ceil(0.125 * cfgExp.numStim);  % 12.5% of trials include a question about the gender of the face
cfgExp.quesPres = [ones(cfgExp.numQu, 1); zeros(cfgExp.numStim - cfgExp.numQu, 1)];  % 1=>question present 0=>no question
cfgExp.quesPres = cfgExp.quesPres(randperm(length(cfgExp.quesPres)));  % randomize order of question trials
cfgExp.quesDur = 750 + (1000 - 750) .* rand(cfgExp.numStim, 1);  % duration of question display in ms
cfgExp.respTimOut = 1500;  % time during which subject can respond in ms

cfgOutput.keyName = cell(cfgExp.numStim, 1);  % preallocate cfgOutput for unpressed trials
cfgOutput.keyName = repmat({'no resp'}, length(cfgOutput.keyName), 1);  % put the default response to 'no resp'

if strcmp(cfgExp.answer.site,'Birmingham')
    cfgExp.site = 2;  % UoB -> 2
elseif strcmp(cfgExp.answer.site,'Nottingham')
    cfgExp.site = 3;  % UoN ->3
elseif strcmp(cfgExp.answer.site,'Aston')
    cfgExp.site = 1;  % Aston -> 1
end  

if strcmp(cfgExp.answer.pc,'MEG'), cfgExp.MEGLab = 1; else, cfgExp.MEGLab = 0; end  % MEG lab computer-> 1 PC-> 0
if strcmp(cfgExp.answer.test,'task'), cfgExp.task = 1; else, cfgExp.task = 0; end  % are we collecting data and running the task?
if strcmp(cfgExp.answer.test,'train'), cfgExp.train = 1; else, cfgExp.train = 0; end  % are we training the participant?

end

% generate N random numbers in the interval (a,b): r = a + (b-a).*rand(N,1).