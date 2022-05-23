function calculate_show_feedback(cfgOutput, cfgExp, blk, cfgScreen)
% calculate_show_feedback(cfgOutput, cfgExp, blk, cfgScreen)
% calculates performance for each block

FB = strcmp(cfgOutput.keyName((blk-1)*cfgExp.numTrial+1:blk*cfgExp.numTrial), ...
     cfgExp.corrResp((blk-1)*cfgExp.numTrial+1:blk*cfgExp.numTrial));

text = ['Correct = ', num2str(sum(FB))];

Screen('Flip', cfgScreen.window);
DrawFormattedText(cfgScreen.window, text, 'center', 'center', [cfgScreen.white, cfgScreen.white, cfgScreen.white]);
Screen('Flip', cfgScreen.window);
WaitSecs(1)

end