import os, sys, datetime, unidecode
from xdg import xdg_data_home, xdg_config_home
from yt_dlp import YoutubeDL

from PyQt5.QtCore import *

## Genral Information
info = {
	"NAME": "bigscraper-qt",
	"VERSION": "1.2.0",
	"AUTHOR": "Fr75s",
	"LICENSE": "GPLv3",
	"URL": ""
}

version_info = info["NAME"] + " v" + info["VERSION"] + ". Made by " + info["AUTHOR"] + ". Licensed under " + info["LICENSE"]

# Paths for saving configs
paths = {
	"DATA": xdg_data_home(),
	"APP_DATA": os.path.join(xdg_data_home(), "bigscraper-qt/"),
	"METADATA": os.path.join(xdg_data_home(), "bigscraper-qt/metadata/"),
	"MEDIA": os.path.join(xdg_data_home(), "bigscraper-qt/media/"),
	"LOGS": os.path.join(xdg_data_home(), "bigscraper-qt/logs/"),
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

## Define some useful functions

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

	# Remove Accents (REQUIRES UNIDECODE)
	out = u"" + out
	out = unidecode.unidecode(out)

	# Numerous Character Replacements
	return out.upper().strip(" ").replace(" -","").replace(": ","_").replace(" ","_").replace(":","_").replace("-","_").replace(".","").replace("!","").replace("?","").replace("'","").replace("&","AND")

# Remove Extension from file names
def trimext(text):
	postdot = text[(text.rfind(".") + 1):]

	while (len(postdot) <= 4 and text.rfind(".") >= 0):
		text = text[0:text.rfind(".")]
		if (text.rfind(".") >= 0):
			postdot = text[(text.rfind(".") + 1):]

	return text

def video_len_test(info, *, incomplete):
	video_duration = info.get("duration")
	if video_duration and video_duration > VIDEO_LEN_LIMIT:
		return "Sorry, too long"

# Download Video
def download_video(url, options):
	with YoutubeDL(options) as video_downloader:
		err = video_downloader.download(url)



## Define a few values for the scripts

# OPTIONS
options = {
	"video": True,
	"videoOverLimit": False,
	"region": "na",
	"glassyTitle": True,
	"recache": False
}

regions = {
	"na": ["(North America)", "(United States)", "(Canada)", "(World)"],
	"eu": ["(Europe)", "(United Kingdom)", "(Germany)", "(France)", "(Spain)", "(Italy)", "(The Netherlands)", "(Russia)", "(World)"],
	"jp": ["(Japan)", "(World)", ""]
}

## Handle Flags

in_flatpak = (".var/app" in paths["APP_DATA"])
if ("-n" in sys.argv):
	in_flatpak = True

output_debug = False
if ("-d" in sys.argv):
	output_debug = True

no_logs = False
if ("--nolog" in sys.argv):
	no_logs = True

if ("-h" in sys.argv or "-?" in sys.argv or "--help" in sys.argv):
	print(version_info)
	print("For general help, visit the guide: https://fr75s.github.io/bigscraperqt/guide/index.html\n")

	print("Flag Help:")
	print("-n\tForce Native UI")
	print("-d\tPrint Debug-level logs to stdout")
	print("--nolog\tDo not generate log files")

	sys.exit()


## Logging

if not(os.path.isdir(paths["LOGS"])):
	os.makedirs(paths["LOGS"], exist_ok=True)

if not(no_logs):
	logfile = open(os.path.join(paths["LOGS"], ct_format + ".log"), "a")
def log(msg, prefix="", debug=False):
	m = msg
	if not(prefix == ""):
		m = "[" + prefix + "] " + msg

	if not(debug) or output_debug:
		print(m)

	if not(no_logs):
		logfile.write(m + "\n")

log("Init Logging... " + ct[0] + "-" + ct[1] + "-" + ct[2] + " " + ct[3] + ":" + ct[4] + ":" + ct[5], "I")


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

# Art title to Pegasus Format
pegasus_artconv = {
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

# Converting system names to abbreviations
convert = {
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
    "Memotech MTX512": "mxt512",
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
}

# Converting system abbreviations to names
convert_rev = {val: key for key, val in convert.items()}

# Converting system abbreviations to IDs used by Launchbox
cv_id = {
	"3do": "1",
	"amiga": "2",
	"amstradcpc": "3",
	"android": "4",
	"arcade": "5",
	"atari2600": "6",
	"atari5200": "7",
	"atari7800": "8",
	"atarijaguar": "9",
	"atarijaguarcd": "10",
	"atarilynx": "11",
	"atarixe": "12",
	"atarist": "76",
	"colecovision": "13",
	"adam": "117",
	"c64": "14",
	"c128": "118",
	"amigacd32": "119",
	"amigacdtv": "120",
	"vic20": "122",
	"intellivision": "15",
	"ios": "16",
	"macintosh": "17",
	"vectrex": "125",
	"xbox": "18",
	"xbox360": "19",
	"xboxone": "20",
	"dos": "83",
	"msx": "82",
	"msx2": "190",
	"windows": "84",
	"linux": "218",
	"ngp": "21",
	"ngpc": "22",
	"neogeo": "23",
	"3ds": "24",
	"n64": "25",
	"64dd": "194",
	"nds": "26",
	"nes": "27",
	"fds": "157",
	"snes": "53",
	"gameandwatch": "166",
	"gb": "28",
	"gba": "29",
	"gbc": "30",
	"gc": "31",
	"virtualboy": "32",
	"wii": "33",
	"wiiu": "34",
	"switch": "211",
	"ouya": "35",
	"cdi": "37",
	"sega32x": "38",
	"segacd": "39",
	"dreamcast": "40",
	"gamegear": "41",
	"genesis": "42",
	"megadrive": "42",
	"mastersystem": "43",
	"naomi": "99",
	"saturn": "45",
	"sg1000": "80",
	"zxspectrum": "46",
	"psx": "47",
	"ps2": "48",
	"ps3": "49",
	"ps4": "50",
	"psvita": "51",
	"psp": "52",
	"ti99": "149",
	"turbografx16": "54",
	"turbografxcd": "163",
	"pcengine": "54",
	"wonderswan": "55",
	"wonderswancolor": "56",
	"odyssey2": "57",
	"odyssey": "78",
	"channelf": "58",
	"gamecom": "63",
	"apple2": "Apple II"
}

# Valid Export Platforms
explats = {
	"Pegasus Frontend": "pegasus",
	"EmulationStation": "es"
}
