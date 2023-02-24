function KbQueueDemo(deviceIndex)
%% KbQueueDemo([deviceIndex])
% Shows how to detect when the user has pressed a key.
% See KbQueueCheck, KbQueueWait, KbName, KbCheck, KbWait, GetChar, CharAvail.
%
% The KbQueueXXX functions are low-level like KbCheck and KbWait, but, like
% GetChar/CharAvail, they use a queue so that brief events can be captured.
% 
% Like GetChar/CharAvail, KbQueueXXX functions may be used
% asychronously - the OS will pick up the character whether your code
% is currently looking for it or not so long as the queue has already been 
% created(using KbQueueCreate) and started (using KbQueueStart).
%
% Unlike GetChar/CharAvail, KbQueueXXX functions can detect isolated presses
% of modifier keys. Also, the times of key presses should be more accurate than
% those associated with GetChar/CharAvail or with KbCheck and the timebase is
% the same as that returned by GetSecs (unlike GetChar/CharAvail).
%
% The first four demos here are analogous to those in KbDemo.m

% Roger Woods, November, 2007

% 11/03/07  rpw Wrote demos 1-5
% 05/21/12  mk  Add event buffer test to demo 5.
% 01/31/16  mk  Suppress keypress spilling via ListenChar(-1);
% 08/30/16  dcn Add exercising all options of KbQueueWait

if nargin < 1
  deviceIndex = [];
end

% Enable unified mode of KbName, so KbName accepts identical key names on
% all operating systems:
KbName('UnifyKeyNames');

% Prevent spilling of keystrokes into console:
ListenChar(-1);

%% Part 4
function KbQueueDemoPart4(deviceIndex)
% Control a screen spot with the keyboard.

% Here are the parameters for this demo.
spotRadius = 15; % The radius of the spot.
% rotationRadius = 200; % The radius of the rotation.
% initialRotationAngle = 3 * pi / 2; % The initial rotation angle in radians.

    % Removes the blue screen flash and minimize extraneous warnings.
    Screen('Preference', 'VisualDebugLevel', 3);
    Screen('Preference', 'SuppressAllWarnings', 1);

    % Find out how many screens and use largest screen number.
    whichScreen = max(Screen('Screens'));
    
    % Open a new window.
    [ window, windowRect ] = Screen('OpenWindow', whichScreen);
    
    % Set colors.
    black = BlackIndex(window);
    
%     % Set keys.
%     rightKey = KbName('RightArrow');
%     leftKey = KbName('LeftArrow');
%     escapeKey = KbName('ESCAPE');
%     
%     keysOfInterest=zeros(1,256);
%     keysOfInterest(rightKey)=1;
%     keysOfInterest(leftKey)=1;
%     keysOfInterest(escapeKey)=1;
    
    % Use the parameters.
    cfgScreen.spotCentre = cfgScreen.centre - (upperLimit - lowerLimit)/2;  % -100 coordinates of fixation dot- normally above center
    cfgScreen.spotSize = 1;  % size of fixation dot in visual degrees
    cfgScreen.spotRect = [cfgScreen.spotCentre - angle2pix(cfgScreen, cfgScreen.spotSize./2)...
    , cfgScreen.spotCentre + angle2pix(cfgScreen, cfgScreen.spotSize./2)];  % rect for fixation dot 
    cfgScreen.spotColor = [1 1 1];  % color of fixation dot in rgb (white)

    
    % Set up the timer.
%     startTime = now;
    durationInSeconds = 60 * 2;
    numberOfSecondsRemaining = durationInSeconds;
    
    KbQueueCreate(deviceIndex, keysOfInterest);
    KbQueueStart(deviceIndex);
    
    % Loop while there is time.
    while numberOfSecondsRemaining > 0
            
%             xOffset = rotationRadius * cos(rotationAngle);
%             yOffset = rotationRadius * sin(rotationAngle);
%             offsetCenteredspotRect = OffsetRect(centeredspotRect, xOffset, yOffset);
            Screen('FillOval', window, cfgScreen.spotColor, cfgScreen.spotRect);
            Screen('Flip', window);
            
            % Note that holding down the arrow key without releasing it will
            % not cause he dot to keep moving since this generates only a
            % single key press event (compare to comparable demo in KbDemo.m)
            %
            % We could work around this by making note of whether the key
            % has been released using the call:
            % [pressed, firstPress, firstRelease, lastPress, lastRelease]= KbQueueCheck(deviceIndex)
            % and noting whether lastRelease is more recent than lastPress for
            % the keys of interest, tracking the status across loop iterations.
            % However,it would be easier to use KbCheck, which reflects the
            % current status of the key directly (see KbDemo.m)
            
            [ pressed, firstPress]=KbQueueCheck(deviceIndex);
           
            if pressed
                if firstPress(rightKey)
                    if centeredspotRect < upperLimit
                        centeredspotRect = centeredspotRect + 0.1;
                    else
                        centeredspotRect = upperLimit;
                    end
                elseif firstPress(leftKey)
                    if centeredspotRect > lowerLimit
                        centeredspotRect = centeredspotRect - 0.1;
                    else
                        centeredspotRect = lowerLimit;
                    end
                elseif firstPress(escapeKey)
                    break;
                end
            end
            
    end
    sca;
    KbQueueRelease(deviceIndex);  % Note that KbQueueRelease is also in the catch clause


end

