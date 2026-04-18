import curses
import time
import datetime
import os

try:
    import gps as gpsd_module
    GPS_AVAILABLE = True
except ImportError:
    GPS_AVAILABLE = False
    print("GPS NOT FOUND")
    exit()
COUNTRY_BOUNDS = {
        "Afghanistan": {"lat": (29.377, 38.491), "lon": (60.529, 74.889)},
        "Albania": {"lat": (39.648, 42.661), "lon": (19.294, 21.054)},
        "Algeria": {"lat": (18.968, 37.094), "lon": (-8.684, 11.999)},
        "Andorra": {"lat": (42.429, 42.656), "lon": (1.414, 1.787)},
        "Angola": {"lat": (-18.042, -4.438), "lon": (11.640, 24.082)},
        "Antigua and Barbuda": {"lat": (16.989, 17.725), "lon": (-61.906, -61.672)},
        "Argentina": {"lat": (-55.061, -21.781), "lon": (-73.578, -53.637)},
        "Armenia": {"lat": (38.841, 41.300), "lon": (43.447, 46.635)},
        "Australia": {"lat": (-43.658, -10.062), "lon": (113.338, 153.639)},
        "Austria": {"lat": (46.372, 49.021), "lon": (9.531, 17.161)},
        "Azerbaijan": {"lat": (38.393, 41.861), "lon": (44.794, 50.370)},
        "Bahamas": {"lat": (20.912, 26.928), "lon": (-79.001, -72.712)},
        "Bahrain": {"lat": (25.796, 26.330), "lon": (50.375, 50.820)},
        "Bangladesh": {"lat": (20.670, 26.631), "lon": (88.028, 92.673)},
        "Barbados": {"lat": (13.045, 13.335), "lon": (-59.652, -59.420)},
        "Belarus": {"lat": (51.262, 56.172), "lon": (23.178, 32.776)},
        "Belgium": {"lat": (49.497, 51.505), "lon": (2.546, 6.408)},
        "Belize": {"lat": (15.886, 18.496), "lon": (-89.225, -87.776)},
        "Benin": {"lat": (6.142, 12.409), "lon": (0.772, 3.843)},
        "Bhutan": {"lat": (26.719, 28.246), "lon": (88.746, 92.119)},
        "Bolivia": {"lat": (-22.898, -9.676), "lon": (-69.645, -57.454)},
        "Bosnia and Herzegovina": {"lat": (42.558, 45.277), "lon": (15.747, 19.622)},
        "Botswana": {"lat": (-26.909, -17.779), "lon": (19.999, 29.360)},
        "Brazil": {"lat": (-33.752, 5.272), "lon": (-73.983, -28.847)},
        "Brunei": {"lat": (4.002, 5.047), "lon": (114.076, 115.364)},
        "Bulgaria": {"lat": (41.235, 44.215), "lon": (22.357, 28.609)},
        "Burkina Faso": {"lat": (9.401, 15.084), "lon": (-5.521, 2.404)},
        "Burundi": {"lat": (-4.470, -2.310), "lon": (28.992, 30.846)},
        "Cabo Verde": {"lat": (14.802, 17.200), "lon": (-25.360, -22.660)},
        "Cambodia": {"lat": (10.487, 14.690), "lon": (102.348, 107.628)},
        "Cameroon": {"lat": (1.656, 13.078), "lon": (8.494, 16.013)},
        "Canada": {"lat": (41.676, 83.110), "lon": (-141.002, -52.619)},
        "Central African Republic": {"lat": (2.220, 11.001), "lon": (14.419, 27.463)},
        "Chad": {"lat": (7.441, 23.450), "lon": (13.473, 24.001)},
        "Chile": {"lat": (-55.980, -17.508), "lon": (-75.644, -66.418)},
        "China": {"lat": (18.197, 53.561), "lon": (73.502, 134.775)},
        "Colombia": {"lat": (-4.227, 12.438), "lon": (-79.000, -66.869)},
        "Comoros": {"lat": (-12.371, -11.362), "lon": (43.211, 44.538)},
        "Congo (Brazzaville)": {"lat": (-5.030, 3.705), "lon": (11.207, 18.650)},
        "Congo (Kinshasa)": {"lat": (-13.459, 5.386), "lon": (12.182, 31.305)},
        "Costa Rica": {"lat": (8.034, 11.220), "lon": (-85.951, -82.555)},
        "Croatia": {"lat": (42.392, 46.555), "lon": (13.490, 19.448)},
        "Cuba": {"lat": (19.828, 23.188), "lon": (-84.952, -74.133)},
        "Cyprus": {"lat": (34.634, 35.701), "lon": (32.272, 34.005)},
        "Czech Republic": {"lat": (48.552, 51.056), "lon": (12.091, 18.860)},
        "Denmark": {"lat": (54.561, 57.752), "lon": (8.073, 15.198)},
        "Djibouti": {"lat": (10.910, 12.707), "lon": (41.774, 43.417)},
        "Dominica": {"lat": (15.200, 15.632), "lon": (-61.483, -61.247)},
        "Dominican Republic": {"lat": (17.598, 19.929), "lon": (-71.945, -68.325)},
        "Ecuador": {"lat": (-5.007, 1.681), "lon": (-80.973, -75.188)},
        "Egypt": {"lat": (22.000, 31.672), "lon": (24.700, 36.902)},
        "El Salvador": {"lat": (13.149, 14.450), "lon": (-90.095, -87.693)},
        "Equatorial Guinea": {"lat": (1.008, 3.764), "lon": (5.619, 11.333)},
        "Eritrea": {"lat": (12.360, 18.004), "lon": (36.440, 43.127)},
        "Estonia": {"lat": (57.510, 59.676), "lon": (21.764, 28.210)},
        "Eswatini": {"lat": (-27.317, -25.719), "lon": (30.794, 32.137)},
        "Ethiopia": {"lat": (3.406, 14.894), "lon": (33.000, 47.979)},
        "Fiji": {"lat": (-20.676, -12.480), "lon": (177.000, -179.917)},
        "Finland": {"lat": (59.808, 70.093), "lon": (20.645, 31.587)},
        "France": {"lat": (41.333, 51.124), "lon": (-5.142, 9.561)},
        "Gabon": {"lat": (-3.979, 2.318), "lon": (8.699, 14.502)},
        "Gambia": {"lat": (13.065, 13.826), "lon": (-16.813, -13.797)},
        "Georgia": {"lat": (41.060, 43.585), "lon": (40.007, 46.691)},
        "Germany": {"lat": (47.270, 55.058), "lon": (5.866, 15.042)},
        "Ghana": {"lat": (4.737, 11.175), "lon": (-3.261, 1.188)},
        "Greece": {"lat": (34.802, 41.749), "lon": (19.374, 29.645)},
        "Grenada": {"lat": (11.983, 12.529), "lon": (-61.801, -61.579)},
        "Guatemala": {"lat": (13.738, 17.816), "lon": (-92.231, -88.225)},
        "Guinea": {"lat": (7.194, 12.674), "lon": (-15.081, -7.641)},
        "Guinea-Bissau": {"lat": (10.924, 12.685), "lon": (-16.713, -13.636)},
        "Guyana": {"lat": (1.185, 8.557), "lon": (-61.395, -56.480)},
        "Haiti": {"lat": (17.980, 20.089), "lon": (-74.479, -71.625)},
        "Honduras": {"lat": (12.984, 16.005), "lon": (-89.351, -83.148)},
        "Hungary": {"lat": (45.748, 48.585), "lon": (16.114, 22.898)},
        "Iceland": {"lat": (63.393, 66.526), "lon": (-24.546, -13.496)},
        "India": {"lat": (8.077, 35.513), "lon": (68.177, 97.395)},
        "Indonesia": {"lat": (-10.940, 5.479), "lon": (95.009, 141.019)},
        "Iran": {"lat": (25.064, 39.781), "lon": (44.032, 63.317)},
        "Iraq": {"lat": (29.069, 37.385), "lon": (38.793, 48.568)},
        "Ireland": {"lat": (51.447, 55.381), "lon": (-10.478, -6.013)},
        "Israel": {"lat": (29.496, 33.337), "lon": (34.267, 35.896)},
        "Italy": {"lat": (36.620, 47.092), "lon": (6.627, 18.521)},
        "Jamaica": {"lat": (17.703, 18.524), "lon": (-78.337, -76.171)},
        "Japan": {"lat": (24.046, 45.523), "lon": (122.934, 153.987)},
        "Jordan": {"lat": (29.186, 33.374), "lon": (34.959, 39.301)},
        "Kazakhstan": {"lat": (40.569, 55.443), "lon": (50.270, 87.359)},
        "Kenya": {"lat": (-4.678, 4.622), "lon": (33.909, 41.899)},
        "Kiribati": {"lat": (-11.437, 4.716), "lon": (-174.545, -168.154)},
        "Kuwait": {"lat": (28.524, 30.099), "lon": (46.553, 48.432)},
        "Kyrgyzstan": {"lat": (39.173, 43.238), "lon": (69.464, 80.228)},
        "Laos": {"lat": (13.910, 22.502), "lon": (100.093, 107.636)},
        "Latvia": {"lat": (55.677, 57.970), "lon": (20.973, 28.241)},
        "Lebanon": {"lat": (33.055, 34.691), "lon": (35.102, 36.624)},
        "Lesotho": {"lat": (-30.668, -28.571), "lon": (27.012, 29.456)},
        "Liberia": {"lat": (4.355, 8.552), "lon": (-11.493, -7.370)},
        "Libya": {"lat": (19.502, 33.170), "lon": (9.319, 25.151)},
        "Liechtenstein": {"lat": (47.048, 47.270), "lon": (9.472, 9.636)},
        "Lithuania": {"lat": (53.906, 56.450), "lon": (20.955, 26.836)},
        "Luxembourg": {"lat": (49.448, 50.184), "lon": (5.735, 6.531)},
        "Madagascar": {"lat": (-25.601, -11.945), "lon": (43.225, 50.477)},
        "Malawi": {"lat": (-17.135, -9.367), "lon": (32.674, 35.916)},
        "Malaysia": {"lat": (0.855, 7.363), "lon": (99.641, 119.268)},
        "Maldives": {"lat": (-0.690, 7.100), "lon": (72.685, 73.759)},
        "Mali": {"lat": (10.147, 25.001), "lon": (-4.245, 4.245)},
        "Malta": {"lat": (35.786, 36.082), "lon": (14.183, 14.575)},
        "Marshall Islands": {"lat": (4.575, 14.616), "lon": (160.802, 172.157)},
        "Mauritania": {"lat": (14.721, 27.295), "lon": (-17.068, -4.834)},
        "Mauritius": {"lat": (-20.520, -10.317), "lon": (56.513, 63.503)},
        "Mexico": {"lat": (14.533, 32.719), "lon": (-117.127, -86.811)},
        "Micronesia": {"lat": (1.028, 10.086), "lon": (137.332, 163.047)},
        "Moldova": {"lat": (45.467, 48.492), "lon": (26.617, 30.136)},
        "Monaco": {"lat": (43.724, 43.752), "lon": (7.409, 7.440)},
        "Mongolia": {"lat": (41.568, 52.149), "lon": (87.762, 119.932)},
        "Montenegro": {"lat": (41.851, 43.559), "lon": (18.451, 20.359)},
        "Morocco": {"lat": (27.667, 35.924), "lon": (-13.169, -0.998)},
        "Mozambique": {"lat": (-26.869, -10.471), "lon": (30.217, 40.840)},
        "Myanmar": {"lat": (9.784, 28.547), "lon": (92.189, 101.170)},
        "Namibia": {"lat": (-28.970, -16.959), "lon": (11.716, 25.256)},
        "Nauru": {"lat": (-0.553, -0.502), "lon": (166.909, 166.959)},
        "Nepal": {"lat": (26.347, 30.447), "lon": (80.058, 88.201)},
        "Netherlands": {"lat": (50.750, 53.555), "lon": (3.358, 7.228)},
        "New Zealand": {"lat": (-52.619, -29.232), "lon": (165.869, 178.561)},
        "Nicaragua": {"lat": (10.708, 15.030), "lon": (-87.668, -82.734)},
        "Niger": {"lat": (11.693, 23.525), "lon": (0.166, 15.996)},
        "Nigeria": {"lat": (4.270, 13.892), "lon": (2.692, 14.680)},
        "North Korea": {"lat": (37.676, 42.986), "lon": (124.270, 130.780)},
        "North Macedonia": {"lat": (40.854, 42.374), "lon": (20.453, 23.034)},
        "Norway": {"lat": (57.977, 71.181), "lon": (4.993, 31.083)},
        "Oman": {"lat": (16.643, 26.393), "lon": (51.998, 59.840)},
        "Pakistan": {"lat": (23.694, 37.097), "lon": (60.878, 77.832)},
        "Palau": {"lat": (2.748, 8.095), "lon": (131.119, 134.722)},
        "Palestine": {"lat": (31.217, 32.553), "lon": (34.217, 35.573)},
        "Panama": {"lat": (7.197, 9.648), "lon": (-83.052, -77.175)},
        "Papua New Guinea": {"lat": (-10.716, -1.312), "lon": (140.843, 155.965)},
        "Paraguay": {"lat": (-27.588, -19.293), "lon": (-62.646, -54.259)},
        "Peru": {"lat": (-18.349, -0.038), "lon": (-81.328, -68.677)},
        "Philippines": {"lat": (4.587, 21.321), "lon": (116.928, 126.537)},
        "Poland": {"lat": (49.002, 54.839), "lon": (14.123, 24.146)},
        "Portugal": {"lat": (36.962, 42.154), "lon": (-9.500, -6.191)},
        "Qatar": {"lat": (24.471, 26.155), "lon": (50.743, 51.607)},
        "Romania": {"lat": (43.619, 48.265), "lon": (20.262, 29.757)},
        "Russia": {"lat": (41.188, 81.858), "lon": (19.640, 180.000)},
        "Rwanda": {"lat": (-2.840, -1.047), "lon": (28.861, 30.899)},
        "Saint Kitts and Nevis": {"lat": (17.095, 17.415), "lon": (-62.872, -62.540)},
        "Saint Lucia": {"lat": (13.713, 14.109), "lon": (-61.077, -60.874)},
        "Saint Vincent and the Grenadines": {"lat": (12.583, 13.377), "lon": (-61.462, -61.119)},
        "Samoa": {"lat": (-14.061, -13.436), "lon": (-172.802, -171.427)},
        "San Marino": {"lat": (43.894, 43.992), "lon": (12.403, 12.516)},
        "Sao Tome and Principe": {"lat": (0.024, 1.699), "lon": (6.470, 7.461)},
        "Saudi Arabia": {"lat": (16.379, 32.161), "lon": (36.578, 55.667)},
        "Senegal": {"lat": (12.332, 16.693), "lon": (-17.535, -11.356)},
        "Serbia": {"lat": (42.232, 46.190), "lon": (18.816, 22.986)},
        "Seychelles": {"lat": (-9.763, -3.705), "lon": (46.199, 56.299)},
        "Sierra Leone": {"lat": (6.930, 10.001), "lon": (-13.296, -10.284)},
        "Singapore": {"lat": (1.259, 1.471), "lon": (103.638, 104.006)},
        "Slovakia": {"lat": (47.731, 49.614), "lon": (16.834, 22.559)},
        "Slovenia": {"lat": (45.422, 46.877), "lon": (13.375, 16.565)},
        "Solomon Islands": {"lat": (-11.856, -6.589), "lon": (155.506, 162.398)},
        "Somalia": {"lat": (-1.661, 11.979), "lon": (40.986, 51.413)},
        "South Africa": {"lat": (-34.840, -22.127), "lon": (16.345, 32.830)},
        "South Korea": {"lat": (33.190, 38.612), "lon": (125.887, 129.584)},
        "South Sudan": {"lat": (3.490, 12.236), "lon": (23.886, 35.948)},
        "Spain": {"lat": (35.947, 43.792), "lon": (-9.301, 4.327)},
        "Sri Lanka": {"lat": (5.917, 9.836), "lon": (79.653, 81.879)},
        "Sudan": {"lat": (8.685, 22.232), "lon": (21.828, 38.607)},
        "Suriname": {"lat": (1.831, 6.002), "lon": (-58.071, -53.976)},
        "Sweden": {"lat": (55.337, 69.060), "lon": (10.963, 24.166)},
        "Switzerland": {"lat": (45.818, 47.808), "lon": (5.956, 10.492)},
        "Syria": {"lat": (32.311, 37.320), "lon": (35.727, 42.376)},
        "Taiwan": {"lat": (21.897, 25.298), "lon": (120.107, 121.951)},
        "Tajikistan": {"lat": (36.671, 41.042), "lon": (67.344, 75.150)},
        "Tanzania": {"lat": (-11.746, -0.990), "lon": (29.327, 40.443)},
        "Thailand": {"lat": (5.637, 20.465), "lon": (97.345, 105.639)},
        "Timor-Leste": {"lat": (-9.463, -8.127), "lon": (124.044, 127.302)},
        "Togo": {"lat": (6.100, 11.139), "lon": (0.007, 1.808)},
        "Tonga": {"lat": (-22.337, -15.557), "lon": (-175.678, -173.741)},
        "Trinidad and Tobago": {"lat": (10.028, 11.362), "lon": (-61.924, -60.520)},
        "Tunisia": {"lat": (30.231, 37.541), "lon": (7.523, 11.600)},
        "Turkey": {"lat": (35.818, 42.108), "lon": (25.668, 44.835)},
        "Turkmenistan": {"lat": (35.129, 42.798), "lon": (52.447, 66.714)},
        "Tuvalu": {"lat": (-9.000, -5.640), "lon": (176.064, 179.872)},
        "Uganda": {"lat": (-1.479, 4.234), "lon": (29.574, 35.004)},
        "Ukraine": {"lat": (44.386, 52.380), "lon": (22.138, 40.228)},
        "United Arab Emirates": {"lat": (22.633, 26.084), "lon": (51.583, 56.382)},
        "United Kingdom": {"lat": (49.957, 58.635), "lon": (-8.175, 1.762)},
        "United States": {"lat": (24.396, 49.384), "lon": (-125.000, -66.934)},
        "Uruguay": {"lat": (-34.951, -30.083), "lon": (-58.443, -53.075)},
        "Uzbekistan": {"lat": (37.185, 45.590), "lon": (55.998, 73.149)},
        "Vanuatu": {"lat": (-20.252, -13.073), "lon": (166.525, 169.901)},
        "Vatican City": {"lat": (41.900, 41.907), "lon": (12.445, 12.458)},
        "Venezuela": {"lat": (0.648, 12.201), "lon": (-73.355, -59.804)},
        "Vietnam": {"lat": (8.562, 23.393), "lon": (102.145, 109.464)},
        "Yemen": {"lat": (12.109, 18.999), "lon": (42.552, 53.109)},
        "Zambia": {"lat": (-18.079, -8.274), "lon": (21.999, 33.706)},
        "Zimbabwe": {"lat": (-22.418, -15.608), "lon": (25.237, 32.849)},
    }

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
        if self.session is None:
            return False; 
        try:
            a = False
            b = False
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
                    a = True
                elif report['class'] == 'SKY': #looks for the SKY class data and updates the gps_get class
                    usat = report.get('uSat', None)
                    nsat = report.get('nSat', None)
                    satelites = report.get('satellites', [])
                    if nsat and usat != None:
                        self.nsat = nsat
                        self.usat = usat
                    if satelites != []:
                        self.satelites = satelites
                    b = True
            return a or b
        except Exception:
            return False
    @property
    def has_fix(self):
        return self.fix >= 2 and self.lat is not None and self.lon is not None
    @property
    def get_head_str(self): #Calculates the direction of travel from the heading that the gps module provides
        if self.heading is None:
            return "Not found"
        directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        directions_index = round(self.heading/45) % 8
        return f"{self.heading:.1f}", f"{directions[directions_index]}"
    @property
    def get_range_of_position(self):
        err = "N/A"
        if self.laterr and self.lonerr != "N/A":
            err = round((self.laterr + self.lonerr)/2,1)
        return err
    @property
    def grid_square_position(self):
        if self.lon and self.lat != 0 and self.lat and self.lon != "N/A":
            lon_adj = self.lon + 180
            lat_adj = self.lat + 90

            F1 = chr(ord('A') + int(lon_adj/20))
            F2 = chr(ord('A') + int(lat_adj/10))

            S1 = str(int((lon_adj%20)/2))
            S2 = str(int(lat_adj%10))

            ss1 = chr(ord('a') + int((lon_adj%2) *12))
            ss2 = chr(ord('a') + int((lat_adj%1) * 24))

            return F1 + F2 + S1 + S2 + ss1 + ss2
        else:
            return "Not found"


    
def get_country(lat, lon): #Calculates which country the position give by the gps is based on the data in COUNTRY_BOUNDS
    for country, bounds in COUNTRY_BOUNDS.items():
        if (bounds["lat"][0] <= lat <= bounds["lat"][1] and 
                bounds["lon"][0] <= lon <= bounds["lon"][1]):
            return country
    return "Ocean"

gps = gps_get()
fix = gps.get_fix()

def get_satelite_info():
    sat = []
    if gps.satelites is not None:
        for satellite in gps.satelites:
            sat.append((satellite.get('PRN', 0), satellite.get('used', False)))
        return sat
    return [("N/A", "N/A")]


def __main__(stdscr):
    fix = gps.update_fix()
    bear, head = gps.get_head_str
    curses.start_color()
    curses.use_default_colors()
    curses.curs_set(0)

    #======================COLORS INITIALIZATION=======================#
    curses.init_pair(1, curses.COLOR_BLACK,  curses.COLOR_MAGENTA) #title bar
    curses.init_pair(2, curses.COLOR_MAGENTA,  -1) #box border
    curses.init_pair(3, curses.COLOR_WHITE, -1) #label
    curses.init_pair(4, curses.COLOR_YELLOW,   -1) #value
    curses.init_pair(5, curses.COLOR_MAGENTA, -1) #color of the header text
    curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_WHITE) #color of the KUKI text
    curses.init_pair(7, curses.COLOR_YELLOW, -1) #color of KUKI the cat

    rows, cols = stdscr.getmaxyx()
    current_country = "N/A"
    if fix and gps.has_fix:
        current_country = get_country(gps.lat, gps.lon)
    stdscr.attron(curses.color_pair(2))
    stdscr.box()
    stdscr.attroff(curses.color_pair(2))
    #==================MAIN DATA BOX========================#
    main_box = curses.newwin(17, 38, 15, int(cols/2 - 33))
    main_box.attron(curses.color_pair(2))
    main_box.box()
    main_box.attroff(curses.color_pair(2))
    main_box.addstr(1,1, "Wait for the content to load", curses.color_pair(3))

    def draw_main_box():
        main_box.attron(curses.color_pair(2))
        main_box.box()
        main_box.attroff(curses.color_pair(2))
        
        main_box.addstr(1,5, " Current gps location: ", curses.color_pair(1))
        main_box.addstr(2,2, "Longitude: ", curses.color_pair(3))
        main_box.addstr(2,2 + len("Longitude: "), f"{gps.lon}", curses.color_pair(4))
        main_box.addstr(3,2, "Latitude: ", curses.color_pair(3))
        main_box.addstr(3,2 + len("Latitude: "), f"{gps.lat}", curses.color_pair(4))
        main_box.addstr(4,2, "Altitude:", curses.color_pair(3))
        main_box.addstr(4,2 + len("Altitude: "), f"{gps.alt}m", curses.color_pair(4))
        main_box.addstr(5,2, "Position error(m): ", curses.color_pair(3))
        main_box.addstr(5,2 + len("position error(m): "), f"{gps.get_range_of_position}", curses.color_pair(4))
        main_box.addstr(6,2, "Current country: ", curses.color_pair(3))
        main_box.addstr(6,2 + len("Current country: "), f"{current_country}", curses.color_pair(4))
        main_box.addstr(7,2, "Current grid square: ", curses.color_pair(3))
        main_box.addstr(7,2+len("current grid square: "), f"{gps.grid_square_position}", curses.color_pair(4))
        main_box.addstr(8,2, "Current speed(m/s): ", curses.color_pair(3))
        main_box.addstr(8,2 + len("Current speed(m/s): "),f"{gps.speed}", curses.color_pair(4))
        main_box.addstr(9,2, "Current speed(km/h): ", curses.color_pair(3))
        main_box.addstr(9,2 + len("Current speed(km/h): "),f"{round(gps.speed * 3.6, 2)}", curses.color_pair(4))
        main_box.addstr(10,2,"Speed error(m/s, km/h): ", curses.color_pair(3))
        if gps.speederr < 10:
            main_box.addstr(10,2 + len("speed error(m/s, km/h): "), f"{gps.speederr:.1f}, {round(gps.speederr * 3.6,1)}", curses.color_pair(4))
        else:
            main_box.addstr(10,2 + len("speed error(m/s, km/h): "), "No movement", curses.color_pair(4))
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
    #==================CURRENT TIME BOX======================#
    time_box = curses.newwin(5, 28, 15, int(cols/2 +5))
    time_box.attron(curses.color_pair(2))
    time_box.box()
    time_box.attroff(curses.color_pair(2))
    time_box.addstr(1,1, "Wait for content to load", curses.color_pair(3))
    def draw_time_box():
        time_box.attron(curses.color_pair(2))
        time_box.box()
        time_box.attroff(curses.color_pair(2))

        time_box.addstr(1, 2, " Current GPS time(UTC): ", curses.color_pair(1))
        time_box.addstr(2, 1, f"{gps.time}", curses.color_pair(4))
        time_box.addstr(3, 1, f"Time error(s): ", curses.color_pair(3))
        time_box.addstr(3, 2+len("time error(s): "), f"{gps.timeerr}", curses.color_pair(4))

    #===================HEADER TEXT BOX======================#
    text_box = curses.newwin(14, cols - 2, 1, 1)

    text_box.addstr(1, 0, " ██████╗ ██████╗ ███████╗ ".center(cols), curses.color_pair(5))
    text_box.addstr(2, 0, "██╔════╝ ██╔══██╗██╔════╝ ".center(cols), curses.color_pair(5))
    text_box.addstr(3, 0, "██║  ███╗██████╔╝███████╗ ".center(cols), curses.color_pair(5))
    text_box.addstr(4, 0, "██║   ██║██╔═══╝ ╚════██║ ".center(cols), curses.color_pair(5))
    text_box.addstr(5, 0, "╚██████╔╝██║     ███████║ ".center(cols), curses.color_pair(5))
    text_box.addstr(6, 0, " ╚═════╝ ╚═╝     ╚══════╝ ".center(cols), curses.color_pair(5))
    text_box.addstr(7, 0, "██╗      ██████╗  ██████╗ █████╗ ████████╗██╗ ██████╗ ███╗   ██╗ ".center(cols), curses.color_pair(5))
    text_box.addstr(8, 0, "██║     ██╔═══██╗██╔════╝██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║ ".center(cols), curses.color_pair(5))
    text_box.addstr(9, 0, "██║     ██║   ██║██║     ███████║   ██║   ██║██║   ██║██╔██╗ ██║ ".center(cols), curses.color_pair(5))
    text_box.addstr(10,0, "██║     ██║   ██║██║     ██╔══██║   ██║   ██║██║   ██║██║╚██╗██║ ".center(cols), curses.color_pair(5))
    text_box.addstr(11,0, "███████╗╚██████╔╝╚██████╗██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║ ".center(cols), curses.color_pair(5))
    text_box.addstr(12,0, "╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ".center(cols), curses.color_pair(5))


    #==================SATELLITE INFO BOX===================#
    found_satelites_box = curses.newwin(12, 28, 20, int(cols/2 +5))
    found_satelites_box.attron(curses.color_pair(2))
    found_satelites_box.box()
    found_satelites_box.attroff(curses.color_pair(2))
    found_satelites_box.addstr(1,1, "Wait for content to load", curses.color_pair(3))
    
    def draw_satelite_info():
        found_satelites_box.attron(curses.color_pair(2))
        found_satelites_box.box()
        found_satelites_box.attroff(curses.color_pair(2))

        found_satelites_box.addstr(1, 5, " Satelites found: ", curses.color_pair(1))
        i = 2
        if (fix):
            sat = get_satelite_info()
            if gps.nsat == 0:
                found_satelites_box.addstr(2 , 2, f"ID: N/A  ", curses.color_pair(4))
                found_satelites_box.addstr(2 , 9 + len("n/a"), f"USED: N/A", curses.color_pair(4))
            else:
                for prn, used in sat:
                    found_satelites_box.addstr(i , 2, f"ID: {prn}  ", curses.color_pair(4))
                    found_satelites_box.addstr(i , 12, f"USED: {used}", curses.color_pair(4))
                    if i < 10:
                        i = i+1
                    else:
                        i = 2
        elif gps.nsat == 0:
            found_satelites_box.addstr(2 , 2, f"ID: N/A  ", curses.color_pair(4))
            found_satelites_box.addstr(2 , 9 + len("n/a"), f"USED: N/A", curses.color_pair(4))


    #=======================KUKI THE CAT BOX=================================#
    cat_box = curses.newwin(15, 28, 27, 1)
    cat_box.addstr(0, 0, "    _", curses.color_pair(7))
    cat_box.addstr(1, 0, "    \`*-", curses.color_pair(7))
    cat_box.addstr(2, 0, "    )  _`-.", curses.color_pair(7))
    cat_box.addstr(3, 0, "    .  : `. .", curses.color_pair(7))
    cat_box.addstr(4, 0, "    : _   '  \.", curses.color_pair(7))
    cat_box.addstr(5, 0, "    ; *` _.   `*-._ ", curses.color_pair(7))
    cat_box.addstr(6, 0, "    `-.-'          `-.", curses.color_pair(7))
    cat_box.addstr(7, 0, "      ; KUKI  `       `.", curses.color_pair(7))
    cat_box.addstr(8, 0, "      :.       .        \.", curses.color_pair(7))
    cat_box.addstr(9, 0, "      . \  .   :   .-'   .", curses.color_pair(7))
    cat_box.addstr(10, 0, "      '  `+.;  ;  '      :",curses.color_pair(7))
    cat_box.addstr(11, 0, "      :  '  |    ;       ;-.",curses.color_pair(7))
    cat_box.addstr(12, 0, "      ; '   : :`-:     _.`* ;",curses.color_pair(7))
    cat_box.addstr(13, 0, "   .*' /  .*' ; .*`- +'  `*'",curses.color_pair(7))
    cat_box.addstr(14, 0, "   `*-*   `*-*  `*-*'",curses.color_pair(7))
    #cat_box.addstr(4, 4 + len("    : _   '  \."), "KUKI", curses.color_pair(7))

    current_time = datetime.datetime.now()                      
    last_time_stamp = current_time.time()
    status = curses.newwin(1, cols-2, rows - 2, 1)
    status.attron(curses.color_pair(1))
    status.addstr(0, 2, f"Last updated: {last_time_stamp}".ljust(cols - 7))
    status.addstr(0, cols - 3 - len("Press q or Q to exit "), "Press q or Q to exit")
    status.attroff(curses.color_pair(1))

    #===============SHOW ALL BOXES=========================#
    stdscr.noutrefresh()
    cat_box.noutrefresh()
    main_box.noutrefresh()
    time_box.noutrefresh()
    text_box.noutrefresh()
    found_satelites_box.noutrefresh()
    status.noutrefresh()
    curses.doupdate()

    last_update = 0 
    stdscr.timeout(100)

    #====================MAIN LOOP==========================#
    while True:
        current_time = datetime.datetime.now()
        now = time.time()

        #============UPDATE DELAY TO PREVENT CRASHES AND MALFUNCTIONS===============#
        if now - last_update >= 1:
            last_time_stamp = current_time.time()
            fix = gps.update_fix()
            last_update = now
            bear, head = gps.get_head_str
            if fix and gps.has_fix:
                current_country = get_country(gps.lat, gps.lon)
            
            main_box.erase()
            draw_main_box()
            if fix:
                found_satelites_box.erase()
                draw_satelite_info()
            time_box.erase()
            draw_time_box()
            status.attron(curses.color_pair(1))
            status.addstr(0, 2, f" Last updated: {last_time_stamp} ".ljust(cols - 7))
            status.addstr(0, cols - 3 - len("Press q or Q to exit "), "Press q or Q to exit")
            status.attroff(curses.color_pair(1))

        main_box.noutrefresh()
        time_box.noutrefresh()
        status.noutrefresh()
        found_satelites_box.noutrefresh()
        
        key = stdscr.getch()
        if key in (ord('q'), ord('Q')):
            stdscr.clear()
            os.system('clear')
            break
        curses.doupdate()
curses.wrapper(__main__)
    
