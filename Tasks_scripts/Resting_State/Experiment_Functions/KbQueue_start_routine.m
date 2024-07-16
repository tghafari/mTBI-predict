function cfgExp = KbQueue_start_routine(cfgExp)
% KbQueue_start_routine(cfgExp)
% Starts KbQueueRoutine for the keyboard to start listening
% A call to KbQueueCheck is required for participants response

KbName('UnifyKeyNames');
cfgExp.quitKey = KbName('ESCAPE');  % quit key
cfgExp.noKey = KbName('n');  % no key
cfgExp.yesKey = KbName('y');  % yes response
cfgExp.activeKeys = [cfgExp.quitKey, cfgExp.noKey, cfgExp.yesKey];

% only listen for specific keys
cfgExp.deviceNum = -1;
scanList = zeros(1,256);
scanList(cfgExp.activeKeys) = 1;
KbQueueCreate(cfgExp.deviceNum, scanList);  % create queue
KbQueueStart;  % start listening to input
KbQueueFlush;  % clear all keyboard presses so far

end
