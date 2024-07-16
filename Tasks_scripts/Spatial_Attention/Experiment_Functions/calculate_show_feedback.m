function cfgOutput = calculate_show_feedback(cfgOutput, cfgExp, nstim, blk, cfgScreen, cfgTrigger, cfgEyelink)
% cfgOutput = calculate_show_feedback(cfgOutput, cfgExp, nstim, blk, cfgScreen, cfgTrigger, cfgEyelink)
% calculates performance for each block

FB = cfgOutput.presd((blk-1)*cfgExp.numTrial+1:blk*cfgExp.numTrial) - cfgExp.corrResp((blk-1)*cfgExp.numTrial+1:blk*cfgExp.numTrial);
TPR = sum(FB == 1) ./ length(FB);  % because pressed is stored as 2, TPR = 2 - 1
TNR = sum(FB == 0) ./ length(FB);  % TNR = 0 - 0
FPR = sum(FB == 2) ./ length(FB);  % FPR = 2 - 0
FNR = sum(FB == -1) ./ length(FB);  % FNR = 0 - 1

text = ['Correct = ', num2str((TPR + TNR)*100), '%   False = ', num2str((FPR + FNR)*100), '%'];

Screen('Flip', cfgScreen.window);
cfgOutput.blkEnd(nstim) = send_trigger(cfgTrigger, cfgExp, cfgTrigger.blkEnd, cfgEyelink, 'end of block');

DrawFormattedText(cfgScreen.window, text, 'center', 'center', [cfgScreen.white, cfgScreen.white, cfgScreen.white]);
Screen('Flip', cfgScreen.window);
WaitSecs(3)

end