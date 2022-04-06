function endTextPresenter(window,color)
%ENDTEXTPRESENTER Summary of this function goes here
%   thank you message at the end of the program

endTxt = 'Thank You! :-)';
Screen('Flip',window);
DrawFormattedText(window,endTxt,'center','center',color); % Opens message
Screen('Flip',window);
WaitSecs(1);
    
end

