function cfgExp = KbQueue_start_routine(cfgExp)
% KbQueue_start_routine(cfgExp)
% Starts KbQueueRoutine for the keyboard to start listening
% A call to KbQueueCheck is required for participants response

KbName('UnifyKeyNames');
cfgExp.quitKey = KbName('ESCAPE');  % quit key
cfgExp.noKey = KbName('n');  % no key
cfgExp.yesKey = KbName('y');  % yes response
cfgExp.respKey = KbName('RightArrow');  % keyboard response
cfgExp.NATAKey = KbName('7&');  % NATA box response
cfgExp.AstonNottKey = KbName('b');  % AU and UoN button box responses #Check for Aston
cfgExp.responses = [cfgExp.NATAKey, cfgExp.AstonNottKey, cfgExp.respKey];

% KB response: '4$' and '7&' are the left and right index fingers of the (5-button) NATA boxes
if cfgExp.MEGLab == 1
    if cfgExp.site == 2
        cfgExp.activeKeys = [cfgExp.quitKey, cfgExp.NATAKey, cfgExp.yesKey, cfgExp.noKey];
    elseif cfgExp.site == 1 || cfgExp.site == 3
        cfgExp.activeKeys = [cfgExp.quitKey, cfgExp.AstonNottKey, cfgExp.yesKey, cfgExp.noKey];
    end
    cfgExp.deviceNum = -1;  % listen to all devices during test/train
else
    cfgExp.activeKeys = [cfgExp.quitKey, cfgExp.respKey, cfgExp.yesKey, cfgExp.noKey];
    cfgExp.deviceNum = -1;  % listen to all devices during test/train
end

% only listen for specific keys
scanList = zeros(1,256);
scanList(cfgExp.activeKeys) = 1;
KbQueueCreate(cfgExp.deviceNum,scanList);  % create queue
KbQueueStart;  % start listening to input
KbQueueFlush;  % clear all keyboard presses so far

end
