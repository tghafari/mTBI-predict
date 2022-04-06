function cfgExp = KbQueueStarterRoutine(cfgExp)
% KbQueueStarterRoutine(MEGLab,expDev)
% Starts KbQueueRoutine for the keyboard to start listening
% A call to KbQueueCheck is required for participants response

KbName('UnifyKeyNames');
cfgExp.quitKey = KbName('ESCAPE');  % quit key
cfgExp.pauseKey = KbName('p');  % pause key
cfgExp.respKey = KbName('RightArrow');  % keyboard response
cfgExp.NATAKey = KbName('7&');  % NATA box response
cfgExp.yesKey = KbName('y');  % yes response

% KB response: '4$' and '7&' are the left and right index fingers of the (5-button) NATA boxes
if cfgExp.MEGLab == 1
    cfgExp.activeKeys = [cfgExp.quitKey, cfgExp.pauseKey, cfgExp.NATAKey, cfgExp.yesKey];
    cfgExp.deviceNum = -1;  % listen to all devices during test/train
else
    cfgExp.activeKeys = [cfgExp.quitKey, cfgExp.pauseKey, cfgExp.respKey, cfgExp.yesKey];
    cfgExp.deviceNum = -1;  % listen to all devices during test/train
end

% only listen for specific keys
scanList = zeros(1,256);
scanList(cfgExp.activeKeys) = 1;
KbQueueCreate(cfgExp.deviceNum,scanList);  % create queue
KbQueueStart;  % start listening to input
KbQueueFlush;  % clear all keyboard presses so far

end
