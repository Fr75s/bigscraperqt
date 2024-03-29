import os, sys, json, atexit, datetime, unidecode
from xdg import xdg_data_home, xdg_config_home
from yt_dlp import YoutubeDL

from PyQt5.QtCore import *

## Genral Information
info = {
	"NAME": "bigscraper-qt",
	"VERSION": "1.4.3",
	"AUTHOR": "Fr75s",
	"LICENSE": "GPLv3",
	"URL": "https://fr75s.github.io/bigscraperqt/"
}

version_info = info["NAME"] + " v" + info["VERSION"] + ". Made by " + info["AUTHOR"] + ". Licensed under " + info["LICENSE"]

# Paths for saving configs
paths = {
	"DATA": xdg_data_home(),
	"APP_DATA": os.path.join(xdg_data_home(), "bigscraper-qt/"),
	"METADATA": os.path.join(xdg_data_home(), "bigscraper-qt/metadata/"),
	"MEDIA": os.path.join(xdg_data_home(), "bigscraper-qt/media/"),
	"LOGS": os.path.join(xdg_data_home(), "bigscraper-qt/logs/"),
	"EXTRA": os.path.join(xdg_data_home(), "bigscraper-qt/extra/"),
	"OPTS": os.path.join(xdg_config_home(), "bigscraper-qt/"),
	"HOME": os.path.expanduser("~")
}

## Some Constants

ydl = YoutubeDL()

VIDEO_LEN_LIMIT = 300

STICK_THRESHOLD = 32768 * 0.75
STICK_DEADZONE = 32768 * 0.2

## Get Time for Logging

ct_raw = str(datetime.datetime.now())

ct_s = ct_raw.split(" ")

ct_l = ct_s[0].split("-")
ct_r = ct_s[1].split(":")

ct = [
	ct_l[0],
	ct_l[1],
	ct_l[2],
	ct_r[0],
	ct_r[1],
	ct_r[2].split(".")[0]
]

ct_format = ct[0] + ct[1] + ct[2] + "_" + ct[3] + ct[4] + ct[5]


#
## Request Link Preformats
#

def lb_page(system, page):
	return "https://gamesdb.launchbox-app.com/platforms/games/" + lb_sysid[system] + "/page/" + str(page)

#
## Define some useful functions
#

# Remove Accents
def noaccent(text):
	out = u"" + text
	return unidecode.unidecode(out)

# Format text for matching
def form(text):
	out = ""

	# Remove Anything in Brackets
	inbr = False
	for c in text:
		if (c in ("(", "[", "{")):
			inbr = True
		if not(inbr):
			out += c
		if (c in (")", "]", "}")):
			inbr = False

	# Remove Accents (USES ABOVE)
	out = noaccent(out)

	# Numerous Character Replacements
	out = out.upper().strip(" ").replace(" -","").replace(": ","_").replace(" ","_").replace(":","_").replace("-","_").replace(".","").replace("!","").replace("?","").replace("'","").replace("&","AND")

	# Remove Consecutive _s
	out2 = ""
	for n in range(0, len(out)):
		if (out[n:n+1] == "_" and out[n+1:n+2] == "_"):
			log(f"DUPLICATE _ AT {n}", "D", True)
		else:
			out2 += out[n:n+1]

	# Resulting string should be fit
	return out2

def linkform(text):
	return text.upper().strip(" ").replace(" ","+")

# Remove Extension from file names
def trimext(text):
	postdot = text[(text.rfind(".") + 1):]

	while (len(postdot) <= 4 and text.rfind(".") >= 0):
		text = text[0:text.rfind(".")]
		if (text.rfind(".") >= 0):
			postdot = text[(text.rfind(".") + 1):]

	return text

# Filter Escape Characters
# (currently only removes \r and \n, and converts other escaped characters)
def filter_escapes(text):
	return text.replace("\\r","").replace("\\n","").replace("\\\\","\\").replace("\\","")

def video_len_test(info, *, incomplete):
	video_duration = info.get("duration")
	if video_duration and video_duration > VIDEO_LEN_LIMIT:
		return "Sorry, too long"

# Download Video
def download_video(url, options):
	with YoutubeDL(options) as video_downloader:
		err = video_downloader.download(url)


def res_file(basename):
	return os.path.dirname(__file__) + "/" + basename



## Define a few values for the scripts

# OPTIONS
options = {
	"video": True,
	"videoOverLimit": False,
	"glassyTitle": True,
	"recache": False,
	"localPaths": False,
}

#
# SCRAPING MODULES
# Currently Implemented:
#
# LaunchBox
# --Arcade Database (adb) soon--
#

optionsVary = {
	"region": "North America",
	"module": "LaunchBox",
	"languageOverride": "None",
	"maxLogFiles": 50,
	"screenScraperUser": "",
	"screenScraperPass": ""
}

def merged_options():
	return {**options, **optionsVary}

def save_options():
	merge_options = merged_options()

	options_json = json.dumps(merge_options, indent = 4)
	open(os.path.join(paths["OPTS"], "options.json"), "w").write(options_json)
	log("Saved Options to File", "D", True)


optionValues = {
	"region": ["North America", "Europe", "Japan"],
	"module": ["LaunchBox", "Arcade Database", "ScreenScraper"],
	"languageOverride": ["None", "English", "Spanish", "French", "German", "Portuguese", "Italian"]
}

langs_universal = {
	"English": "en",
	"Spanish": "es",
	"French": "fr",
	"German": "de",
	"Portuguese": "pt",
	"Italian": "it",
}

regions = {
	"North America": ["(North America)", "(United States)", "(Canada)", "(World)"],
	"Europe": ["(Europe)", "(United Kingdom)", "(Germany)", "(France)", "(Spain)", "(Italy)", "(The Netherlands)", "(Russia)", "(World)"],
	"Japan": ["(Japan)", "(World)", ""]
}

regions_ss = {
	"North America": ["us", "ame", "ca", "wor", "ss"],
	"Europe": ["eu", "uk", "de", "fr", "wor", "ss"],
	"Japan": ["jp", "wor", "ss"]
}

region_translate = {
	"ss": "",

	"us": "(North America)",
	"ame": "(North America)",
	"ca": "(North America)",

	"eu": "(Europe)",
	"uk": "(United Kingdom)",
	"de": "(Germany)",
	"fr": "(France)",
	"sp": "(Spain)",
	"it": "(Italy)",
	"nl": "(The Netherlands)",
	"ru": "(Russia)",

	"jp": "(Japan)",
	"cn": "(China)",
	"kr": "(Korea)",

	"au": "(Australia)",
	"br": "(Brazil)",

	"wor": "(World)"
}

langs_ss = {
	"North America": ["en", "es"],
	"Europe": ["en", "fr", "es", "de", "it", "pt"],
	"Japan": ["en"]
}

## Handle Flags

in_flatpak = (".var/app" in paths["APP_DATA"])
if ("-n" in sys.argv):
	in_flatpak = True

output_debug = False
if ("-d" in sys.argv):
	output_debug = True

output_links = False
if ("-l" in sys.argv):
	output_links = True

no_logs = False
if ("--nolog" in sys.argv):
	no_logs = True

if ("-h" in sys.argv or "-?" in sys.argv or "--help" in sys.argv):
	print(version_info)
	print("For general help, visit the guide: https://fr75s.github.io/bigscraperqt/guide/index.html\n")

	print("Flag Help:")
	print("-n\t\tForce Native UI")
	print("-d\t\tPrint Debug-level logs to stdout")
	print("-l\t\tPrint Links to stdout (they are not logged)")
	print("--nolog\t\tDo not generate log files")

	print("-style [style]\tUse a different Qt Style (built into PyQt, but useful)")

	sys.exit()


## Logging

if not(os.path.isdir(paths["LOGS"])):
	os.makedirs(paths["LOGS"], exist_ok=True)

if not(no_logs):
	logfile = open(os.path.join(paths["LOGS"], ct_format + ".log"), "a")

log_hist = ["", "", "", "", ""]
def log(msg, prefix="", debug=False, bypassHist=False):
	m = msg
	if not(prefix == ""):
		m = "[" + prefix + "] " + msg
	
	full_loghist = True
	for i in log_hist:
		if (m != i):
			full_loghist = False

	if not(full_loghist and not(bypassHist)):
		
		for i in range(3, -1, -1):
			log_hist.pop(i + 1)
			log_hist.insert(i + 1, log_hist[i])

		log_hist.pop(0)
		log_hist.insert(0, m)
	
		pm = m

		# Colors
		if prefix == "D":
			pm = "\033[37m" + m + "\033[00m"
		if prefix == "L":
			pm = "\033[94m" + m + "\033[00m"
		if prefix == "W":
			pm = "\033[91m" + m + "\033[00m"

		if not(debug) or output_debug:
			print(pm)

	if not(no_logs):
		logfile.write(m + "\n")

def close_log():
	if not(no_logs):
		logfile.close()

atexit.register(close_log)

def log_link(link):
	if output_links:
		print(f"\033[94m[L] {link}\033[00m")

log("Program Init... " + ct[0] + "-" + ct[1] + "-" + ct[2] + " " + ct[3] + ":" + ct[4] + ":" + ct[5], "I")

## String Stuff

stuffkey = "PleaseDoNotUseThisForMaliciousPurposesWhatWouldYouEvenAccomplishWhenYourQuoteJoyEndquoteDoesntMatter"
def stuff(msg):
	msg_chars = []
	stuff_chars = []

	for i in range(0, len(msg)):
		msg_chars.append(ord(msg[i]))
	for i in range(0, len(msg)):
		stuff_chars.append(ord(stuffkey[i]))

	out = ""
	for i in range(0, len(msg)):
		out += str(msg_chars[i] + stuff_chars[i]) + ";"

	out = out[:-1]

	return out

def unstuff(msg):
	enclen = len(msg.split(";"))

	msg_chars = []
	stuff_chars = []

	for i in range(0, enclen):
		msg_chars.append(int(msg.split(";")[i]))
	for i in range(0, enclen):
		stuff_chars.append(ord(stuffkey[i]))

	out = ""
	for i in range(0, enclen):
		out += (chr(msg_chars[i] - stuff_chars[i]))

	return out


## SCRAPING CONVERSIONS & LISTS

# Month Name to Number
calendar_month = {
	"January": "01",
	"February": "02",
	"March": "03",
	"April": "04",
	"May": "05",
	"June": "06",
	"July": "07",
	"August": "08",
	"September": "09",
	"October": "10",
	"November": "11",
	"December": "12"
}

calendar_month_rev = {v: k for k, v in calendar_month.items()}

ad_arts = {
	"image_ingame": ["Screenshot - Gameplay"],
	"image_title": ["Screenshot - Game Title", "Box - Front"],
	"image_marquee": ["Arcade - Marquee"],
	"image_cabinet": ["Arcade - Cabinet"],
	"image_flyer": ["Advertisement Flyer - Front"],
}

# Art title to Pegasus Format
pegasus_artconv = {
	"Arcade - Marquee": ["marquee"],
	"Advertisement Flyer - Front": ["poster"],
	"Box - Front": ["boxFront"],
	"Box - Back": ["boxBack"],
	"Clear Logo": ["logo", "wheel"],
	"Cart - Front": ["cartridge"],
	"Disc": ["cartridge"],
	"Screenshot - Gameplay": ["gameplay", "background", "titlescreen"],
	"Background": ["background"],
	"Screenshot - Game Title": ["titlescreen"],
	"Video": ["video"]
}

# ScreenScraper Art Types to LB Ids
ss_arts = {
	"sstitle": "Screenshot - Game Title",
	"ss": "Screenshot - Gameplay",
	"fanart": "Fanart - Background",
	"screenmarquee": "Arcade - Marquee",
	"wheel": "Clear Logo",
	"box-2D": "Box - Front",
	"box-2D-back": "Box - Back",
	"box-3D": "Box - 3D",
	"support-2D": "Cart - Front" #(ScreenScraper does not differentiate between disc and cartridge, so this will have to suffice)
}

# Extensions that should be ignored when scraping, mostly saves, extra files and metadata
nongame_extensions = [
	".txt",
	".png",
	".jpg",
	".sav",
	".srm",
	".bak",
	".cue"
]


#
# Systems
#

# List of Systems with corresponding system IDs
systems = {
	"Arcade Database": {
		"Arcade": "arcade"
	},
	"LaunchBox": {
		"3DO Interactive Multiplayer": "3do",
		"Amstrad CPC": "amstradcpc",
		"Android": "android",
		"Apple II": "apple2",
		"Apple IIGS": "apple2gs",
		"Apple iOS": "ios",
		"Apple Mac OS": "macintosh",
		"Arcade": "arcade",
		"Atari 2600": "atari2600",
		"Atari 5200": "atari5200",
		"Atari 7800": "atari7800",
		"Atari Jaguar": "atarijaguar",
		"Atari Jaguar CD": "atarijaguarcd",
		"Atari Lynx": "atarilynx",
		"Atari ST": "atarist",
		"Atari XEGS": "atarixe",
		"Bally Astrocade": "astrocade",
		"BBC Microcomputer System": "bbcmicro",
		"Camputers Lynx": "camputerslynx",
		"Coleco ADAM": "adam",
		"ColecoVision": "colecovision",
		"Commodore 128": "c128",
		"Commodore 64": "c64",
		"Commodore Amiga": "amiga",
		"Commodore Amiga CD32": "amigacd32",
		"Commodore CDTV": "amigacdtv",
		"Commodore VIC-20": "vic20",
		"Entex Adventure Vision": "advision",
		"Fairchild Channel F": "channelf",
		"GCE Vectrex": "vectrex",
		"Linux": "linux",
		"Magnavox Odyssey": "odyssey",
		"Magnavox Odyssey 2": "odyssey2",
		"Mattel Intellivision": "intellivision",
		"Memotech MTX512": "mtx512",
		"Microsoft DOS": "dos",
		"Microsoft MSX": "msx",
		"Microsoft MSX2": "msx2",
		"Microsoft Xbox": "xbox",
		"Microsoft Xbox 360": "xbox360",
		"Microsoft Xbox One": "xboxone",
		"NEC PC-Engine": "pcengine",
		"NEC TurboGrafx CD": "turbografxcd",
		"NEC TurboGrafx-16": "turbografx16",
		"Nintendo 3DS": "3ds",
		"Nintendo 64": "n64",
		"Nintendo 64DD": "64dd",
		"Nintendo DS": "nds",
		"Nintendo Entertainment System": "nes",
		"Nintendo Famicom Disk System": "fds",
		"Nintendo Game & Watch": "gameandwatch",
		"Nintendo Game Boy": "gb",
		"Nintendo Game Boy Advance": "gba",
		"Nintendo Game Boy Color": "gbc",
		"Nintendo GameCube": "gc",
		"Nintendo Switch": "switch",
		"Nintendo Virtual Boy": "virtualboy",
		"Nintendo Wii": "wii",
		"Nintendo Wii U": "wiiu",
		"Ouya": "ouya",
		"Philips CD-i": "cdi",
		"Sega 32X": "sega32x",
		"Sega CD": "segacd",
		"Sega Dreamcast": "dreamcast",
		"Sega Game Gear": "gamegear",
		"Sega Genesis": "genesis",
		"Sega Master System": "mastersystem",
		"Sega Mega Drive": "megadrive",
		"Sega Naomi": "naomi",
		"Sega Saturn": "saturn",
		"Sega SG-1000": "sg1000",
		"Sinclair ZX Spectrum": "zxspectrum",
		"SNK Neo Geo AES": "neogeo",
		"SNK Neo Geo Pocket": "ngp",
		"SNK Neo Geo Pocket Color": "ngpc",
		"Sony Playstation": "psx",
		"Sony Playstation 2": "ps2",
		"Sony Playstation 3": "ps3",
		"Sony Playstation 4": "ps4",
		"Sony Playstation Vita": "psvita",
		"Sony PSP": "psp",
		"Super Nintendo Entertainment System": "snes",
		"Texas Instruments TI 99/4A": "ti99",
		"Tiger Game.com": "gamecom",
		"Windows": "windows",
		"WonderSwan": "wonderswan",
		"WonderSwan Color": "wonderswancolor"
	},
	"ScreenScraper": {
		"3DO Interactive Multiplayer": "3do",
		"Amstrad CPC": "amstradcpc",
		"Amstrad GX4000": "gx4000",
		"Apple II": "apple2",
		"Apple MacOS": "macintosh",
		"Atari 2600": "atari2600",
		"Atari 5200": "atari5200",
		"Atari 7800": "atari7800",
		"Atari 800": "atari800",
		"Atari Jaguar": "atarijaguar",
		"Atari Lynx": "atarilynx",
		"Atari ST": "atarist",
		"Atomiswave": "atomiswave",
		"Bally Astrocade": "astrocade",
		"BBC Microcomputer System": "bbcmicro",
		"Capcom Play System": "cps1",
		"Capcom Play System II": "cps2",
		"Capcom Play System III": "cps3",
		"Coleco ADAM": "adam",
		"ColecoVision": "colecovision",
		"Commodore 64": "c64",
		"Commodore Amiga": "amiga",
		"Commodore Amiga CD32": "amigacd32",
		"Commodore Amiga CDTV": "amigacdtv",
		"Commodore VIC-20": "vic20",
		"Fairchild Channel F": "channelf",
		"GCE Vectrex": "vectrex",
		"Linux": "linux",
		"Magnavox Odyssey 2": "odyssey2",
		"MAME": "mame",
		"Mattel Intellivision": "intellivision",
		"Microsoft DOS": "dos",
		"Microsoft MSX": "msx",
		"Microsoft MSX2": "msx2",
		"Microsoft Windows 3.X": "win3x",
		"Microsoft Windows 9x": "win9x",
		"Microsoft Windows": "windows",
		"Microsoft Xbox": "xbox",
		"Microsoft Xbox 360": "xbox360",
		"Microsoft Xbox One": "xboxone",
		"NEC PC Engine SuperGrafx": "supergrafx",
		"NEC PC-FX": "pcfx",
		"NEC TurboGrafx-16": "turbografx16",
		"Nintendo 3DS": "3ds",
		"Nintendo 64": "n64",
		"Nintendo 64DD": "64dd",
		"Nintendo DS": "nds",
		"Nintendo Entertainment System": "nes",
		"Nintendo Famicom Disk System": "fds",
		"Nintendo Game & Watch": "gameandwatch",
		"Nintendo Game Boy": "gb",
		"Nintendo Game Boy Color": "gbc",
		"Nintendo Game Boy Advance": "gba",
		"Nintendo GameCube": "gc",
		"Nintendo Pokemon Mini": "pokemini",
		"Nintendo Switch": "switch",
		"Nintendo Virtual Boy": "virtualboy",
		"Nintendo Wii": "wii",
		"Nintendo Wii U": "wiiu",
		"Nokia N-Gage": "ngage",
		"Oric Atmos": "oric",
		"Philips CD-i": "cdi",
		"Pico-8": "pico8",
		"Sega 32X": "sega32x",
		"Sega CD": "segacd",
		"Sega Dreamcast": "dreamcast",
		"Sega Game Gear": "gamegear",
		"Sega Genesis": "genesis",
		"Sega Master System": "mastersystem",
		"Sega Model II": "model2",
		"Sega Model III": "model3",
		"Sega Naomi": "naomi",
		"Sega Naomi 2": "naomi2",
		"Sega Saturn": "saturn",
		"Sega SG-1000": "sg1000",
		"Sharp X1": "x1",
		"Sharp X68000": "x68000",
		"Sinclair ZX-81": "zx81",
		"Sinclair ZX Spectrum": "zxspectrum",
		"SNK Neo Geo": "neogeo",
		"SNK Neo Geo CD": "neogeocd",
		"SNK Neo Geo MVS": "neogeomvs",
		"SNK Neo Geo Pocket": "ngp",
		"SNK Neo Geo Pocket Color": "ngpc",
		"Sony Playstation": "psx",
		"Sony Playstation 2": "ps2",
		"Sony Playstation 3": "ps3",
		"Sony Playstation 4": "ps4",
		"Sony Playstation Vita": "psvita",
		"Sony PSP": "psp",
		"Super Nintendo Entertainment System": "snes",
		"Texas Instruments TI 99/4A": "ti99",
		"TIC-80": "tic80",
		"Tiger Game.com": "gamecom",
		"Uzebox": "uzebox",
		"Watara Supervision": "supervision",
		"WonderSwan": "wonderswan",
		"WonderSwan Color": "wonderswancolor",
	}
}

# LaunchBox systems to ID numbers
lb_sysid = {
		"3do": "1-3do-interactive-multiplayer",
	"amiga": "2-commodore-amiga",
	"amstradcpc": "3-amstrad-cpc",
	"android": "4-android",
	"arcade": "5-arcade",
	"atari2600": "6-atari-2600",
	"atari5200": "7-atari-5200",
	"atari7800": "8-atari-7800",
	"atarijaguar": "9-atari-jaguar",
	"atarijaguarcd": "10-atari-jaguar-cd",
	"atarilynx": "11-atari-lynx",
	"atarixe": "12-atari-xegs",
	"atarist": "76-atari-st",
	"colecovision": "13-colecovision",
	"adam": "117-coleco-adam",
	"c64": "14-commodore-64",
	"c128": "118-commodore-128",
	"amigacd32": "119-commodore-amiga-cd32",
	"amigacdtv": "120-commodore-cdtv",
	"vic20": "122-commodore-vic-20",
	"intellivision": "15-mattel-intellivision",
	"ios": "16-apple-ios",
	"macintosh": "17-apple-mac-os",
	"vectrex": "125-gce-vectrex",
	"xbox": "18-microsoft-xbox",
	"xbox360": "19-microsoft-xbox-360",
	"xboxone": "20-microsoft-xbox-one",
	"dos": "83-ms-dos",
	"msx": "82-microsoft-msx",
	"msx2": "190-microsoft-msx2",
	"windows": "84-windows",
	"linux": "218-linux",
	"ngp": "21-snk-neo-geo-pocket",
	"ngpc": "22-snk-neo-geo-pocket-color",
	"neogeo": "23-snk-neo-geo-aes",
	"3ds": "24-nintendo-3ds",
	"n64": "25-nintendo-64",
	"64dd": "194-nintendo-64dd",
	"nds": "26-nintendo-ds",
	"nes": "27-nintendo-entertainment-system",
	"fds": "157-nintendo-famicom-disk-system",
	"snes": "53-super-nintendo-entertainment-system",
	"gameandwatch": "166-nintendo-game-watch",
	"gb": "28-nintendo-game-boy",
	"gba": "29-nintendo-game-boy-advance",
	"gbc": "30-nintendo-game-boy-color",
	"gc": "31-nintendo-gamecube",
	"virtualboy": "32-nintendo-virtual-boy",
	"wii": "33-nintendo-wii",
	"wiiu": "34-nintendo-wii-u",
	"switch": "211-nintendo-switch",
	"ouya": "35-ouya",
	# 36 is skipped lol
	"cdi": "37-philips-cd-i",
	"sega32x": "38-sega-32x",
	"segacd": "39-sega-cd",
	"dreamcast": "40-sega-dreamcast",
	"gamegear": "41-sega-game-gear",
	"genesis": "42-sega-genesis",
	"megadrive": "42-sega-genesis",
	"mastersystem": "43-sega-master-system",
	"naomi": "99-sega-naomi",
	"saturn": "45-sega-saturn",
	"sg1000": "80-sega-sg-1000",
	"zxspectrum": "46-sinclair-zx-spectrum",
	"psx": "47-sony-playstation",
	"ps2": "48-sony-playstation-2",
	"ps3": "49-sony-playstation-3",
	"ps4": "50-sony-playstation-4",
	"psvita": "51-sony-playstation-vita",
	"psp": "52-sony-psp",
	"ti99": "149-texas-instruments-ti-994a",
	"turbografx16": "54-nec-turbografx-16",
	"turbografxcd": "163-nec-turbografx-cd",
	"pcengine": "54-nec-turbografx-16",
	"wonderswan": "55-wonderswan",
	"wonderswancolor": "56-wonderswan-color",
	"odyssey2": "57-magnavox-odyssey-2",
	"odyssey": "78-magnavox-odyssey",
	"channelf": "58-fairchild-channel-f",
	"gamecom": "63-tiger-gamecom",
	"apple2": "111-apple-ii"
}

sc_sysid = {
	"3do": 29,
	"amstradcpc": 65,
	"gx4000": 87,
	"apple2": 86,
	"macintosh": 146,
	"atari2600": 26,
	"atari5200": 40,
	"atari7800": 41,
	"atari800": 43,
	"atarijaguar": 27,
	"atarilynx": 28,
	"atarist": 42,
	"atomiswave": 53,
	"astrocade": 44,
	"bbcmicro": 37,
	"cps1": 6,
	"cps2": 7,
	"cps3": 8,
	"adam": 89,
	"colecovision": 48,
	"c64": 66,
	"amiga": 64,
	"amigacd32": 130,
	"amigacdtv": 129,
	"vic20": 73,
	"channelf": 80,
	"vectrex": 102,
	"linux": 145,
	"odyssey2": 104,
	"mame": 75,
	"intellivision": 115,
	"dos": 135,
	"msx": 113,
	"msx": 116,
	"win3x": 136,
	"win9x": 137,
	"windows": 138,
	"xbox": 32,
	"xbox360": 33,
	"xboxone": 34,
	"supergrafx": 105,
	"pcfx": 72,
	"turbografx16": 31,
	"3ds": 17,
	"n64": 14,
	"64dd": 122,
	"nds": 15,
	"fds": 106,
	"gameandwatch": 52,
	"gb": 9,
	"gbc": 10,
	"gba": 12,
	"gc": 13,
	"nes": 3,
	"pokemini": 211,
	"switch": 225,
	"virtualboy": 11,
	"wii": 16,
	"wiiu": 18,
	"snes": 4,
	"ngage": 30,
	"oric": 131,
	"cdi": 133,
	"pico8": 234,
	"sega32x": 19,
	"segacd": 20,
	"dreamcast": 23,
	"gamegear": 21,
	"genesis": 1,
	"mastersystem": 2,
	"model2": 54,
	"model3": 55,
	"naomi": 56,
	"naomi2": 230,
	"saturn": 22,
	"sg1000": 109,
	"x1": 220,
	"x68000": 79,
	"zx81": 77,
	"zxspectrum": 76,
	"neogeo": 142,
	"neogeomvs": 68,
	"neogeocd": 70,
	"ngp": 25,
	"ngpc": 82,
	"psx": 57,
	"ps2": 58,
	"ps3": 59,
	"ps4": 60,
	"psp": 61,
	"psvita": 62,
	"ti99": 205,
	"tic80": 222,
	"gamecom": 121,
	"uzebox": 216,
	"supervision": 207,
	"wonderswan": 45,
	"wonderswancolor": 46
}

# Valid Export Platforms
explats = {
	"Pegasus Frontend": "pegasus",
	"Pegasus Frontend (Lutris IDs)": "lpegasus",
	"EmulationStation": "es"
}
