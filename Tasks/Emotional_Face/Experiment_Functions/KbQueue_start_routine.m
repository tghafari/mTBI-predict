function cfgExp = KbQueue_start_routine(cfgExp)
% KbQueue_start_routine(cfgExp)
% Starts KbQueueRoutine for the keyboard to start listening
% A call to KbQueueCheck is required for participants response

KbName('UnifyKeyNames');
cfgExp.quitKey = KbName('ESCAPE');  % quit key
cfgExp.respKeyM = KbName('RightArrow');  % keyboard response male
cfgExp.respKeyF = KbName('LeftArrow');  % keyboard response female
cfgExp.NATAKeyM = KbName('7&');  % NATA box response male
cfgExp.NATAKeyF = KbName('4$');  % NATA box response female
cfgExp.yesKey = KbName('y');  % yes response
cfgExp.noKey = KbName('n');  % no key
cfgExp.responses = [cfgExp.NATAKeyF, cfgExp.NATAKeyM, cfgExp.respKeyF, cfgExp.respKeyM];

% KB response: '4$' and '7&' are the left and right index fingers of the (5-button) NATA boxes
if cfgExp.MEGLab == 1
    cfgExp.activeKeys = [cfgExp.quitKey, cfgExp.NATAKeyF, cfgExp.NATAKeyM, cfgExp.yesKey, cfgExp.noKey];
    cfgExp.deviceNum = -1;  % listen to all devices during test/train
else
    cfgExp.activeKeys = [cfgExp.quitKey, cfgExp.respKeyF, cfgExp.respKeyM, cfgExp.yesKey, cfgExp.noKey];
    cfgExp.deviceNum = -1;  % listen to all devices during test/train
end

% only listen for specific keys
scanList = zeros(1,256);
scanList(cfgExp.activeKeys) = 1;
KbQueueCreate(cfgExp.deviceNum,scanList);  % create queue
KbQueueStart;  % start listening to input
KbQueueFlush;  % clear all keyboard presses so far

end
