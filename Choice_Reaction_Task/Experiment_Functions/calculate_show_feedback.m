function cfgOutput = calculate_show_feedback(cfgOutput, cfgExp, blk, cfgScreen, cfgTrigger, cfgEyelink)
% cfgOutput = calculate_show_feedback(cfgOutput, cfgExp, blk, cfgScreen, cfgTrigger, cfgEyelink)
% calculates performance for each block

cfgOutput.blkEnd(nstim) = send_trigger(cfgTrigger, cfgExp, cfgTrigger.blkEnd, cfgEyelink, 'end of block');

FB = strcmp({cfgOutput.keyName{(blk-1)*cfgExp.numTrial+1:blk*cfgExp.numTrial}}, ...
     {cfgExp.corrResp{(blk-1)*cfgExp.numTrial+1:blk*cfgExp.numTrial, 2}}); %#ok<*CCAT1>

text = ['Correct = ', num2str(round(100 * sum(FB) / cfgExp.numTrial)), '%'];

Screen('Flip', cfgScreen.window);
DrawFormattedText(cfgScreen.window, text, 'center', 'center', [cfgScreen.white, cfgScreen.white, cfgScreen.white]);
Screen('Flip', cfgScreen.window);
WaitSecs(1)

end