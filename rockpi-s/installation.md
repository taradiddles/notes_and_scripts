# Armbian on Rock PI S

device: Radxa Rock Pi S (`https://wiki.radxa.com/RockpiS`)

Steps:

Install armbian on the device and make sure it works properly:

- download armbian for the rock pi S from `https://www.armbian.com/radxa-rockpi-s/`
- copy the image file to the SD card: follow steps 1 to 3 from `https://wiki.radxa.com/RockpiS/getting_started`
- ssh in the device (see `https://docs.armbian.com/User-Guide_Getting-Started/`). Note: check your router/dhcp server's leases file to find the device's assigned IP.

## Power consumption tweaks

Disable wifi: add `blacklist rtl8723ds` to `/etc/modprobe.d/blacklist.conf`

Systemd's bluetooth service isn't installed, so no need to disable bluetooth with `systemctl disable bluetooth`

Reboot. `rfkill list` should be empty (otherwise, `rfkill block all`).

## I2C/GPIO setup

headers pinout and pin addressing: `https://wiki.radxa.com/RockpiS/hardware/gpio`

Header pins are in GPIO mode by default, so no need to change anything. I2C/SPI/UART/... need to be enabled via overlays:

- doc (despite being for allwinner, also applies to rockchip): `https://docs.armbian.com/User-Guide_Allwinner_overlays/`
- available overlays are listed at `https://wiki.radxa.com/Device-tree-overlays` and in `/boot/dtb/rockchip/overlay/README.rockchip-overlays`

### Enabling I2C bus 0

To enable the first I2C bus, add `overlays=i2c0` to `/boot/armbianEnv.txt` (if multiple overlays are needed, separate with spaces) and reboot.

A `/dev/i2c-0` entry should now exist.

### libmraa

Add radxa apt sources to `/etc/apt/sources.list.d/apt-radxa-com.list`:

```
deb http://apt.radxa.com/buster-stable/ buster main
deb http://apt.radxa.com/buster-testing/ buster main
```

Import key with `wget -O -  apt.radxa.com/buster-testing/public.key | sudo apt-key add -`

Update/upgrade: `apt update ; apt upgrade`

Install libraa: `apt install libmraa-rockpis`

Tests:

- `mraa-gpio get 12`
- `mraa-i2c detect 0` (i2c-0 overlay should be enabled !).


### i2c-tools

`apt install i2c-tools`

`i2c-detect 0` (note: seems to detect a bunch of random stuff when no device is connected compared to `mraa-i2c detect 0`)


### DPS310 barometer

As root:

~~~
apt install python3-dev python3-pip
~~~

As a regular user (eg. 'weather'):

~~~
pip3 install --upgrade setuptools
pip3 install wheel
pip3 install adafruit-circuitpython-dps310 adafruit-extended-bus
~~~

