# The BumbleBox: an open-source platform for collecting and quantifying behavior in bumblebees

![MastersFigure1final_lowres](https://github.com/Crall-Lab/BumbleBox/assets/102829182/f4c060cb-423d-47ce-b37c-edd3d5f6d22b)

https://github.com/Crall-Lab/BumbleBox/assets/102829182/884fe794-ba71-4942-8e86-25422a294a5b

## Software Installation and Setup

### Raspberry Pi Install

Installed using the following hardware:
- Rasbperry Pi 4b, 8GB RAM
- 32GB SanDisk Ultra SD card
- Monitor with HDMI
- HDMI to micro-HDMI cable

1. Download Debian Bookworm 64-bit OS onto your SD card using a computer with the Raspberry Pi Imager application (Download the application here: https://www.raspberrypi.com/software/)
   
2. Put the SD card into the Pi's SD card slot, hook the Pi up to a monitor via a micro-HDMI to HDMI cable, and power the Pi on - you should see the operating system load on the screen
   
3. You will need to create a username and password for the Raspberry Pi - Ex. 'pi' and 'bombus'
   
5. Open a terminal window (look for a button on the top left of the screen that looks like a black box with a blue top and white text inside it showing '>_')

6. We're now going to install the required software to use the BumbleBox code. For each of the following commands, type the command (or copy and paste) into the terminal window, and then press enter. Once you enter the command, the computer may take some time to download the required software, and will show a lot of text on the screen. Wait for each command to finish running before attempting to run the next command.

```bash
pip3 install opencv-contrib-python –break-system-packages
```

```bash
pip install pandas --break-system-packages
```

```bash
pip install scipy --break-system-packages
```

```bash
pip install python-crontab --break-system-packages
```

```bash
pip install scikit-video --break-system-packages
```

```bash
pip install dask –break-system-packages`
```

Download the BumbleBox code onto your Raspberry Pi. I download the folder onto the Pi's Desktop so I can access it easily. To do this, click 
 

