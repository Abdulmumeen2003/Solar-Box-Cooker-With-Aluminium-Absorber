
%% INDEPENDENT ALUMINIUM SOLAR BOX COOKER PREDICTION
% Construction:
% - Black-coated aluminium absorber
% - Sawdust insulation
% - Single glass cover
% - Plywood external box
% - Reflector fixed at 90 degrees
% - No water load
%
% This is a simplified one-node prediction model.
% Weather and thermal parameters are assumed scenario inputs,
% not measured data or experimentally calibrated values.

clear;
clc;
close all;

%% 1. SIMULATION TIME
dt = 10;                     % Time step (seconds)

startHour = 9;
endHour = 16;

t = 0:dt:(endHour-startHour)*3600;
timeHours = startHour + t/3600;
timeMinutes = t/60;

%% 2. ALUMINIUM ABSORBER GEOMETRY
L = 0.50;                    % Length (m)
W = 0.30;                    % Width (m)
thickness = 0.00025;         % Thickness (m)

A = L * W;                   % Absorber/aperture area (m^2)
V = L * W * thickness;       % Aluminium volume (m^3)

%% 3. ALUMINIUM THERMAL PROPERTIES
rho = 2700;                  % Density (kg/m^3)
cp = 900;                    % Specific heat capacity (J/kg.K)

alpha = 0.90;                % Black surface solar absorptivity

mass_plate = rho * V;
C_plate = mass_plate * cp;

%% 4. COOKER CONSTRUCTION ASSUMPTIONS
% These are initial engineering estimates.
% They are not measured properties of the actual cooker.

tau_glass = 0.85;            % Assumed single-glass solar transmission
F_reflector = 1.15;          % Approximate reflector optical contribution

U_effective = 12.0;           % Effective heat-loss coefficient (W/m^2.K)

C_cooker = 1500;             % Estimated additional cooker heat capacity (J/K)

C_total = C_plate + C_cooker;

reflector_angle = 90;        % Fixed reflector angle (degrees)

%% 5. ASSUMED CLEAR-SKY MAIDUGURI WEATHER SCENARIO
% These profiles are illustrative assumptions, not measured weather data.

weatherTime = [9 10 11 12 12.5 13 14 15 16];

weatherIrradiance = [520 720 860 940 950 930 820 650 420];
% Solar irradiance (W/m^2)

weatherAmbient = [33 35 37 38.5 39 39.5 39 37.5 35.5];
% Ambient temperature (degrees C)

G = interp1(weatherTime, weatherIrradiance, ...
    timeHours, 'pchip');

Ta = interp1(weatherTime, weatherAmbient, ...
    timeHours, 'pchip');

windSpeed = 2.0 * ones(size(t));  % Assumed wind speed (m/s)

%% 6. INITIAL CONDITIONS
Tp = zeros(size(t));

% Assume the cooker starts at ambient temperature at 9:00 AM.
Tp(1) = Ta(1);

%% 7. ONE-NODE THERMAL SIMULATION
for k = 1:length(t)-1

    % Solar energy absorbed by the aluminium plate
    Q_solar = alpha * tau_glass * F_reflector * A * G(k);

    % Combined heat loss from the cooker
    Q_loss = U_effective * A * (Tp(k) - Ta(k));

    % Net heat input
    Q_net = Q_solar - Q_loss;

    % Temperature change
    dTdt = Q_net / C_total;

    % Forward Euler numerical integration
    Tp(k+1) = Tp(k) + dTdt * dt;

end

%% 8. PERFORMANCE RESULTS
[peakTemp, peakIndex] = max(Tp);

peakTimeMinutes = timeMinutes(peakIndex);
peakClockTime = timeHours(peakIndex);

temperatureAt4PM = Tp(end);
temperatureRise = peakTemp - Tp(1);

fprintf('\n');
fprintf('ALUMINIUM SOLAR BOX COOKER PREDICTION\n');
fprintf('--------------------------------------\n');

fprintf('Absorber material: Black-coated aluminium\n');
fprintf('Reflector angle: %.0f degrees\n', reflector_angle);
fprintf('Insulation: Sawdust\n');
fprintf('Glass cover: Single glazing\n');
fprintf('External box: Plywood\n');
fprintf('Water load: None\n\n');

fprintf('Aluminium plate mass: %.4f kg\n', mass_plate);
fprintf('Aluminium plate heat capacity: %.2f J/K\n', C_plate);
fprintf('Total assumed thermal capacity: %.2f J/K\n', C_total);

fprintf('\nInitial plate temperature: %.2f deg C\n', Tp(1));
fprintf('Peak plate temperature: %.2f deg C\n', peakTemp);
fprintf('Time to peak: %.2f minutes\n', peakTimeMinutes);
fprintf('Peak clock time: %.2f hours\n', peakClockTime);
fprintf('Temperature at 4 PM: %.2f deg C\n', temperatureAt4PM);
fprintf('Maximum temperature rise: %.2f deg C\n', temperatureRise);

%% 9. TEMPERATURE PREDICTION GRAPH
figure('Color','w');

plot(timeHours, Tp, 'r-', 'LineWidth', 2.5);
hold on;

plot(timeHours, Ta, 'b--', 'LineWidth', 1.8);

plot(peakClockTime, peakTemp, 'ko', ...
    'MarkerFaceColor','k', 'MarkerSize',7);

xlabel('Time of day (hours)');
ylabel('Temperature (deg C)');

title('Independent Predicted Temperature of Aluminium Absorber');

legend('Predicted aluminium temperature', ...
       'Ambient temperature', ...
       'Predicted peak temperature', ...
       'Location','best');

grid on;
xlim([startHour endHour]);

%% 10. SOLAR IRRADIANCE GRAPH
figure('Color','w');

plot(timeHours, G, 'LineWidth', 2);

xlabel('Time of day (hours)');
ylabel('Solar irradiance (W/m^2)');

title('Assumed Clear-Sky Solar Irradiance Profile');

grid on;
xlim([startHour endHour]);

%% 11. AMBIENT TEMPERATURE GRAPH
figure('Color','w');

plot(timeHours, Ta, 'LineWidth', 2);

xlabel('Time of day (hours)');
ylabel('Ambient temperature (deg C)');

title('Assumed Ambient Temperature Profile');

grid on;
xlim([startHour endHour]);

%% 12. EXPORT PREDICTION DATA
Results = table( ...
    timeHours(:), ...
    timeMinutes(:), ...
    G(:), ...
    Ta(:), ...
    windSpeed(:), ...
    Tp(:), ...
    'VariableNames', { ...
    'Time_hours', ...
    'Elapsed_time_minutes', ...
    'Solar_irradiance_W_m2', ...
    'Ambient_temperature_C', ...
    'Assumed_wind_speed_m_s', ...
    'Predicted_aluminium_temperature_C'});

writetable(Results, ...
    'aluminium_improved_prediction_timeseries.csv');

Summary = table( ...
    peakTemp, ...
    peakTimeMinutes, ...
    peakClockTime, ...
    temperatureAt4PM, ...
    temperatureRise, ...
    U_effective, ...
    tau_glass, ...
    F_reflector, ...
    C_cooker, ...
    'VariableNames', { ...
    'Peak_temperature_C', ...
    'Peak_elapsed_minutes', ...
    'Peak_clock_time_hours', ...
    'Temperature_at_4PM_C', ...
    'Maximum_temperature_rise_C', ...
    'Effective_heat_loss_W_m2K', ...
    'Glass_transmission', ...
    'Reflector_factor', ...
    'Additional_cooker_heat_capacity_J_K'});

writetable(Summary, ...
    'aluminium_improved_prediction_summary.csv');

fprintf('\nPrediction files successfully exported.\n');
