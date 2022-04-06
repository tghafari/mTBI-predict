function countDownToStart(window,cfgScreen)
% countDownToBegin(window,cfgScreen)
% counts down to start the program
% window -> output of PsychImaging('OpenWindiw',...)
% color -> font color

cntdwnTxt={'Go','Set','Ready'};

for cntr = length(cntdwnTxt):-1:1
    DrawFormattedText(window,cntdwnTxt{cntr},'center','center',cfgScreen.white);  % opens message
    Screen('Flip',window);
    WaitSecs(.95)
end
end
