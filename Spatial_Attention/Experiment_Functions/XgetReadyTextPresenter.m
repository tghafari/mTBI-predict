function vbl = getReadyTextPresenter(window,color,experDevCod,condMat)
%getReadyTextPresenter(window,color,respDevCod)
%window => ouputted from PsychImaging
%color => the color of text
%experDevCod => the code of response device (external keyboard=>9 internal
%keyboard=>3) -- should be the experimenter's device not the participant's
%condMat -> the main condition matrix

blockTypTxt={'Auditory Regular \n Visual Irregular','Auditory Irregular \n Visual Regular','Auditory Irregular \n Visual Irregular'};
nxtBlockTxt=['This block is: \n' blockTypTxt{condMat(1,1)}];
readyTxt = 'Get ready. Sit still. The experiment will start shortly';

Screen('Flip',window);
DrawFormattedText(window,nxtBlockTxt,'center','center',color); % Opens message
Screen('Flip',window);
WaitSecs(0.03*60);

Screen('Flip',window);
DrawFormattedText(window,readyTxt,'center','center',color); % Opens message
Screen('Flip',window);

KbStrokeWait(experDevCod);
WaitSecs(.05)

vbl = Screen('Flip',window); %baseline vbl
end

