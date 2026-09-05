# GPS APP FOR TERMINAL IN PYTHON WITH DUAL-BAND WARDRIVING

## USAGE
You have to have gps daemon installed(gpsd)
```bash
sudo apt install gpsd gpsd-clients # for debian/ubuntu
sudo pacman -Syu gpsd gpsd-clients # for arch
```
You have to have GPSd module for python installed
```bash
pip install gps
#or
pip3 install gps
#for some distros the best would be
sudo apt install python3-gps
```
To run you just use:
```bash
python3 Country.py # or whatever you save this file as
# if you want the app to log GPS satellites to a file use
python3 Country.py -l
```
This app automatically logs the wifi networks that it finds to a file called "log_{system_time}.csv"
