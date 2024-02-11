# The BumbleBox: an open-source platform for collecting and quantifying behavior in bumblebees

![MastersFigure1final_lowres](https://github.com/Crall-Lab/BumbleBox/assets/102829182/f4c060cb-423d-47ce-b37c-edd3d5f6d22b)

https://github.com/Crall-Lab/BumbleBox/assets/102829182/df6746e8-be8d-474d-97e5-7dcfe8cf2d3f

https://github.com/Crall-Lab/BumbleBox/assets/102829182/92d87284-6381-4c2a-ad78-1d7bee3951b9


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
   
4. Open a terminal window (look for a button on the top left of the screen that looks like a black box with a blue top and white text inside it showing '>_')

5. We're now going to install the required software to use the BumbleBox code. For each of the following commands, type the command (or copy and paste) into the terminal window, and then press enter. Once you enter the command, the computer may take some time to download the required software, and will show a lot of text on the screen. Wait for each command to finish running before attempting to run the next command.

```bash
pip3 install opencv-contrib-python --break-system-packages
```

```bash
pip3 install pandas --break-system-packages
```

```bash
pip3 install scipy --break-system-packages
```

```bash
pip3 install python-crontab --break-system-packages
```

```bash
pip3 install scikit-video --break-system-packages
```

```bash
pip3 install dask –break-system-packages`
```
Amazing! You have now downloaded all the necessary packages to run the BumbleBox on the Raspberry Pi.

6. Next, download the BumbleBox code onto your Raspberry Pi.  To download the code, click the green 'Code' button on the main BumbleBox page and then press the 'Download Zip' button. After downloading the folder onto the Pi and unzipping it, you might want to put the folder onto the Pi's Desktop so you can access it easily.

![download-zip-example-github](https://github.com/Crall-Lab/BumbleBox/assets/102829182/961ca94d-ce7b-4b3b-a8c8-8560dd3a271c)


## Install labelling software (on a separate computer, not the Raspberry Pi - install instructions tested for Mac and Linux computers so far)
### The BumbleBox generates nest images daily that can be labelled in order to track different nest components, which can be useful for a variety of interesting research questions. To do this, we need to install the BumbleBox code and the labelling software we will use on a separate computer. 

1. Install BumbleBox code onto your computer, in the same manner as above

2. Open a terminal window on your computer (try typing 'terminal' into your computer search bar to find it, or go to your applications page and search for the terminal app)

3. Type the following command to create what is called a virtual environment, which basically creates an isolated place on your computer to download software so that it won't potentially cause conflicts with other software on your computer. The virtual environment we're creating is called labelme, because we will be downloading software called labelme.

```bash
python3 -m venv labelme
```

4. Now we have to 'go into' the virtual environment that we've created, using this command:

```bash
source labelme/bin/activate
```

Your terminal should now look something like this:

![virtual-env-tutorial-pic](https://github.com/Crall-Lab/BumbleBox/assets/102829182/838d461d-6928-4cc8-b6d2-368ecc983b3f)

Now we're ready to install labelme!

```bash
pip3 install labelme
```
