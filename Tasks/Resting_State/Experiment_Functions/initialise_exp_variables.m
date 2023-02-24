function cfgExp = initialise_exp_variables(cfgExp)
% cfgExp = initialise_exp_variables(cfgExp)
% Introduces variables of interest for SpAtt task
% to change any repetition you should edit this function

cfgExp.restDur = 5 * 60 * 1000;  % duration of each resting state session in ms (5 min)

if strcmp(cfgExp.answer.site,'Birmingham'), cfgExp.site = 2; elseif strcmp(cfgExp.answer.site,'Nottingham'), cfgExp.site = 3;
    strcmp(cfgExp.answer.site,'Aston'), cfgExp.site = 1; end  % Aston -> 1, UoB -> 2, UoN ->3
if strcmp(cfgExp.answer.pc,'MEG'), cfgExp.MEGLab = 1; else, cfgExp.MEGLab = 0; end  % MEG lab computer-> 1 PC-> 0
if strcmp(cfgExp.answer.test,'task'), cfgExp.task = 1; else, cfgExp.task = 0; end  % are we collecting data and running the task?

end
