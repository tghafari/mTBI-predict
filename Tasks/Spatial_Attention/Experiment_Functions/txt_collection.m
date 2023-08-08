function cfgTxt = txt_collection
% cfgTxt = txt_collection
% collection of all texts used in the experiment

cfgTxt.quitTxt = 'Are you sure you want to abort the experiment? y/n';
cfgTxt.startTxt = 'Are you ready to start? \n Tell the experimenter to start the task when you are ready';
cfgTxt.breakTxt = 'Take a break \n tell the experimenter to continue when you are ready';
cfgTxt.endTxt = 'Thank you :-) \n\n Please stay still while we save your data.';
instr1 = 'First a dot appears in the centre of the screen. \n\n Please look at that dot for the duration of the task.' ;
instr2 = 'Then an arrow will appear below the fixation point. \n\n The arrow shows the direction to which you should attend.';
instr3 = 'Then you will see two circular moving gratings \n on the two sides of the screen. \n\n Please attend to the grating that was cued by the arrow \n without moving your eyes.';
instr4 = 'A red dot will appear in the centre of the attended circle. \n\n Please press the right index finger as soon as you see the dot. \n\n Please put down the left button box.';
cfgTxt.instrTxt = {instr1, instr2, instr3, instr4};

end