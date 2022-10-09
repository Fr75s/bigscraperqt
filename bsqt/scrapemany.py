# scrapemany

## Scrapes all games in a specified folder

import os, sys, json, zlib, shutil, hashlib, requests
from lxml import html

from .const import *

from PyQt5.QtCore import *

class ScrapeTask(QObject):
	complete = pyqtSignal()
	out = pyqtSignal(str)

	bar = pyqtSignal(int, int, int)

	data = []
	options_loc = []

	# Scraper Specifics

	ss_stopall = False
	ss_maxthreads = 1

	# Functions
	def __init__(self, data_i, opt_main):
		super().__init__()
		self.data = data_i
		self.options_loc = opt_main

	def video_progress_hook(self, d):
		if d["status"] == "downloading":
			downloaded = d["downloaded_bytes"]

			total = None
			if ("total_bytes" in d):
				total = d["total_bytes"]
			elif ("total_bytes_estimate" in d):
				total = d["total_bytes_estimate"]

			if not(total == None):
				self.bar.emit(1, 1, 0)
				self.bar.emit(3, downloaded, total)
		if d["status"] == "finished":
			self.bar.emit(1, 0, 0)

	def run(self):

		self.out.emit("Starting...")

		log("Data is " + str(self.data), "I")
		log("Will write to " + paths["APP_DATA"], "I")

		#
		# #   #   # #
		# #   ###  #
		# ### ### # #
		#
		if (self.options_loc["module"] == "LaunchBox"):

			log("Scraping from LaunchBox", "I")

			# Get system
			system_name = self.data[1]
			system = systems["LaunchBox"][self.data[1]]

			# Get game folder
			in_folder = self.data[0].replace("file://", "")

			# Get valid games in folder
			# Get valid games in folder
			game_files = []
			game_names = []
			for f in os.listdir(in_folder):
				validFile = True
				if not("." in f):
					validFile = False
				else:
					for ext in nongame_extensions:
						if f.endswith(ext):
							validFile = False
							break
				if (validFile):
					game_name_format = form(trimext(os.path.basename(f)))

					# If the file doesn't exist or recache mode is on, you can scrape
					if (not(os.path.isfile(os.path.join(paths["METADATA"], system) + "/" + game_name_format + ".json")) or self.options_loc["recache"]):
						game_files.append(os.path.join(in_folder, f))
						game_names.append(game_name_format)

			log("Data formatted to " + str([game_names, game_files, system]), "I")



			# Create Folders if necessary
			if not(os.path.isdir(os.path.join(paths["METADATA"], system))):
				log("Creating metadata path for " + system, "D", True)
				os.makedirs(os.path.join(paths["METADATA"], system), exist_ok=True)

			for g in game_names:
				# Iterate through each game's name for file creation to make it *organized*
				if not(os.path.isdir(os.path.join(paths["MEDIA"], system, g))):
					log("Creating media path for " + g, "D", True)
					os.makedirs(os.path.join(paths["MEDIA"], system, g), exist_ok=True)



			# BEGIN
			# Prepare for page downloading
			current_page = 1
			games_found = 0

			page_after_all_alphabetically = False

			# Check if any valid games are in folder
			if not(len(game_names) == 0):
				# Download 1st Page
				self.out.emit("Getting Page " + str(current_page))
				self.bar.emit(0, 1, 0)
				page = requests.get("https://gamesdb.launchbox-app.com/platforms/games/" + lb_sysid[system] + "|" + str(current_page), timeout=15)
				log("Page Request Successful", "D", True)
				pagetree = html.fromstring(page.content)
				page_games = pagetree.xpath('//a[@class="list-item"]')

				while (len(page_games) > 0) and not(page_after_all_alphabetically) and (games_found < len(game_names)):

					# Scan through each text item
					log("Parsing Website Data", "I")
					game_titles = pagetree.xpath("//div[@class='col-sm-10']/h3[1]/text()")
					game_titles_format = []

					# Format game titles
					for t in game_titles:
						game_titles_format.append(form(t))

					if (sorted(game_titles_format)[0] > sorted(game_names)[-1]):
						page_after_all_alphabetically = True

					if not(page_after_all_alphabetically):
						# Check for games that match any in the games list
						for g in game_names:
							if (g in game_titles_format):

								# Clear image folder if recache is on
								if (os.path.isdir(os.path.join(paths["MEDIA"], system, g)) and self.options_loc["recache"]):
									log("Resetting media directory for " + g + " (recache mode on)", "I")
									shutil.rmtree(os.path.join(paths["MEDIA"], system, g))
									os.makedirs(os.path.join(paths["MEDIA"], system, g), exist_ok=True)

								games_found += 1
								self.out.emit("Getting details for " + g + " (" + str(games_found) + " of " + str(len(game_names)) + ")")

								game_index = game_titles_format.index(g)
								details_link = "https://gamesdb.launchbox-app.com" + pagetree.xpath('//a[@class="list-item"]/@href')[game_index]
								database_id = details_link.rsplit('/', 1)[-1]
								images_link = "https://gamesdb.launchbox-app.com/games/images/" + database_id

								# Get details page
								log("Attempting to get Details Page", "I")
								details_page = requests.get(details_link)
								log("Page Request Successful", "D", True)
								details = html.fromstring(details_page.content)

								# Initialize metadata object
								meta = {}
								meta["File"] = game_files[game_names.index(g)]

								# Get details from page
								info = details.xpath('//td[@class="row-header"]/text()')
								for i in info:
									# Standard
									if i in ("Name", "Platform", "Release Date", "Game Type", "ESRB", "Max Players", "Cooperative"):
										log("Adding " + i + " to metadata", "D", True)
										meta[i] = details.xpath('//td[@class="row-header" and text()="' + i + '"]/../td[2]/span[1]/text()')
									# Links
									if i in ("Developers", "Publishers", "Genres", "Wikipedia", "Video Link"):
										log("Adding " + i + " to metadata", "D", True)
										meta[i] = details.xpath('//td[@class="row-header" and text()="' + i + '"]/../td[2]/span[1]/a/text()')
									# Overview Text Block
									if i in ("Overview"):
										log("Adding " + i + " to metadata", "D", True)
										meta[i] = details.xpath('//div[@class="view"]/text()')
									# Rating
									if i in ("Rating"):
										log("Adding " + i + " to metadata", "D", True)
										meta[i] = details.xpath('//span[@id="communityRating"]/text()')

								## Image Downloads
								# Get Images page
								self.out.emit("Getting Images Page for " + meta["Name"][0])
								images_page = requests.get(images_link)
								log("Page Request Successful", "D", True)
								images = html.fromstring(images_page.content)

								# Get links and corresponding titles
								image_links = images.xpath('//a[contains(@href, "https://images.launchbox-app.com")]/@href')
								image_titles = images.xpath('//a[contains(@href, "https://images.launchbox-app.com")]/@data-title')

								# Download each image
								index = 0
								self.out.emit("Downloading Images For " + meta["Name"][0])
								self.bar.emit(1, 1, 0)
								for link in image_links:
									# Get link
									image_title = image_titles[index]

									# Download the image
									#self.out.emit("Downloading Image " + str(index + 1) + " of " + str(len(image_links)) + " for " + meta["Name"][0])

									# Don't crash if the image can't download
									try:
										log("Attempting Image Download", "D", True)
										image = requests.get(link, timeout=15)
										log("Request Successful, Writing to file", "D", True)

										# Write to file
										open(os.path.join(paths["MEDIA"], system, g) + "/" + image_title + ".png", "wb").write(image.content)
									except Exception as e:
										log("Image Download Failed: " + str(e), "E")
										self.out.emit("Image " + str(index + 1) + " couldn't Download.")

									index += 1
									self.bar.emit(3, index + 1, len(image_links))
								self.bar.emit(1, 0, 0)

								# List image titles in metadata
								meta["Images"] = (image_titles if len(image_titles) > 0 else ["NULL"])



								## Video Downloads
								if self.options_loc["video"] and meta["Video Link"]:
									# Option is set: Download video

									dl_options = {
										"match_filter": video_len_test,
										"outtmpl": os.path.join(paths["MEDIA"], system, g) + "/" + meta["Name"][0] + " - Video.%(ext)s",
										"progress_hooks": [self.video_progress_hook]
									}

									self.out.emit("Attempting Video Download")
									try:
										download_video(meta["Video Link"][0], dl_options)
									except Exception as e:
										log("Video Download Failed: " + str(e), "E")
										self.out.emit("Couldn't Download Video")

								# Write Metadata
								meta_json = json.dumps(meta, indent = 4)
								log("Writing Metadata to File", "D", True)
								open(os.path.join(paths["METADATA"], system) + "/" + g + ".json", "w").write(meta_json)

								self.out.emit("Collection Complete for " + g + " (" + str(games_found) + " of " + str(len(game_names)) + ")")
								self.bar.emit(2, games_found, len(game_names))

						current_page += 1
						self.out.emit("Getting Page " + str(current_page))

						try:
							page = requests.get("https://gamesdb.launchbox-app.com/platforms/games/" + lb_sysid[system] + "|" + str(current_page), timeout=15)
							log("Page Request Successful", "D", True)
						except Exception as e:
							current_page -= 1
							log("Couldn't Fetch Page: " + str(e), "E")
						pagetree = html.fromstring(page.content)
						page_games = pagetree.xpath('//a[@class="list-item"]')

				self.bar.emit(0, 0, 0)
				self.out.emit("Process Complete: Found " + str(games_found) + " of " + str(len(game_names)) + " Games. Exiting...")

			else:
				log("No Unscraped Games In Folder", "I")
				self.out.emit("No unscraped games in this folder. Exiting...")

		#
		# ### ##  #
		# ### # # ###
		# # # ##  ###
		#
		elif (self.options_loc["module"] == "Arcade Database"):

			log("Scraping from Arcade Database", "I")

			# Get the MAME game ID from the filename (filename needs to be the mame game id)
			in_file = self.data[0].replace("file://", "")
			mame_id = form(trimext(os.path.basename(in_file)))

			# Get the system
			system = systems["Arcade Database"][self.data[1]]

			# Get game folder
			in_folder = self.data[0].replace("file://", "")

			# Get valid games in folder
			game_files = []
			for f in os.listdir(in_folder):
				validFile = True
				if not("." in f):
					validFile = False
				else:
					for ext in nongame_extensions:
						if f.endswith(ext):
							validFile = False
							break
				if (validFile):
					game_files.append(os.path.join(in_folder, f))

			game_names = []
			for f in game_files:
				mame_id = form(trimext(os.path.basename(f)))

				if (os.path.isfile(os.path.join(paths["EXTRA"], "adb.json")) and not self.options_loc["recache"]):
					log("Checking adb.json", "D", True)
					adb = json.load(open(os.path.join(paths["EXTRA"], "adb.json")))

					if not(mame_id in adb):
						game_names.append(mame_id)
				else:
					game_names.append(mame_id)

			log("Data formatted to " + str([game_names, game_files, system]), "I")



			# Only scrape if there are games to scrape
			if len(game_names) > 0:
				# Create Metadata folder if necessary
				if not(os.path.isdir(os.path.join(paths["METADATA"], system))):
					log("Creating metadata path for " + system, "D", True)
					os.makedirs(os.path.join(paths["METADATA"], system), exist_ok=True)

				# Create Media paths and generate links
				game_urls = []
				combi_string = "http://adb.arcadeitalia.net/service_scraper.php?ajax=query_mame&game_name="
				for g in game_names:
					# Also combine each game name into a single URL string for the request, splitting this if there are too many characters
					if len(combi_string + g + ";") > 800:
						game_urls.append(combi_string)
						combi_string = "http://adb.arcadeitalia.net/service_scraper.php?ajax=query_mame&game_name=" + g + ";"
					else:
						combi_string = combi_string + g + ";"

				game_urls.append(combi_string)


				total_games = len(game_names)
				games_downloaded = 0

				index = 0

				self.bar.emit(0, 1, 0)
				self.bar.emit(2, games_downloaded, total_games)

				add_to_adb = []
				for url in game_urls:
					index += 1

					log("Attempting to get page " + url, "I")
					try:
						self.out.emit("Getting Data Page " + str(index))
						page = requests.get(url, timeout=15)
						log("Page Request Successful", "D", True)
					except Exception as e:
						self.out.emit("Couldn't Get the game page")
						log(f"ERROR: {e}", "D", True)
						self.bar.emit(0, 0, 0)
						self.complete.emit()

					page_content = page.json()

					for game_meta in page_content["result"]:
						# Start Filtering metadata into format
						self.out.emit("Getting Data For " + game_meta["short_title"])
						meta = {}
						for f in game_files:
							if game_meta["game_name"] in f:
								meta["File"] = f

						# Basic Information
						meta["Name"] = [game_meta["short_title"]]
						meta["Platform"] = ["Arcade"]
						meta["Release Date"] = [game_meta["year"]] # There's already support for year-only release dates, no concern there

						# Developers, Publishers, Genres
						meta["Developers"] = [game_meta["manufacturer"]]
						meta["Publishers"] = [game_meta["manufacturer"]]
						meta["Genres"] = game_meta["genre"].split(" / ")

						# More Basic Info
						meta["Max Players"] = [str(game_meta["players"])]

						real_rating = game_meta["rate"] / 20
						if (real_rating > 0):
							meta["Rating"] = [str(real_rating)]

						meta["Video Link"] = ["https://youtu.be/" + game_meta["youtube_video_id"]]
						meta["Overview"] = [game_meta["history"]]

						game_name = form(meta["Name"][0])


						# Make Image Folders
						# Clear everything if recache on
						if (self.options_loc["recache"]):
							log("Resetting media directory for " + game_name + " (recache mode on)", "I")
							shutil.rmtree(os.path.join(paths["MEDIA"], system, game_name))
							os.makedirs(os.path.join(paths["MEDIA"], system, game_name), exist_ok=True)

						if not(os.path.isdir(os.path.join(paths["MEDIA"], system, game_name))):
							log("Creating media path for " + game_name, "D", True)
							os.makedirs(os.path.join(paths["MEDIA"], system, game_name), exist_ok=True)

						images_completed = 0
						current_image = 1
						total_images = len(list(ad_arts.keys()))
						images = []

						# Uses ad_arts to simplify the process, viewable in const.py
						self.bar.emit(1, 1, 0)
						for art in ad_arts:
							try:
								image = requests.get(game_meta["url_" + art], timeout=15)
								log("Request Successful, Writing to file", "D", True)
								# Write to file
								for out_art in ad_arts[art]:
									image_title = meta["Name"][0] + " - " + out_art
									open(os.path.join(paths["MEDIA"], system, game_name) + "/" + image_title + ".png", "wb").write(image.content)

									images.append(image_title)

									log(f"Write Successful for {out_art}", "D", True)

								images_completed += 1
								self.bar.emit(3, images_completed, total_images)
							except Exception as e:
								self.out.emit(f"Error Ocurred while Downloading Image {current_image}")
								total_images -= 1
								log(f"ERROR: {e}", "D", True)

							current_image += 1
						self.bar.emit(1, 0, 0)

						meta["Images"] = images



						# Get Video
						if self.options_loc["video"] and "Video Link" in meta:
							dl_options = {
								"match_filter": video_len_test,
								"outtmpl": os.path.join(paths["MEDIA"], system, game_name) + "/" + meta["Name"][0] + " - Video.%(ext)s",
								"progress_hooks": [self.video_progress_hook]
							}

							self.out.emit("Attempting Video Download")
							try:
								download_video(meta["Video Link"][0], dl_options)
							except Exception as e:
								log("Video Download Failed: " + str(e), "E")
								self.out.emit("Couldn't Download Video")
						self.bar.emit(1, 0, 0)


						# Queue for adding to adb.json
						add_to_adb.append(form(game_meta["game_name"]))

						# Write Output
						meta_json = json.dumps(meta, indent = 4)
						log("Writing Metadata to File", "D", True)
						open(os.path.join(paths["METADATA"], system) + "/" + game_name + ".json", "w").write(meta_json)

						games_downloaded += 1
						self.bar.emit(2, games_downloaded, total_games)

				# Write IDs to adb.json
				if (os.path.isfile(os.path.join(paths["EXTRA"], "adb.json"))):
					log("Adding to ADB Scraped Games list", "D", True)
					adb = json.load(open(os.path.join(paths["EXTRA"], "adb.json")))

					for mame_id in add_to_adb:
						if not(mame_id in adb):
							adb.append(mame_id)

					adb_json = json.dumps(adb, indent = 4)
					open(os.path.join(paths["EXTRA"], "adb.json"), "w").write(adb_json)
					log("Saved ADB Scraped Games list to file", "D", True)
				else:
					log("Creating ADB Scraped Games list", "D", True)
					adb_json = json.dumps(add_to_adb, indent = 4)

					open(os.path.join(paths["EXTRA"], "adb.json"), "w").write(adb_json)
					log("Saved ADB Scraped Games list to file", "D", True)

				self.out.emit("Process Complete. Exiting...")

			else:
				log("No Games to Scrape.", "I")
				self.out.emit("All Games Already Scraped. Exiting...")

			self.bar.emit(0, 0, 0)

		#
		#  ## ###  ##
		#  #  #    #
		# ##  ### ##
		#
		elif (self.options_loc["module"] == "ScreenScraper"):

			log("Scraping from ScreenScraper", "I")

			in_folder = self.data[0].replace("file://", "")
			self.ss_stopall = False

			system_full = self.data[1]
			system = systems["ScreenScraper"][self.data[1]]
			system_id = sc_sysid[system]

			# Get valid games in folder
			game_files = []
			game_names = []
			for f in os.listdir(in_folder):
				validFile = True
				if not("." in f):
					validFile = False
				else:
					for ext in nongame_extensions:
						if f.endswith(ext):
							validFile = False
							break
				if (validFile):
					game_name_format = form(trimext(os.path.basename(f)))

					# If the file doesn't exist or recache mode is on, you can scrape
					if (not(os.path.isfile(os.path.join(paths["METADATA"], system) + "/" + game_name_format + ".json")) or self.options_loc["recache"]):
						game_files.append(os.path.join(in_folder, f))
						game_names.append(game_name_format)

			log("Data formatted to " + str([game_names, game_files, system, system_id]), "I")

			# Create Folders if necessary
			if not(os.path.isdir(os.path.join(paths["METADATA"], system))):
				log("Creating metadata path for " + system, "D", True)
				os.makedirs(os.path.join(paths["METADATA"], system), exist_ok=True)

			for g in game_names:
				# Iterate through each game's name for file creation to make it *organized*
				if not(os.path.isdir(os.path.join(paths["MEDIA"], system, g))):
					log("Creating media path for " + g, "D", True)
					os.makedirs(os.path.join(paths["MEDIA"], system, g), exist_ok=True)



			# and BEGIN

			# Quick User Check

			# Get the Username and Password of the user, set in the options which is transferred here
			urlUserPass = ""

			if (self.options_loc["screenScraperUser"] != "" and self.options_loc["screenScraperPass"] != ""):
				urlUserPass = "&ssid=" + self.options_loc["screenScraperUser"] + "&sspassword=" + self.options_loc["screenScraperPass"]

			url_base = "https://www.screenscraper.fr/api2/jeuInfos.php?devid=Fr75s&devpassword=" + unstuff("169;216;221;197;183;184;141;180;163;214;234") + "&softname=bigscraperqt&output=json" + urlUserPass

			# Scrape Games
			if not(len(game_names) == 0):
				idx = 0
				self.bar.emit(0, 1, 0)
				self.bar.emit(1, 0, len(game_names))

				for game_name in game_names:
					game_file = game_files[idx]

					#
					# Ideally, this would be where I would be handling multithreaded scraping.
					# I need to figure out how it works, however, which might require significant change to the program.
					# For now, this small thing is how it is. :(
					#

					log(f"Scraping For {game_name}", "I")
					self.screenscraper(game_name, game_file, url_base, [system_id, system, system_full])

					idx += 1
					self.bar.emit(2, idx, len(game_names))

				self.out.emit("Scraping Complete. Exiting...")

			else:
				log("No Unscraped Games In Folder", "I")
				self.out.emit("No unscraped games in this folder. Exiting...")

		self.complete.emit()




	# Actual Scraping functions can go here,
	# Typically for use with multithreading (**later**)

	def screenscraper(self, game_name, game_path, baseurl, system_info):

		continue_scrape = True

		# Get the necessary file details to ensure the game is scraped correctly

		# A) File Size
		game_size = os.path.getsize(game_path)
		infoappend = ""
		if (game_size > 128000000):
			infoappend = "(This may take a while)"

		# MD5
		self.out.emit(f"Processing MD5 Hash (1/3) for {game_name} {infoappend}...")
		hash_md5 = hashlib.md5(open(game_path, 'rb').read()).hexdigest()
		log(f"MD5 Hash: {hash_md5}", "D", True)

		# SHA1
		self.out.emit(f"Processing SHA1 Hash (2/3) for {game_name} {infoappend}...")
		hash_sha1 = hashlib.sha1(open(game_path, 'rb').read()).hexdigest()
		log(f"SHA1 Hash: {hash_sha1}", "D", True)

		# CRC32
		self.out.emit(f"Processing CRC32 Hash (3/3) for {game_name} {infoappend}...")
		hash_crc32 = zlib.crc32(open(game_path, 'rb').read())
		log(f"CRC32 Hash: {hash_crc32}, CRC32 Hex-Formatted Hash: {hex(hash_crc32)[2:]}", "D", True)



		# Generate URL
		url = baseurl + "&crc=" + hex(hash_crc32)[2:] + "&md5=" + hash_md5 + "&sha1=" + hash_sha1 + "&systemeid=" + str(system_info[0]) + "&romtype=rom&romnom=" + os.path.basename(game_path) + "&romtaille=" + str(game_size)

		if not(self.ss_stopall):
			log(f"Attempting to get page for {game_name}", "I")
			try:
				self.out.emit(f"Getting Metadata Page For {game_name}")
				page = requests.get(url, timeout=15)
				log("Page Request Successful", "D", True)
			except Exception as e:
				self.out.emit("Sorry, there was a network error.")
				log(f"ERROR: {e}", "D", True)
				continue_scrape = False
		else:
			log(f"Cannot Continue for {game_name}, stop requested.", "D", True)

		print(f"URL: \n{url}")

		if continue_scrape and not(self.ss_stopall):

			# Check for errors returned by the response if invalid

			# These first 4 indicate a global issue, so stop all scraping if seen
			if "API totalement fermé" in page.text:
				self.out.emit("The ScreenScraper API is down right now. Exiting...")
				log(f"ScreenScraper Request Error: API Down", "I")
				self.ss_stopall = True
				self.complete.emit()
			if "Le logiciel de scrape utilisé a été blacklisté" in page.text:
				self.out.emit("Bigscraper-qt has been blacklisted. Exiting...")
				log(f"ScreenScraper Request Error: App Blacklisted", "I")
				self.ss_stopall = True
				self.complete.emit()
			if "Votre quota de scrape est" in page.text:
				self.out.emit("Your daily ScreenScraper scraping limit has been reached, try again tomorrow.")
				log(f"ScreenScraper Request Error: Daily Quota Reached", "I")
				self.ss_stopall = True
				self.complete.emit()
			if ("API fermé pour les non membres" in page.text) or ("API closed for non-registered members" in page.text):
				self.out.emit("ScreenScraper is down for unregistered users, Exiting...")
				log(f"ScreenScraper Request Error: Server Down for Unregistered users.", "I")
				self.ss_stopall = True
				self.complete.emit()

			# This one is just a local problem, so other games can continue even if this one is bad
			if "Champ crc, md5 ou sha1 erroné" in page.text:
				self.out.emit("Your Game file's hashes are incorrect. Exiting...")
				log(f"ScreenScraper Request Error: Incorrect File Hashes (check the hashes of your files)", "I")
				continue_scrape = False


			if continue_scrape and not(self.ss_stopall):
				# Scan for content (if request is successful)
				page_content = page.json()

				# Check if file returned is empty
				if not(page_content):
					self.out.emit("ScreenScraper Returned Nothing. Exiting...")
					log(f"The JSON File ScreenScraper Returned is empty. ScreenScraper is probably down.", "I")
					continue_scrape = False

				# Check if any errors were returned by ScreenScraper
				if continue_scrape and not(self.ss_stopall):
					if not(page_content["header"]["success"] == "true"):
						self.out.emit(f"ScreenScraper Error: {page_content['header']['error']}. Exiting...")
						log(f"ScreenScraper Returned An Error: {page_content['header']['error']}", "I")
						continue_scrape = False

					# Check if you've exceeded the daily request limit
					reqs_today = int(page_content["response"]["ssuser"]["requeststoday"])
					reqs_max = int(page_content["response"]["ssuser"]["maxrequestsperday"])
					if (reqs_today >= reqs_max):
						self.out.emit("You've Exceeded the Max Number of Requests. Exiting...")
						log("You've exceeded the Max Daily Requests.", "I")
						self.ss_stopall = True

					self.ss_maxthreads = int(page_content["response"]["ssuser"]["maxthreads"])

					# Last check before metadata is actually scraped
					if continue_scrape and not(self.ss_stopall):
						self.out.emit(f"Collecting Metadata for {game_name}")
						log("Collecting Game Metadata", "I")

						game_raw = page_content["response"]["jeu"]
						meta = {}

						# File for the game
						meta["File"] = game_path

						# Scan each regional code for data relevant to it
						for reg in regions_ss[self.options_loc["region"]]:

							# Name: Check if names of games match the regional name
							if not("Name" in meta):
								log("Checking for Game Name", "D", True)
								for uncat_name in game_raw["noms"]:
									if uncat_name["region"] == reg:
										meta["Name"] = [uncat_name["text"]]
										log("Adding Game Name", "D", True)
										break

							# Release Date: Check if regional release dates match
							if not("Release Date" in meta):
								log("Checking for Game Release", "D", True)
								for uncat_release in game_raw["dates"]:
									if uncat_release["region"] == reg:
										rd_raw = uncat_release["text"].split("-")
										meta["Release Date"] = [calendar_month_rev[rd_raw[1]] + " " + rd_raw[2] + ", " + rd_raw[0]]
										log("Adding Game Release", "D", True)
										break

						# Also scan each language for data relevant to it
						langlist = langs_ss[self.options_loc["region"]]
						if self.options_loc["languageOverride"] != "None":
							langlist = [langs_universal[self.options_loc["languageOverride"]]]

						genrelist = []
						genre_indexes_namefound = []
						for lang in langlist:

							# Overview: Check if regional overview matches region
							if not("Overview" in meta):
								log("Checking for Game Overview", "D", True)
								for uncat_ov in game_raw["synopsis"]:
									if uncat_ov["langue"] == lang:
										meta["Overview"] = [uncat_ov["text"]]
										log("Adding Game Overview", "D", True)
										break

							# Genre: Scan through each genre and check if the language matches
							idx = 0
							for genre in game_raw["genres"]:
								log("Checking for Game Genre", "D", True)
								# Check if this genre already has found a name
								if not(idx in genre_indexes_namefound):
									log("This Genre name not found yet", "D", True)
									for genre_name in genre["noms"]:
										if (genre_name["langue"] == lang):
											genrelist.append(genre_name["text"])
											genre_indexes_namefound.append(idx)
											log(f"Adding this genre ({idx})", "D", True)
											break
								idx += 1
						meta["Genres"] = genrelist



						# Platform
						log("Getting Platform", "D", True)
						meta["Platform"] = [system_info[2]]

						# Developers, Publishers
						log("Getting Developers", "D", True)
						meta["Developers"] = [game_raw["developpeur"]["text"]]
						log("Getting Publishers", "D", True)
						meta["Publishers"] = [game_raw["editeur"]["text"]]

						# Max Players: Get the last number of the range
						log("Getting Max Players", "D", True)
						meta["Max Players"] = [game_raw["joueurs"]["text"].split("-")[-1]]

						# Rating
						# ScreenScraper simply has the rating out of 20, do a little math and it is just dividing the rating by 4 to get a rating out of 5
						log("Getting Rating", "D", True)
						meta["Rating"] = [str((int(game_raw["note"]["text"])) / 4)]



						# Media Scraping
						log("Starting to Get Media", "I", True)
						self.out.emit(f"Downloading Images for {meta['Name'][0]}")
						self.bar.emit(1, 1, 0)

						iidx = 0
						images = []

						for media in game_raw["medias"]:

							# Get Type, URL and Region of Image
							mtype = media["type"]
							murl = media["url"].replace("neoclone", "www")
							mreg = media["region"] if ("region" in media) else "none"

							image_id = ""

							# Convert ScreenScraper region to Formatted Name
							translated_mreg = ""
							if (mreg != "ss") and (mreg != "none") and (mreg in region_translate):
								translated_mreg = " " + region_translate[mreg]

							# Set the Formalized Image ID (title)
							if mtype in ss_arts:
								image_id = meta["Name"][0] + " - " + ss_arts[mtype] + translated_mreg

							if mtype == "video-normalized":
								meta["Video Link"] = [murl]


							# If the image is unique, download it.
							if not(image_id in images) and (image_id != ""):
								# Actually Download the Image
								log(f"Downloading Media ({idx + 1} / {len(game_raw['medias'])}) (for {meta['Name'][0]})", "I")

								if (not(os.path.isfile(os.path.join(paths["MEDIA"], system_info[1], game_name) + "/" + image_id + "." + media["format"]))) and (not(self.ss_stopall)):
									try:
										image_data = requests.get(murl, timeout=15)
										# Write it to a file
										log("Download Successful, Writing to file", "D", True)
										open(os.path.join(paths["MEDIA"], system_info[1], game_name) + "/" + image_id + ".png", "wb").write(image_data.content)
									except Exception as e:
										log(f"Download Error: {e}", "D", True)
										iidx += 1
										self.bar.emit(3, iidx, len(game_raw["medias"]))
										continue

								images.append(image_id)

							else:
								log("This image is not unique or is already downloaded.", "D", True)

							iidx += 1
							self.bar.emit(3, iidx, len(game_raw["medias"]))

						meta["Images"] = images
						self.bar.emit(1, 0, 0)

						# Get Video
						log(f"Checking if Video Download is Needed for {meta['Name'][0]}", "D", True)
						log(str(self.options_loc["video"]), "D", True)
						log(str("Video Link" in meta), "D", True)
						log(str(self.ss_stopall), "D", True)

						if ("Video Link" in meta):
							log(meta["Video Link"][0], "D", True)

						if (self.options_loc["video"]) and ("Video Link" in meta) and not(os.path.isfile(os.path.join(paths["MEDIA"], system_info[1], game_name) + "/" + meta["Name"][0] + " - Video" + ".mp4")) and (not(self.ss_stopall)):

							self.out.emit(f"Downloading Video for {meta['Name'][0]}")
							log(f"Downloading Video for {meta['Name'][0]}", "D", True)
							try:
								video_data = requests.get(meta["Video Link"][0], timeout=15)
								meta["Video Link"] = [meta["Video Link"][0].replace("Fr75s", "[DEVID]").replace(unstuff("169;216;221;197;183;184;141;180;163;214;234"), "[DEVPASS]")]

								log("Download Successful, Writing to file", "D", True)
								open(os.path.join(paths["MEDIA"], system_info[1], game_name) + "/" + meta["Name"][0] + " - Video" + ".mp4", "wb").write(video_data.content)

							except Exception as e:
								log(f"Download Error: {e}", "D", True)
								video_data = requests.get(meta["Video Link"][0], timeout=15)
								meta["Video Link"] = [meta["Video Link"][0].replace("Fr75s", "[DEVID]").replace(unstuff("169;216;221;197;183;184;141;180;163;214;234"), "[DEVPASS]")]

						if (self.ss_stopall):
							self.out.emit("Global API Error Detected. Wrapping Up...")

						# Write Metadata to [game_name].json
						meta_json = json.dumps(meta, indent = 4)
						log("Writing Metadata to File", "D", True)
						open(os.path.join(paths["METADATA"], system_info[1]) + "/" + game_name + ".json", "w").write(meta_json)



