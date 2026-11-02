# Firmware Source

`main.cpp` contains the Arduino application. It initializes the DHT22 and MAX6675 interfaces, reads probe temperature, ambient temperature and relative humidity, and streams comma-separated readings with a sensor-status field over the serial connection. The source pin assignments are documented in the project-level README.
