%% Basic Setup

expBasicSetup  % basic PTB setup and clearing up
%% Input and OS folder preparations

answer = inputPrompt;
filedir = fileDirCreator(answer);

%% Make variables and read in images

cfgExp = varIntro(answer);  % introduce experiment variables
cfgTrigger = triggerIntro;  % introduce triggers
cfgStim = visStimReader(filedir,cfgExp);  % randomly read visual stimuli and cues for all trials
cfgScreen = screenVars(cfgExp);  % introduce visual variables
datapixxSetup(cfgExp, cfgScreen)  % sets up propixx
cfgTxt = txt_collection;  % collection of all texts
%% Screen Setup

[window, windowRect] = PsychImaging('OpenWindow', cfgScreen.scrNum, cfgScreen.black, cfgScreen.fullScrn);  % open an on screen window and color it gray
cfgScreen = screenBscSetup(cfgScreen, window);
%% Visual stimulus and fixation cross characteristics and hardware timing

presentingStr = imgMakeTxture(window, cfgStim);  % make texture for visual stim and cue
cfgScreen = fixDotChar(windowRect, cfgScreen);  % characteristics of fixation dot
cfgScreen = rectVisStimDest(cfgScreen, windowRect);  % destination rectangle to present the stimulus
cfgExp = time2frame(cfgExp, cfgScreen);  % time and frame conversions
cfgTrigger = triggerInit(cfgExp, cfgTrigger);  % initiate triggers
%% Main Experiment

cfgExp = KbQueueStarterRoutine(cfgExp);  % start KbQueu routine
cfgScreen.vbl = Screen('Flip',window);  % get the first VBL
% getReadyTextPresenter(window,black,expDev,condMat); % waits for experimenter's command and gets baseline VBL
%
% % Countdown to start
% countDownToStart(window,cfgScreen)
%
nstim = 0;  % count number of stimuli in total
inTask = 1;  % are we in the task?
for blk = 1:2
    for trl = 1:5
        nstim = nstim + 1;  % count stims presented in total
        
        % beginig of blocks fixation dot
        cfgOutput.strtTmPnt(nstim) = triggerSend(cfgTrigger, cfgExp, cfgTrigger.start);
        dispFixDot(window, cfgScreen, cfgExp, nstim, 1)  % 1 indicated it is ITI
        
        % cue presentation
        cfgOutput = dispCue(window, presentingStr, nstim, cfgScreen, cfgExp, cfgTrigger, cfgOutput);
        
        % ISI with fixation dot presentation
        dispFixDot(window, cfgScreen, cfgExp, nstim, 0);  % 0 indicated it is not ITI (it is ISI)
        
        % present visual stimulus with/without red flash dot
        cfgOutput = dispVisStim(window, presentingStr, nstim, cfgScreen, cfgExp, cfgOutput, cfgStim, cfgTrigger);

        % listen for a response cfgExp
        cfgOutput = responseCollector(cfgExp, cfgOutput, cfgTrigger, nstim, window, cfgTxt, cfgScreen);
         
    end
end


sca

%%
%     %Thank you messeage at the end
%     if blk == 2 %numBlock*length(blockInd)
%         endTextPresenter(window,black)
%         KbQueueStop(partDev);
%         sca
%         break
%     end
%
%     %Rest after each block
%     [blckHistory,~] = restTextPresenter(blckHistory,blk,playerRFT,window,black,expDev,numTrial,trilAud,condMat,0);
%     end
%
%
% sca
