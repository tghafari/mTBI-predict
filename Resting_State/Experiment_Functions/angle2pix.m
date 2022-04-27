function pixel = angle2pix(cfgScreen,angle)
% pixel = angle2pix(cfgScreen,angle)
% converts visual angles in degrees to pixels.
% cfgScreen.distance (distance from screen in cm)
% cfgScreen.dispSize.width (width of screen in mm)
% cfgScreen.resolution.width (number of pixels of display in horizontal direction)

% Warning: assumes isotropic (square) pixels

pixSize = (cfgScreen.dispSize.width./10)/cfgScreen.resolution.width;   % how many mm is one pixel? mm/pix
sz = 2 * cfgScreen.distance * tan(pi * angle/ (2 * 180));  % distance in cm
pixel = round(sz/pixSize);   % pixel

end




