# brew

Raspberry Pi based brewing controller.\
Written for and tested on a Raspberry Pi 4B running DietPi 9.9, but might work on other combinations.\
Requires docker and docker compose to be installed.
Runs on http://localhost:80. Port can be changed in the `docker-compose` file.

PID logic copied from [hirschmann/pid-autotune](https://github.com/hirschmann/pid-autotune).

## GPIO pins

- GPIO04 - Data channel of a DS18B20 temperature sensor
- GPIO12 - Fan PWM signal
- GPIO13 - PWM signal to drive the heater through a solid state relay
- GPIO24 - Positive voltage for a buzzer
- GPIO26 - Fan tachometer input
- GPIO27 - Pump relay signal

More details about the connections (necessary components and wiring) can be found in the `electronics` sub-directory (open with KiCad).

## Configuring temperature sensor

Add 1-Wire to boot configuration:

```
sudo echo -e "\ndtoverlay=w1-gpio\n" >> /boot/config.txt
```

Reboot:

```
sudo reboot
```

Add modules:

```
sudo modprobe w1-gpio
sudo modprobe w1-therm
```

## Installation

Configure DS18B20 if not alread configured (see previous section).\
Log in to your Pi and navigate to the directory you want to save the application to.\
Download the `docker-compose.yml` file:

```
wget https://raw.githubusercontent.com/andresrobam/brew/refs/heads/master/docker-compose.yml
```

Create a sub-directory for the configuration:

```
mkdir -p server/config
```

Start the application:

```
docker compose up -d
```

## Local build

To build and run locally:

```
docker compose -f docker-compose-local.yml up -d
```
