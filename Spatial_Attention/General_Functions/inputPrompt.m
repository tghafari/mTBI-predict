function ansr = inputPrompt
%ansr = InputPrompt
%  returns the details of subject and data collection in ansr struct
%Sub #,MEG PC subjects code, MEG PC date format, training or test, on what
%computer (MEG or Win)

prompt     = {'Subject Numbed','Subject Code','Date','Train/Task/Test','Testing PC'}; 
dlgtitle   = 'Details';
dims       = [1,30;1,30;1,30;1,30;1,30];
defaultans = {'101','B51A','20201120','test','win'};
answer = inputdlg(prompt,dlgtitle,dims,defaultans);
ansr = cell2struct(answer, {'sub', 'code', 'date', 'task', 'pc'},1);

end

