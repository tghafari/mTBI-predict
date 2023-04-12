function cfgTxt = txt_collection
% cfgTxt = txt_collection
% collection of all texts used in the experiment

cfgTxt.quitTxt = 'Are you sure you want to abort the experiment? y/n';
cfgTxt.startTxt = 'Are you ready to start? \n Tell the experimenter to start the task when you are ready';
cfgTxt.breakTxt = 'Take a break \n tell the experimenter to continue when you are ready';
cfgTxt.endTxt = 'Thank you :-)';
instr1 = 'First a dot appears at the centre of the screen. \n\n Please look at that dot for the duration of the task.' ;
instr2 = 'Then an arrow will appear below the fixation point. \n\n The arrow shows the button you should press.';
instr3 = 'Please press the corresponding button \n as soon as you see the arrow.';
cfgTxt.instrTxt = {instr1, instr2, instr3};


end