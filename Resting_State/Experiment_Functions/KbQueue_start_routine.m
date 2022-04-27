function cfgExp = KbQueue_start_routine(cfgExp)
% KbQueue_start_routine(cfgExp)
% Starts KbQueueRoutine for the keyboard to start listening
% A call to KbQueueCheck is required for participants response

KbName('UnifyKeyNames');
cfgExp.quitKey = KbName('ESCAPE');  % quit key
cfgExp.pauseKey = KbName('p');  % pause key
cfgExp.respKey = KbName('RightArrow');  % keyboard response
cfgExp.yesKey = KbName('y');  % yes response

% participant cannot respond with NATA box
cfgExp.activeKeys = [cfgExp.quitKey, cfgExp.pauseKey, cfgExp.respKey, cfgExp.yesKey];
cfgExp.deviceNum = -1;  % listen to all devices during test/train

% only listen for specific keys
scanList = zeros(1,256);
scanList(cfgExp.activeKeys) = 1;
KbQueueCreate(cfgExp.deviceNum,scanList);  % create queue
KbQueueStart;  % start listening to input
KbQueueFlush;  % clear all keyboard presses so far

end
