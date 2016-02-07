clear
close all

% Creates test VAWT geometry file

% Add geom creation scripts to path
path(path,'~/CACTUS/CACTUS-tools/geometry/CreateGeom');

% Params
R = 0.5375*3.28084;         % Center radius (ft)
R_m = 0.5375;               % radius in m at midspan
HR = 0.807/R_m;             % Height to radius ratio
eta = 0.5;                  % Blade mount point ratio (mount point behind leading edge as a fraction of chord)
NBlade = 3;                 % number of blades
NBElem = 20;                % number of blade elements
NStrut = 3;                 % number of struts
NSElem = 10;                % number of strut elements
CRs = 0.06/R_m;             % strut chord to radius
TCs = 0.21;                 % strut thickness to chord

CT = 0.040/R_m;             % Root chord to radius
CR = 0.067/R_m;             % Tip chord to radius
CRr_1 = linspace(CR,CT,(NBElem/2)+1);
CRr_2 = linspace(CT,CR,(NBElem/2)+1);
CRr(1,1:NBElem/2) = CRr_2(1,1:NBElem/2);
CRr(1,((NBElem/2)+1):(NBElem+1)) = CRr_1;


% Output filename
FN = 'config/geom/RM2_Geom.geom';

% Plot data?
PlotTurbine = 0;

% Convert
dToR = pi/180;
FlipN = 1;

% Create basic parabolic blade VAWT
% CreateTurbine(NBlade,NBElem,NStrut,NSElem,RefR,RotN,RotP,RefAR,Type,varargin)
Type = 'VAWT';
BShape = 0;
T = CreateTurbine(NBlade,NBElem,NStrut,NSElem,R,[],[],[],Type,1,CRr,HR,eta,BShape,CRs,TCs);

% Write geom file
WriteTurbineGeom(FN,T);

% Plot if desired
if PlotTurbine

    % Plot animated turbine rotation
    XLim=[-2,2];
    YLim=[0,2];
    ZLim=[-2,2];

    % Plot controls
    PlotVec=0;
    SFVec=.5;
    Trans=.5;

    hf=figure(1);
    set(hf,'Position',[303   124   956   610])
    set(gca,'Position',[5.2743e-002  5.1245e-002  8.9979e-001  8.8141e-001])
    set(gca,'CameraPosition',[-52.1999   30.4749   62.2119])
    set(gca,'CameraUpVector',[1.8643e-001  9.7433e-001 -1.2615e-001])
    set(gca,'CameraViewAngle',6.3060e+000)
    grid on
    set(gcf,'Color','white');
    % hl=light('Position',[-1,0,0]); % Not compatible with octave
    set(gca,'Color','white');
    set(gca,'DataAspectRatio',[1,1,1])
    set(gca,'XLim',XLim,'YLim',YLim,'ZLim',ZLim)

    HIn=[];
    PhasePlot=linspace(0,2*pi,150);
    for i=1:length(PhasePlot)
       H=PlotTurbineGeom(T,hf,PhasePlot(i),HIn,Trans,PlotVec,SFVec);
       HIn=H;
       pause(.01);
    end

end
