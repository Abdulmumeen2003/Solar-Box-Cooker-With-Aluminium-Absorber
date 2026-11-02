
#include <Arduino.h>
#include <DHT.h>
#include <max6675.h>
#include <math.h>

// DHT22
#define DHTPIN 2
#define DHTTYPE DHT22

// MAX6675: CLK, CS, SO
const int thermoCLK = 10;
const int thermoCS  = 9;
const int thermoSO  = 11;

DHT dht(DHTPIN, DHTTYPE);
MAX6675 thermocouple(thermoCLK, thermoCS, thermoSO);

void setup() {
    Serial.begin(9600);
    dht.begin();

    Serial.println(F("Solar Box Cooker Sensor Test"));
    Serial.println(F("Time_s,Probe_C,Ambient_C,Humidity_pct,Status"));

    delay(2000);
}

void loop() {
    float probeTemp = thermocouple.readCelsius();
    float ambientTemp = dht.readTemperature();
    float humidity = dht.readHumidity();

    bool dhtOK = !isnan(ambientTemp) && !isnan(humidity);
    bool probeOK = !isnan(probeTemp);

    Serial.print(millis() / 1000.0, 1);
    Serial.print(',');

    if (probeOK) Serial.print(probeTemp, 2);
    else Serial.print(F("ERROR"));

    Serial.print(',');

    if (dhtOK) Serial.print(ambientTemp, 2);
    else Serial.print(F("ERROR"));

    Serial.print(',');

    if (dhtOK) Serial.print(humidity, 2);
    else Serial.print(F("ERROR"));

    Serial.print(',');

    if (!dhtOK && !probeOK) {
        Serial.println(F("BOTH_SENSORS_ERROR"));
    } else if (!dhtOK) {
        Serial.println(F("DHT_ERROR"));
    } else if (!probeOK) {
        Serial.println(F("THERMOCOUPLE_ERROR"));
    } else {
        Serial.println(F("READINGS_VALID"));
    }

    delay(2500);
}