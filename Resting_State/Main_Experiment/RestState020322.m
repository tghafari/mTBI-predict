%% Basic Setup

cfgEyelink = basic_setup_experiment;  % basic PTB setup and clearing up
%% Input and OS folder preparations

cfgExp.answer = prompt_input;
cfgFile = create_file_directory(cfgExp);
%% Make variables and read in images

cfgExp = initialise_exp_variables(cfgExp);  % introduce experiment variables
cfgTrigger = introduce_triggers;  % introduce triggers
cfgScreen = initialise_screen_variables(cfgExp);  % introduce visual variables
setup_datapixx(cfgExp, cfgScreen)  % sets up propixx
cfgTxt = txt_collection;  % collection of all texts
%% Screen Setup

[cfgScreen.window, cfgScreen.windowRect] = PsychImaging('OpenWindow', cfgScreen.scrNum, cfgScreen.black, cfgScreen.fullScrn);  % open an on screen window and color it gray
cfgScreen = basic_setup_screen(cfgScreen);
cfgEyelink = initialise_eyelink(cfgFile, cfgEyelink, cfgScreen);  % initialise eyelink
cfgScreen = fix_dot_properties(cfgScreen);  % characteristics of fixation dot
cfgExp = time2frame(cfgExp, cfgScreen);  % time and frame conversions
cfgTrigger = initialise_trigger_port(cfgExp, cfgTrigger);  % initiate triggers
%% Main Experiment

cfgExp = KbQueue_start_routine(cfgExp);  % start KbQueu routine
cfgScreen.vbl = Screen('Flip',cfgScreen.window);  % get the first VBL
draw_myText(cfgScreen, cfgExp, cfgTxt.startTxt);
cfgOutput.strtTmPnt = send_trigger(cfgTrigger, cfgExp, cfgTrigger.start);
display_fixation_dot(cfgScreen, cfgExp);  % 1 indicated it is ITI
draw_myText(cfgScreen, cfgExp, cfgTxt.endTxt);
cfgOutput = cleanup(cfgFile, cfgExp, cfgScreen, cfgEyelink, cfgOutput, cfgTrigger);
