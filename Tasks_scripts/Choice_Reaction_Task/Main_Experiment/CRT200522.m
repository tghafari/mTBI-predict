%% Basic Setup
clear; close all; sca; fclose('all');  % EVALUATE BEFORE RUN. This should be outside of function, otherwise might not work!
cfgEyelink = basic_setup_experiment;  % basic PTB setup and clearing up
%% Input and OS folder preparations

cfgExp.answer = prompt_input;
cfgFile = create_file_directory(cfgExp);
%% Make variables and read in images

[cfgExp, cfgOutput] = initialise_exp_variables(cfgExp);  % introduce experiment variables
cfgTrigger = introduce_triggers;  % introduce triggers
cfgCue = initialise_cue_variables;
[cfgCue, cfgExp, cfgTrigger] = read_cue(cfgFile, cfgExp, cfgCue, cfgTrigger);  % randomly read visual stimuli and cues for all trials
cfgScreen = initialise_screen_variables(cfgExp);  % introduce visual variables
setup_datapixx(cfgExp, cfgScreen)  % sets up propixx
cfgTxt = txt_collection;  % collection of all texts
%% Screen Setup

[cfgScreen.window, cfgScreen.windowRect] = PsychImaging('OpenWindow', cfgScreen.scrNum, cfgScreen.backgroundColor, cfgScreen.fullScrn);  % open an on screen window and color it gray
cfgScreen = basic_setup_screen(cfgScreen);
cfgEyelink = initialise_eyelink(cfgFile, cfgEyelink, cfgScreen, cfgExp);  % initialise eyelink
%% Visual stimulus and fixation cross characteristics and hardware timing

cfgScreen = fix_dot_properties(cfgScreen);  % characteristics of fixation dot
cfgExp = time2frame(cfgExp, cfgScreen);  % time and frame conversions
cfgCue = cue_properties(cfgScreen, cfgCue);  % destination rectangle to present the cue
presentingStr = make_texture_images(cfgScreen, cfgCue, cfgExp);  % make texture for cue
cfgTrigger = initialise_trigger_port(cfgExp, cfgTrigger);  % initiate triggers
%% Main Experiment

cfgExp = KbQueue_start_routine(cfgExp);  % start KbQueue routine
cfgScreen.vbl = Screen('Flip',cfgScreen.window);  % get the first VBL
cfgOutput.vbl = cfgScreen.vbl;  % put first vbl into cfgOutput as well
showInstructions(cfgScreen, cfgTxt, cfgExp, presentingStr, cfgCue)
cfgOutput = draw_myText(cfgScreen, cfgExp, cfgTxt.startTxt, cfgTxt, cfgOutput, cfgTrigger, cfgFile, cfgEyelink, cfgCue);

nstim = 0;  % count number of stimuli in total
for blk = 1:cfgExp.numBlock
    cfgOutput.blkStrtTmPnt(blk) = send_trigger(cfgTrigger, cfgExp, cfgTrigger.blkNum(blk), cfgEyelink, sprintf('block n. %d', blk));

    for trl = 1:cfgExp.numTrial
        nstim = nstim + 1;  % count stims presented in total
        cfgOutput.trlStrtTmPnt(nstim) = send_trigger(cfgTrigger, cfgExp, cfgTrigger.trialStart, cfgEyelink, 'trial start');

        if ~cfgExp.catchTrial(nstim)
            % ISI with fixation dot presentation
            display_fixation_dot(cfgScreen, cfgExp);

            % cue presentation
            cfgOutput = display_cue(presentingStr, nstim, cfgCue, cfgScreen, cfgExp, cfgTrigger, cfgOutput, cfgEyelink);

            % listen for a response
            cfgOutput = response_collector(cfgExp, cfgOutput, cfgTrigger, nstim, cfgTxt, cfgScreen, cfgFile, cfgEyelink, cfgCue);

        elseif cfgExp.catchTrial(nstim) % catch trial
            cfgOutput.catchTmPnt(nstim) = send_trigger(cfgTrigger, cfgExp, cfgTrigger.catchTrial, cfgEyelink, 'catch trial');
            cfgOutput.cueOnTmPnt(nstim) = cfgOutput.catchTmPnt(nstim);
            
            % only present fixation dot for catch trials
            display_fixation_dot(cfgScreen, cfgExp)
            
            % listen for a response
            cfgOutput = response_collector(cfgExp, cfgOutput, cfgTrigger, nstim, cfgTxt, cfgScreen, cfgFile, cfgEyelink, cfgCue);
        end

    end

    cfgOutput = calculate_show_feedback(cfgOutput, cfgExp, nstim, blk, cfgScreen, cfgTrigger, cfgEyelink);
    if blk ~= cfgExp.numBlock
        cfgOutput = draw_myText(cfgScreen, cfgExp, cfgTxt.breakTxt, cfgTxt, cfgOutput, cfgTrigger, cfgFile, cfgEyelink, cfgCue);
    end
end

cfgOutput = draw_myText(cfgScreen, cfgExp, cfgTxt.endTxt, cfgTxt, cfgOutput, cfgTrigger, cfgFile, cfgEyelink, cfgCue);
cfgOutput = cleanup(cfgFile, cfgExp, cfgScreen, cfgEyelink, cfgOutput, cfgTrigger, cfgTxt, cfgCue);
