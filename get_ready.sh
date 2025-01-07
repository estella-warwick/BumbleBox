#!/bin/bash

# Script to get this Raspberry Pi ready
# to run BumbleBox code
echo "Get Pi ready to run BumbleBox code"
cd ~/code/BumbleBox

# Set up directories
echo "Create necessary directories (if they don't already exist)"
# Logs directory - stores logging output
if [ ! -d "$HOME/Desktop" ]; then
  mkdir $HOME/Desktop
fi
if [ ! -d "$HOME/Desktop/BumbleBox" ]; then
  mkdir $HOME/Desktop/BumbleBox
fi
if [ ! -d "$HOME/Desktop/BumbleBox/logs" ]; then
  mkdir $HOME/Desktop/BumbleBox/logs
fi
echo "Directories done"

# Get the virtual environment set up
# with the necessary packets etc.
echo "Set up Virtual Environment and Python packages"
python3 -m venv venv
# Add system wide packages to venv
# These will include picamera2
python3 -m venv --system-site-packages venv
# Install the specific requirements for this app
source venv/bin/activate
echo "Estella Dec 2024 - Tested combo doesn't work :-(. Use Latest"
read -p "Python packages - use latest (L), or the tested (T) combination of versions?: " package_set
requirements_file="requirements_tested.txt"
if [ "$package_set" = "L" ]; then
  echo "Use latest"
  requirements_file="requirements_latest.txt"
else
  echo "Use the tested version set (the default option)"
fi
pip install -r $requirements_file
echo "Python packages installed"
echo
echo "============================================================="
echo "Ready to run.  Next actions for you:"
echo " - edit setup.py if you want any non-default settings"
echo " - do 'source venv/bin/activate' to start the Virtual Environment"
echo " - do 'python3 -m start_automated_recording' to kick off recording + tag analysis"
echo
echo "(alternatively you can run the processes manually.  Dec 2024, Estella note - only tested for record_video so far)"