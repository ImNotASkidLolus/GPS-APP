import curses
import time
import datetime
import os
import argparse
import threading
import math
import json
from shapely.geometry import shape, Point
import csv
try:
    import gps as gpsd_module
    GPS_AVAILABLE = True
except ImportError:
    GPS_AVAILABLE = False
    print("GPS NOT FOUND")
    exit()

#  ██████╗ ██████╗ ███████╗       ██╗      ██████╗  ██████╗ █████╗ ████████╗██╗ ██████╗ ███╗   ██╗                             
# ██╔════╝ ██╔══██╗██╔════╝       ██║     ██╔═══██╗██╔════╝██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║                            
# ██║  ███╗██████╔╝███████╗       ██║     ██║   ██║██║     ███████║   ██║   ██║██║   ██║██╔██╗ ██║                            
# ██║   ██║██╔═══╝ ╚════██║       ██║     ██║   ██║██║     ██╔══██║   ██║   ██║██║   ██║██║╚██╗██║                            
# ╚██████╔╝██║     ███████║       ███████╗╚██████╔╝╚██████╗██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║                            
#  ╚═════╝ ╚═╝     ╚══════╝       ╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝

# The app was basically made for my hackberry and was not tested for other devices, 
# but probably this code works for every system that will run gpsd(GPS daemon).
# Basically all unix based systems Mac, Linux, Free BSD      
# Please notify me for any issues of bugs to fix or maybe even features to add ;)                                                                              
filename = "log"
WIGLE_HEADER = [
    'WigleWifi-1.4',
    'appRelease=Wardriver',
    'model=custom',
    'release=1.0',
    'device=linux',
    'display=wardrive',
    'board=uconsole',
    'brand=unknown',
]

WIGLE_COLS = [
    'MAC','SSID','AuthMode','FirstSeen','Channel',
    'CurrentLatitude','CurrentLongitude','AltitudeMeters','AccuracyMeters','Type'
]
class gps_get():
    def __init__(self):
        self.lat = 0 
        self.lon = 0
        self.alt = 0
        self.laterr = 0
        self.lonerr = 0
        self.speed = 0
        self.speederr = 0
        self.fix = 0 #what type of fix the gps has
        self.time = "No time"  
        self.timeerr = 0
        self.heading = 0 
        self.climb = "N/A" #climb rate 
        self.session = None
        self.satelites = None
        self.usat = 0 #number of used satellites
        self.nsat = 0 #number of found satellites
        self.country_name = ""
        self._is_set = threading.Event()
    def stop(self):
        self._is_set.set()
    def get_fix(self):
        if not GPS_AVAILABLE:
            return "Error: GPS NOT FOUND!"
        else:
            try:
                self.session = gpsd_module.gps(mode=gpsd_module.WATCH_ENABLE | gpsd_module.WATCH_NEWSTYLE)
                return True
            except Exception:
                return False
    def update_fix(self):
        while not self._is_set.is_set():
            if self.session is None:
                break
            try:
                for _ in range(20):
                    report = self.session.next()
                    if report['class'] == 'TPV': #looks for the TPV class data and updates the gps_get class
                        self.fix   = getattr(report, 'mode',  1)
                        self.lat   = getattr(report, 'lat',   "N/A")
                        self.lon   = getattr(report, 'lon',   "N/A")
                        self.laterr = getattr(report, 'epy', "N/A")
                        self.lonerr = getattr(report, 'epx', "N/A")
                        self.alt   = getattr(report, 'alt',   "N/A")
                        self.speed = getattr(report, 'speed', 0)
                        self.speederr = getattr(report, 'eps', 0)
                        self.time = getattr(report, 'time', datetime.datetime.now())
                        self.timeerr = getattr(report, 'ept', "N/A")
                        self.heading = getattr(report, 'track', 0)
                        self.climb = getattr(report, 'climb', "N/A")
                    elif report['class'] == 'SKY': #looks for the SKY class data and updates the gps_get class
                        usat = getattr(report, 'uSat', None)
                        nsat = getattr(report, 'nSat', None)
                        satelites = getattr(report, 'satellites', [])
                        if nsat and usat != None:
                            self.nsat = nsat
                            self.usat = usat
                        if satelites != []:
                            self.satelites = satelites
                time.sleep(0.5)
            except Exception:
                print("Polling error")
    @property
    def has_fix(self):
        return self.fix >= 2 and self.lat is not None and self.lon is not None
    @property
    def get_head_str(self): #Cal    print(args.output)   # None if not providedculates the direction of travel from the heading that the gps module provides
        if self.heading is None:
            return "Not found"
        directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        directions_index = round(self.heading/45) % 8
        return f"{self.heading:.1f}", f"{directions[directions_index]}"
    @property
    def get_range_of_position(self):
        err = "N/A"
        if self.laterr and self.lonerr != "N/A":
            err = round(math.sqrt(self.laterr**2 + self.lonerr**2),1)
        return err
    @property
    def grid_square_position(self):
        if self.lon not in (0, "N/A") and self.lat not in (0, "N/A"):
            lon_adj = self.lon + 180
            lat_adj = self.lat + 90
            F1 = chr(ord('A') + int(lon_adj / 20))
            F2 = chr(ord('A') + int(lat_adj / 10))

            S1 = str(int((lon_adj % 20) / 2))
            S2 = str(int(lat_adj % 10))

            ss1 = chr(ord('a') + int((lon_adj % 2) * 12))
            ss2 = chr(ord('a') + int((lat_adj % 1) * 24))

            return F1 + F2 + S1 + S2 + ss1 + ss2
        else:
            return "Not found"
    
    def get_country(self): #Calculates which country the position give by the gps is based on the data in COUNTRY_BOUNDS
        with open("/home/dragon/GPS-APP/map.geojson") as f:
            data = json.load(f)

        location = Point(self.lon, self.lat)
        features = data.get('features', [data])
        for feature in features:
            polygon = shape(feature['geometry'])
            if polygon.contains(location):
                country_name = feature.get('properties', {}).get('NAME', 'Unknown Country')
                self.country_name = country_name
                return country_name
        return "Ocean"

def get_constelation(id):
    if id == 0:
        return "GPS(US)"
    elif id == 1:
        return "SBAS"
    elif id == 2:
        return "GALILEO(EU)"
    elif id == 3:
        return "BEIDOU(CN)"
    elif id == 4:
        return "IMES"
    elif id == 5:
        return "QZSS(JPN)"
    elif id == 6:
        return "GLONASS(RU)"
    else:
        return "N/A"
def get_satelite_info():
    sat = []
    if gps.satelites is not None:
        for satellite in gps.satelites:
            sat.append((int(satellite.get('PRN', 0)), satellite.get('used', False), satellite.get('ss', 0), satellite.get('gnssid', "N/A")))
        return sorted(sat)
    return [("N/A", "N/A", "N/A", "N/A")]
def log_sats(lat,lon):
    try:
        new_satellites = []
        if not os.path.exists(os.path.expanduser("~/satellites.txt")):
            open(os.path.expanduser("~/satellites.txt"),"x")
        with open(os.path.expanduser("~/satellites.txt"), "r") as f:
            content = f.read()
            for prn, used, ss, gnssid in get_satelite_info():
                if str(prn) not in content:
                    new_satellites.append((prn, gnssid))
        with open(os.path.expanduser("~/satellites.txt"), "a") as f:
            for sat in new_satellites:
                f.write(f"{sat[0]} {get_constelation(sat[1])} {lat} {lon}\n")
    except Exception as e:
        print(e)
log_satellites = False
start_idx = 0

def scan_aps():
    global l_secs,l_channels,l_ssids,l_bssids, filename
    seen = set()
    filename = filename + "_" + str(datetime.datetime.now()) + ".csv"
    with open(filename, 'w', newline='') as f:
        f.write(','.join(WIGLE_HEADER) + '\n')
        w = csv.writer(f)
        w.writerow(WIGLE_COLS)
    while not gps._is_set.is_set():
        ssids = []
        bssids = []
        channels = []
        secs = []
        if not gps.fix:
            time.sleep(0.5)
            continue
        try:
            os.popen("nmcli dev wifi rescan")
            netw = os.popen("nmcli -t -f SSID,BSSID,CHAN,SECURITY dev wifi list").read()
            netw = netw.split('\n')
            for line in netw:
                if len(line) < 10:
                    continue
                line = line.split(':')
                ssids.append(line[0])
                bssid = line[1:6]   
                n_bssid = ""
                counter = 0
                for i in bssid:
                    n_bssid += str(i.strip("\\"))
                    if counter < 4:
                        n_bssid+=":"
                        counter+=1
                bssids.append(n_bssid)
                channels.append(line[7])
                secs.append(line[8])
        except Exception as e:
            print(e)
        for bssid, essid, channel, privacy in zip(bssids, ssids, channels, secs):
            if bssid in seen:
                continue
            if gps.lat == 0:
                continue
            if not gps.fix:
                continue
            with threading.Lock():
                if bssid in seen:
                    continue
                seen.add(bssid)
                with open(filename, 'a', newline='') as f:
                    w = csv.writer(f)
                    w.writerow([
                        bssid,
                        essid,
                        f'[{privacy}]',
                        gps.time,
                        channel,
                        gps.lat,
                        gps.lon,
                        gps.alt,
                        gps.get_range_of_position,
                        'WIFI',
                    ])

        
def main(stdscr):
    global start_idx, log_satellites
    bear, head = gps.get_head_str
    rows, cols = stdscr.getmaxyx()
    curses.start_color()
    curses.use_default_colors()
    curses.curs_set(0)

    #======================COLORS INITIALIZATION=======================#
    curses.init_pair(1, curses.COLOR_BLACK,  curses.COLOR_GREEN) #title bar
    curses.init_pair(2, curses.COLOR_WHITE,  -1) #box border
    curses.init_pair(3, curses.COLOR_GREEN, -1) #label
    curses.init_pair(4, curses.COLOR_MAGENTA,   -1) #value
    curses.init_pair(5, curses.COLOR_RED, -1) #color of the header text
    curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_WHITE) #color of the KUKI text
    curses.init_pair(7, curses.COLOR_YELLOW, -1) #color of KUKI the cat

    current_country = "N/A"
    if fix and gps.has_fix:
        current_country = gps.get_country()
    try:
        stdscr.attron(curses.color_pair(2))
        stdscr.box()
        stdscr.attroff(curses.color_pair(2))
    except Exception:
        print("Error printing too screen, perhaps your terminal is too small :(")
        exit()
    #==================MAIN DATA BOX========================#
    try:
        main_box = curses.newwin(17, 34, 1, 1)
        main_box.attron(curses.color_pair(2))
        main_box.box()
        main_box.attroff(curses.color_pair(2))
        main_box.addstr(1,1, "Wait for the content to load", curses.color_pair(3))
    except Exception:
        print("Error printing too screen, perhaps your terminal is too small :(")
        exit()

    def draw_main_box():
        try:
            main_box.attron(curses.color_pair(2))
            main_box.box()
            main_box.attroff(curses.color_pair(2))
            
            main_box.addstr(1,1, " Current gps location: ".center(32), curses.color_pair(1))
            main_box.addstr(2,2, "Longitude: ", curses.color_pair(3))
            main_box.addstr(2,2 + len("Longitude: "), f"{gps.lon}", curses.color_pair(4))
            main_box.addstr(3,2, "Latitude: ", curses.color_pair(3))
            main_box.addstr(3,2 + len("Latitude: "), f"{gps.lat}", curses.color_pair(4))
            main_box.addstr(4,2, "Altitude:", curses.color_pair(3))
            main_box.addstr(4,2 + len("Altitude: "), f"{gps.alt}m", curses.color_pair(4))
            main_box.addstr(5,2, "Position error(m): ", curses.color_pair(3))
            main_box.addstr(5,2 + len("position error(m): "), f"{gps.get_range_of_position}", curses.color_pair(4))
            main_box.addstr(6,2, "Current country: ", curses.color_pair(3))
            main_box.addstr(6,2 + len("Current country: "), f"{current_country[:10]}", curses.color_pair(4))
            main_box.addstr(7,2, "Current grid square: ", curses.color_pair(3))
            main_box.addstr(7,2+len("current grid square: "), f"{gps.grid_square_position}", curses.color_pair(4))
            main_box.addstr(8,2, "Current speed(m/s): ", curses.color_pair(3))
            main_box.addstr(8,2 + len("Current speed(m/s): "),f"{gps.speed}", curses.color_pair(4))
            main_box.addstr(9,2, "Current speed(km/h): ", curses.color_pair(3))
            main_box.addstr(9,2 + len("Current speed(km/h): "),f"{round(gps.speed * 3.6, 1)}", curses.color_pair(4))
            main_box.addstr(10,2,"Speed error(m/s, km/h): ", curses.color_pair(3))
            if gps.speederr < 50:
                main_box.addstr(10,2 + len("speed error(m/s, km/h): "), f"{round(gps.speederr,1)}, {round(gps.speederr * 3.6,1)}", curses.color_pair(4))
            else:
                main_box.addstr(10,2 + len("speed error(m/s, km/h): "), "Stnry", curses.color_pair(4))
            main_box.addstr(11,2, "Climb rate(m/s): ", curses.color_pair(3))
            main_box.addstr(11,2 + len("Climb rate(m/s): "), f"{gps.climb}", curses.color_pair(4))
            main_box.addstr(12,2, "Heading: ", curses.color_pair(3))
            main_box.addstr(12,2 + len("Heading: "), f"{head}", curses.color_pair(4))
            main_box.addstr(13,2, "Bearing: ", curses.color_pair(3))
            main_box.addstr(13,2 + len("Bearing: "), f"{bear}°T", curses.color_pair(4))
            main_box.addstr(14,2, "Used satellites: ", curses.color_pair(3))
            main_box.addstr(14, 2 + len("used satellites: "), f"{gps.usat}", curses.color_pair(4))
            main_box.addstr(15,2, "Satellites found: ", curses.color_pair(3))
            main_box.addstr(15,2+len("satellites found: "), f"{gps.nsat}", curses.color_pair(4))
        except Exception as e:
            print("Error printing too screen, perhaps your terminal is too small :( main")
            print(e)
            exit()
    #==================CURRENT TIME BOX======================#
    try:
        time_box = curses.newwin(5, 32, 1, 1+34)
        time_box.attron(curses.color_pair(2))
        time_box.box()
        time_box.attroff(curses.color_pair(2))
        time_box.addstr(1,1, "Wait for content to load", curses.color_pair(3))
    except Exception:
        print("Error printing too screen, perhaps your terminal is too small :( time")

    def draw_time_box():
        try:
            time_box.attron(curses.color_pair(2))
            time_box.box()
            time_box.attroff(curses.color_pair(2))

            time_box.addstr(1, 1, " Current GPS time(UTC): ".center(30), curses.color_pair(1))
            time_box.addstr(2, 2, f"{gps.time}", curses.color_pair(4))
            time_box.addstr(3, 2, f"Time error(s): ", curses.color_pair(3))
            time_box.addstr(3, 2+len("time error(s): "), f"{gps.timeerr}", curses.color_pair(4))
        except Exception:
            print("Error printing too screen, perhaps your terminal is too small :( time show")

    #==================SATELLITE INFO BOX===================#
    try:
        found_satelites_box = curses.newwin(12, 32, 6, 1+34)
        found_satelites_box.attron(curses.color_pair(2))
        found_satelites_box.box()
        found_satelites_box.attroff(curses.color_pair(2))
        found_satelites_box.addstr(1,1, "Wait for content to load", curses.color_pair(3))
    except Exception:
        print("Error printing too screen, perhaps your terminal is too small :(")
        exit()

    def draw_satelite_info():
        try:
            found_satelites_box.attron(curses.color_pair(2))
            found_satelites_box.box()
            found_satelites_box.attroff(curses.color_pair(2))

            found_satelites_box.addstr(1, 1, " Satelites found: ".center(30), curses.color_pair(1))
            i = 3
            if (fix):
                sat = get_satelite_info()
                if gps.nsat == 0:
                    found_satelites_box.addstr(2 , 2, "ID ", curses.color_pair(3))
                    found_satelites_box.addstr(2, 6, "SNR",curses.color_pair(3))
                    found_satelites_box.addstr(2 , 11, "USED",curses.color_pair(3))
                    found_satelites_box.addstr(2, 18, "CONST",curses.color_pair(3))
                    found_satelites_box.addstr(3, 2, "N/A",curses.color_pair(4))
                    found_satelites_box.addstr(3, 6, "N/A",curses.color_pair(4))
                    found_satelites_box.addstr(3, 11, "N/A",curses.color_pair(4))
                    found_satelites_box.addstr(3, 18, "N/A",curses.color_pair(4))
                    
                else:
                    found_satelites_box.addstr(2 , 2, "ID ", curses.color_pair(3))
                    found_satelites_box.addstr(2, 6, "SNR",curses.color_pair(3))
                    found_satelites_box.addstr(2 , 11, "USED",curses.color_pair(3))
                    found_satelites_box.addstr(2, 18, "CONST",curses.color_pair(3))
                    for prn, used, snr, gnssid in sat[start_idx:]:
                        found_satelites_box.addstr(i, 2, f"{prn}  ",curses.color_pair(4))
                        found_satelites_box.addstr(i, 6, f"{int(snr)}dB  ", curses.color_pair(4))
                        found_satelites_box.addstr(i, 11, f"{used}",curses.color_pair(4))
                        found_satelites_box.addstr(i, 18, get_constelation(gnssid),curses.color_pair(4))
                        if i < 10:
                            i = i+1
                        else:
                            i = 3
                        if log_satellites:
                            log_sats(gps.lat, gps.lon)
            else:
                found_satelites_box.addstr(3, 2, "N/A",curses.color_pair(4))
                found_satelites_box.addstr(3, 6, "N/A",curses.color_pair(4))
                found_satelites_box.addstr(3, 11, "N/A",curses.color_pair(4))
                found_satelites_box.addstr(3, 18, "N/A",curses.color_pair(4))
        except Exception:
            print("Error printing too screen, perhaps your terminal is too small :( satellites")
            exit()
            
    current_time = datetime.datetime.now()                      
    last_time_stamp = current_time.time()
    #===============SHOW ALL BOXES=========================#
    try:
        stdscr.noutrefresh()
        main_box.noutrefresh()
        time_box.noutrefresh()
        found_satelites_box.noutrefresh()
        curses.doupdate()
    except Exception:
        print("Error printing too screen, perhaps your terminal is too small :( updating")
        exit()

    last_update = 0 
    stdscr.timeout(100)

    #====================MAIN LOOP==========================#
    while True:
        current_time = datetime.datetime.now()
        now = time.time()

        #============UPDATE DELAY TO PREVENT CRASHES AND MALFUNCTIONS===============#
        if now - last_update >= 1:
            
            last_time_stamp = current_time.time()
            last_update = now
            bear, head = gps.get_head_str
            if fix and gps.has_fix:
                current_country = gps.get_country()
            
        try:
            main_box.erase()
            draw_main_box()
            if fix:
                found_satelites_box.erase()
                draw_satelite_info()
            time_box.erase()
            draw_time_box()
            stdscr.erase()
            stdscr.attron(curses.color_pair(2))
            stdscr.box()
            stdscr.attroff(curses.color_pair(2))
            stdscr.noutrefresh()
            main_box.noutrefresh()
            time_box.noutrefresh()
            found_satelites_box.noutrefresh()
        except Exception:
            print("Error printing too screen, perhaps your terminal is too small :(")
            exit()
        
        key = stdscr.getch()
        if key in (ord('q'), ord('Q')):
            stdscr.clear()
            os.system('clear')
            break
        elif key == curses.KEY_UP:
            if start_idx > 0:
                start_idx -=1
        elif key == curses.KEY_DOWN:
            if start_idx < len(get_satelite_info()) - 5:
                start_idx += 1
        curses.doupdate()

if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(description="COUNTRY GPS TOOL")
    argument_parser.add_argument("-n", "--nocat", action="store_true", help="Hides the KUKI image from displaying")
    argument_parser.add_argument("-f", "--forcecat", action="store_true", help="Force the cat to show up")
    argument_parser.add_argument("-l", "--log-satellites", action="store_true", help="Logs the satellites found to a file called satellites.txt")
    parsed_args = argument_parser.parse_args()
    use_cat = not parsed_args.nocat
    force_cat = parsed_args.forcecat
    log_satellites = parsed_args.log_satellites
    gps = gps_get()
    fix = gps.get_fix()
    gps_thread = threading.Thread(target=gps.update_fix, daemon=True)
    gps_thread.start()
    scan_thread = threading.Thread(target=scan_aps,daemon=True)
    scan_thread.start()
    curses.wrapper(main)
    gps.stop()
    if gps_thread:
        gps_thread.join(timeout=1)
       
    
