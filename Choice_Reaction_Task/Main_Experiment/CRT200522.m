%% Basic Setup

cfgEyelink = basic_setup_experiment;  % basic PTB setup and clearing up
%% Input and OS folder preparations

cfgExp.answer = prompt_input;
cfgFile = create_file_directory(cfgExp);
%% Make variables and read in images

cfgExp = initialise_exp_variables(cfgExp);  % introduce experiment variables
cfgTrigger = introduce_triggers;  % introduce triggers
cfgCue = initialise_cue_variables;
cfgCue = read_cue(cfgFile, cfgExp, cfgCue);  % randomly read visual stimuli and cues for all trials
cfgScreen = initialise_screen_variables(cfgExp);  % introduce visual variables
setup_datapixx(cfgExp, cfgScreen)  % sets up propixx
cfgTxt = txt_collection;  % collection of all texts
%% Screen Setup

[cfgScreen.window, cfgScreen.windowRect] = PsychImaging('OpenWindow', cfgScreen.scrNum, cfgScreen.backgroundColor, cfgScreen.fullScrn);  % open an on screen window and color it gray
cfgScreen = basic_setup_screen(cfgScreen);
cfgEyelink = initialise_eyelink(cfgFile, cfgEyelink, cfgScreen);  % initialise eyelink
%% Visual stimulus and fixation cross characteristics and hardware timing

cfgScreen = fix_dot_properties(cfgScreen);  % characteristics of fixation dot
cfgExp = time2frame(cfgExp, cfgScreen);  % time and frame conversions
cfgCue = cue_properties(cfgScreen, cfgCue);  % destination rectangle to present the cue
presentingStr = make_texture_images(cfgScreen, cfgCue, cfgExp);  % make texture for cue
cfgTrigger = initialise_trigger_port(cfgExp, cfgTrigger);  % initiate triggers
%% Main Experiment

cfgExp = KbQueue_start_routine(cfgExp);  % start KbQueu routine
cfgScreen.vbl = Screen('Flip',cfgScreen.window);  % get the first VBL
draw_myText(cfgScreen, cfgExp, cfgTxt.startTxt);

nstim = 0;  % count number of stimuli in total
for blk = 1:cfgExp.numBlock
    for trl = 1:cfgExp.numTrial
        nstim = nstim + 1;  % count stims presented in total
        
        % beginig of blocks fixation dot
        cfgOutput.strtTmPnt(nstim) = send_trigger(cfgTrigger, cfgExp, cfgTrigger.start);
        display_fixation_dot(cfgScreen, cfgExp)
        
        if ~cfgExp.catchTrial(nstim)
        % cue presentation
        cfgOutput = display_cue(presentingStr, nstim, cfgCue, cfgScreen, cfgExp, cfgTrigger, cfgOutput);
        
        % ISI with fixation dot presentation
        display_fixation_dot(cfgScreen, cfgExp); 
              
        % listen for a response
        cfgOutput = response_collector(cfgExp, cfgOutput, cfgTrigger, nstim, cfgTxt, cfgScreen, cfgFile, cfgEyelink);
        end

    end
    calculate_show_feedback(cfgOutput, cfgExp, blk, cfgScreen);
    cfgOutput = draw_myText(cfgScreen, cfgExp, text, cfgTxt, cfgOutput, cfgTrigger, cfgFile, cfgEyelink);
    
end

cfgOutput = draw_myText(cfgScreen, cfgExp, text, cfgTxt, cfgOutput, cfgTrigger, cfgFile, cfgEyelink);
cfgOutput = cleanup(cfgFile, cfgExp, cfgScreen, cfgEyelink, cfgOutput, cfgTrigger);
