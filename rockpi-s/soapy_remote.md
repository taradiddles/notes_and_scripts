# Using a rock pi S as a networked RSP remote with SoapyRemote

device: Radxa Rock Pi S (`https://wiki.radxa.com/RockpiS`)

Steps:

Install armbian on the device and make sure it works properly:

- download armbian for the rock pi S from `https://www.armbian.com/radxa-rockpi-s/`
- copy the image file to the SD card: follow steps 1 to 3 from `https://wiki.radxa.com/RockpiS/getting_started`
- ssh in the device (see `https://docs.armbian.com/User-Guide_Getting-Started/`). Note: check your router/dhcp server's leases file to find the device's assigned IP.

Then cross-compile SoapyRemote and copy the files to the device as explained below.

## Cross-compiling SoapyRemote 

### Armbian toolchain

Get/extract the toolchain (from `https://dl.armbian.com/_toolchains/`):

```
mkdir $HOME/devel/
cd $HOME/devel/
wget https://dl.armbian.com/_toolchains/gcc-linaro-7.4.1-2019.02-x86_64_aarch64-linux-gnu.tar.xz
tar --strip-components=1 --one-top-level=gcc_aarch64 -xJf gcc-linaro-7.4.1-2019.02-x86_64_aarch64-linux-gnu.tar.xz
```

Copy the content below to `~/devel/toolchains.cmake`:

```
set(CMAKE_SYSTEM_NAME Linux)
set(buildpath /home/user/devel)
set(CMAKE_PREFIX_PATH ${buildpath}/SDRplay_RSP_API-ARM64/inc ; ${buildpath}/SDRplay_RSP_API-ARM64/aarch64)
set(SoapySDR_DIR ${buildpath}/target/usr/local/share/cmake/SoapySDR)
set(CMAKE_C_COMPILER ${buildpath}/gcc_aarch64/bin/aarch64-linux-gnu-gcc)
set(CMAKE_CXX_COMPILER ${buildpath}/gcc_aarch64/bin/aarch64-linux-gnu-g++)
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)
```

### Building SDRplay API

https://www.sdrplay.com/arm64dl2.php

```
cd $HOME/devel/
chmod a+x SDRplay_RSP_API-ARM64-3.06.1.run
./SDRplay_RSP_API-ARM64-3.06.1.run --target SDRplay_RSP_API-ARM64
ln -s -r SDRplay_RSP_API-ARM64/aarch64/libsdrplay_api.so.3.06 SDRplay_RSP_API-ARM64/aarch64/libsdrplay_api.so
```


### Building SoapySDR

```
cd $HOME/devel/
git clone https://github.com/pothosware/SoapySDR.git
mkdir SoapySDR/build
cd SoapySDR/build
cmake -DCMAKE_TOOLCHAIN_FILE:PATH="../../toolchains.cmake" ..
make
make install DESTDIR=~/devel/target/
```


### Building SoapySDRPlay

```
cd $HOME/devel/
git clone -b API3+RSPduo https://github.com/fventuri/SoapySDRPlay ./SoapySDRPlay
mkdir ./SoapySDRPlay/build
cd ./SoapySDRPlay/build
cmake -DCMAKE_TOOLCHAIN_FILE:PATH="../../toolchains.cmake" ..
make
make install DESTDIR=~/devel/target/
```

### Building SoapyRemote

```
cd $HOME/devel/
git clone https://github.com/pothosware/SoapyRemote.git
mkdir SoapyRemote/build
cd SoapyRemote/build
cmake -DCMAKE_TOOLCHAIN_FILE:PATH="../../toolchains.cmake" ..
make
make install DESTDIR=~/devel/target/
```

## Deploy to the rock pi

- copy/install the SDR play API on the rock pi
- copy the content of `$HOME/devel/target` to the rock pi root fs.

Make libraries in `/usr/local/lib` available system-wide: copy the content below to `/etc/ld.so.conf.d/local.conf`:

```
/usr/local/lib
```

and run `sudo ldconfig`.

Check that libraries are properly found with `sudo ldconfig -p | grep Soapy` and/or `ldd /usr/local/bin/SoapySDRUtil`

Add a systemd unit file for SDRplay API server: copy the content below to `/usr/local/lib/systemd/system/sdrplay_apiService.service`:

```
[Unit]
Description=SDRplay API server
Before=SoapySDRServer.service

[Service]
ExecStart=/usr/local/bin/sdrplay_apiService
KillMode=process
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable/start the servers:

```
sudo systemctl daemon-reload
sudo systemctl enable sdrplay_apiService.service
sudo systemctl start sdrplay_apiService.service
sudo systemctl enable SoapySDRServer
sudo systemctl start SoapySDRServer
```


Finally, check that everything's OK:

`SoapySDRUtil --find`:

```
######################################################
##     Soapy SDR -- the SDR abstraction library     ##
######################################################

Found device 0
  driver = remote
  label = SDRplay Dev0 RSPdx 191104XXXX
  remote = tcp://1.2.3.4:55132
  remote:driver = sdrPlay

Found device 1
  driver = sdrPlay
  label = SDRplay Dev0 RSPdx 191104XXXX
```

## TODO

this won't work: `nmcli connection modify "Wired connection 1" mtu 9000`; find why.
