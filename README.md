# brew
Raspberry Pi based brewing controller

Written for and tested on a Raspberry Pi 4B running DietPi 9.9, but might work on other combinations.

#pins
pump
fan
ssr heat
buzzer
ds18b20 temp

needs docker and etc


# Installation
Log in to your Pi and navigate to the folder you want to save the application to.\
Download docker-compose file
wget https://raw.githubusercontent.com/andresrobam/brew/refs/heads/master/docker-compose.yml
mkdir -p server/config
docker compose up -d