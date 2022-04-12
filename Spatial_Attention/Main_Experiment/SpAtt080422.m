%% Basic Setup

cfgEyelink = basic_setup_experiment;  % basic PTB setup and clearing up
%% Input and OS folder preparations

cfgExp.answer = prompt_input;
cfgFile = create_file_directory(cfgExp);
%% Make variables and read in images

cfgExp = initialise_variables(cfgExp);  % introduce experiment variables
cfgTrigger = introduce_triggers;  % introduce triggers
cfgStim = read_visual_stim(cfgFile,cfgExp);  % randomly read visual stimuli and cues for all trials
cfgScreen = screen_variables(cfgExp);  % introduce visual variables
setup_datapixx(cfgExp, cfgScreen)  % sets up propixx
cfgTxt = txt_collection;  % collection of all texts
%% Screen Setup

[window, windowRect] = PsychImaging('OpenWindow', cfgScreen.scrNum, cfgScreen.black, cfgScreen.fullScrn);  % open an on screen window and color it gray
cfgScreen = basic_setup_screen(cfgScreen, window);
% cfgEyelink = initialise_eyelink(cfgFile, cfgEyelink, cfgScreen);  % initialise eyelink
%% Visual stimulus and fixation cross characteristics and hardware timing

presentingStr = make_texture_images(window, cfgStim);  % make texture for visual stim and cue
cfgScreen = fix_dot_properties(windowRect, cfgScreen);  % characteristics of fixation dot
cfgExp = time2frame(cfgExp, cfgScreen);  % time and frame conversions
cfgScreen = visual_stim_properties(cfgScreen, cfgExp, windowRect);  % destination rectangle to present the stimulus
cfgTrigger = initialise_triggers(cfgExp, cfgTrigger);  % initiate triggers
%% Main Experiment

cfgExp = KbQueue_start_routine(cfgExp);  % start KbQueu routine
cfgScreen.vbl = Screen('Flip',window);  % get the first VBL
% getReadyTextPresenter(window,black,expDev,condMat); % waits for experimenter's command and gets baseline VBL
%
% % Countdown to start
% countDownToStart(window,cfgScreen)
%
nstim = 0;  % count number of stimuli in total

for blk = 1:2
    for trl = 1:5
        nstim = nstim + 1;  % count stims presented in total
        
        % beginig of blocks fixation dot
        cfgOutput.strtTmPnt(nstim) = send_trigger(cfgTrigger, cfgExp, cfgTrigger.start);
        display_fixation_dot(window, cfgScreen, cfgExp, nstim, 1)  % 1 indicated it is ITI
        
        % cue presentation
        cfgOutput = display_cue(window, presentingStr, nstim, cfgScreen, cfgExp, cfgTrigger, cfgOutput);
        
        % ISI with fixation dot presentation
        display_fixation_dot(window, cfgScreen, cfgExp, nstim, 0);  % 0 indicated it is not ITI (it is ISI)
        
        % present visual stimulus with/without red flash dot
        cfgOutput = display_visual_stim(window, presentingStr, nstim, cfgScreen, cfgExp, cfgOutput, cfgStim, cfgTrigger);

        % listen for a response cfgExp
        cfgOutput = response_collector(cfgExp, cfgOutput, cfgTrigger, nstim, window, cfgTxt, cfgScreen);
         
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
