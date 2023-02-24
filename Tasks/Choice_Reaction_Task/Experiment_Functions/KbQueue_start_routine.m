function cfgExp = KbQueue_start_routine(cfgExp)
% KbQueue_start_routine(cfgExp)
% Starts KbQueueRoutine for the keyboard to start listening
% A call to KbQueueCheck is required for participants response

KbName('UnifyKeyNames');
cfgExp.quitKey = KbName('ESCAPE');  % quit key
cfgExp.respKeyR = KbName('RightArrow');  % keyboard response female
cfgExp.respKeyL = KbName('LeftArrow');  % keyboard response male
cfgExp.NATAKeyR = KbName('7&');  % NATA box response right
cfgExp.NATAKeyL = KbName('4$');  % NATA box response left
cfgExp.AstonNottKeyR = KbName('1!');  % AU and UoN button box responses for right index #TO BE CHECKED
cfgExp.AstonNottKeyL = KbName('5%');  % AU and UoN button box responses for left index #TO BE CHECKED
cfgExp.yesKey = KbName('y');  % yes response
cfgExp.noKey = KbName('n');  % no key
cfgExp.responses = [cfgExp.NATAKeyR, cfgExp.NATAKeyL, cfgExp.AstonNottKeyR, cfgExp.AstonNottKeyL, cfgExp.respKeyR, cfgExp.respKeyL];

if cfgExp.MEGLab == 1
    cfgExp.activeKeys = [cfgExp.quitKey, cfgExp.NATAKeyR, cfgExp.NATAKeyL, cfgExp.yesKey, cfgExp.noKey];
    cfgExp.deviceNum = -1;  % listen to all devices during test/train
else
    cfgExp.activeKeys = [cfgExp.quitKey, cfgExp.respKeyR, cfgExp.respKeyL, cfgExp.yesKey, cfgExp.noKey];
    cfgExp.deviceNum = -1;  % listen to all devices during test/train
end

% only listen for specific keys
scanList = zeros(1,256);
scanList(cfgExp.activeKeys) = 1;
KbQueueCreate(cfgExp.deviceNum,scanList);  % create queue
KbQueueStart;  % start listening to input
KbQueueFlush;  % clear all keyboard presses so far

end
