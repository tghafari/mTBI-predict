function ansr = prompt_input
%ansr = prompt_input
%  returns the details of subject and data collection in ansr struct
%Sub #,MEG PC subjects code, MEG PC date format, training or test, on what
%computer (MEG or Win)
% Subject codes-> T: testing, B: actual data

prompt     = {'Site', 'Subject Code', 'Session', 'Task', 'Run', 'Train/Task/Test', 'Testing PC'}; 
dlgtitle   = 'Details';
dims       = [1, 30; 1, 30; 1, 30; 1, 30; 1, 30; 1, 30; 1, 30];
defaultans = {'Birmingham', 'T101', '01', 'CRT', '01', 'test', 'win'};
answer = inputdlg(prompt, dlgtitle, dims, defaultans);
ansr = cell2struct(answer, {'site', 'sub', 'ses', 'task', 'run', 'test', 'pc'}, 1);

end

