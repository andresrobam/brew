# brew

Raspberry Pi based brewing controller.\
Written for and tested on a Raspberry Pi 4B running DietPi 9.9, but might work on other combinations.\
Requires docker and docker compose to be installed.
Runs on http://localhost:80. Port can be changed in the `docker-compose` file.

PID logic copied from [hirschmann/pid-autotune](https://github.com/hirschmann/pid-autotune).

## Issues

Fan tachometer signal reading does not work as intended and is hidden in the UI. Will be fixed in a future revision. \
Transistor footprints on the PCB have their pads very close together which makes soldering difficult. Will be changed for wider footprint in a future revision.

## GPIO pins

- GPIO04 (board 7) - Data channel of a DS18B20 temperature sensor (input)
- GPIO12 (board 32) - Fan PWM (output)
- GPIO13 (board 33) - PWM signal to drive the heater through a solid state relay (output)
- GPIO24 (board 18) - Buzzer (output)
- GPIO26 (board 37) - Fan tachometer signal (input)
- GPIO27 (board 13) - Pump relay control (output)

More details about the connections (necessary components and wiring) can be found in the `electronics` sub-directory (open with KiCad).

## Configuring temperature sensor and PWM modules

Add hardware PWM to boot configuration:

```
sudo echo -e "\ndtoverlay=pwm-2chan,pin=12,func=4,pin2=13,func2=4\n" >> /boot/config.txt
```

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

Configure DS18B20 if not alread configured (see previous section).

Install gcc:
```
apt install gcc
```

Navigate to the folder you want to install this application to and clone the repository:
```
git clone https://github.com/andresrobam/brew.git
```

Start the UI:
```
docker compose up -d
```

Navigate to the backend directory, install requirements and start the backend:
```
cd server
pip3 install -r requirements.txt
python3 app.py
```

## Local build

To build and run locally:

```
docker compose -f docker-compose-local.yml up -d
```
