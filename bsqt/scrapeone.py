# scrape1

## Scrapes any one game based on the chosen file and system.

import os, sys, json, zlib, shutil, hashlib, requests
from lxml import html

from .const import *

from PyQt5.QtCore import *

class ScrOneTask(QObject):
	complete = pyqtSignal()
	out = pyqtSignal(str)
	stat = pyqtSignal(str)

	bar = pyqtSignal(int, int, int)

	data = []
	options_loc = {}

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

			in_file = self.data[0].replace("file://", "")
			game_match = form(trimext(os.path.basename(in_file)))

			system_name = self.data[1]
			system = systems["LaunchBox"][self.data[1]]

			log("Data formatted to " + str([game_match, system]), "I")

			# Create Folders if necessary
			if not(os.path.isdir(os.path.join(paths["METADATA"], system))):
				log("Creating metadata path for " + system, "D", True)
				os.makedirs(os.path.join(paths["METADATA"], system), exist_ok=True)
			if not(os.path.isdir(os.path.join(paths["MEDIA"], system, game_match))):
				log("Creating media path for " + game_match, "D", True)
				os.makedirs(os.path.join(paths["MEDIA"], system, game_match), exist_ok=True)



			# Prepare for page downloading
			current_page = 1
			game_found = False

			# Check if game is already downloaded
			if (not(os.path.isfile(os.path.join(paths["METADATA"], system) + "/" + game_match + ".json")) or self.options_loc["recache"]):
				# Clear image folder if recache is on
				if (os.path.isdir(os.path.join(paths["MEDIA"], system, game_match)) and self.options_loc["recache"]):
					log("Resetting media directory for " + game_match + " (recache mode on)", "I")
					shutil.rmtree(os.path.join(paths["MEDIA"], system, game_match))
					os.makedirs(os.path.join(paths["MEDIA"], system, game_match), exist_ok=True)

				# Start Downloading Pages
				self.out.emit("Getting Page " + str(current_page))
				page = requests.get(lb_page(system, current_page), timeout=15)
				log("Page Request Successful", "D", True)
				
				pagetree = html.fromstring(page.content)
				page_games = pagetree.xpath('//a[@class="list-item"]')

				log(str(page_games), "D", True)

				while (len(page_games) > 0):
					# Scan through each text item
					log("Parsing Website Data", "I")
					game_titles = pagetree.xpath("//div[@class='col-sm-10']/h3[1]/text()")
					game_titles_format = []

					# Format game titles
					for t in game_titles:
						game_titles_format.append(form(t))

					# Check if game is in list
					if (game_match in game_titles_format):
						# Game is in list: Stop scraping pages
						game_found = True
						break
					else:
						log("Game Not Found", "I")
						current_page += 1

						# Get next page
						self.out.emit("Getting Page " + str(current_page))
						try:
							page = requests.get(lb_page(system, current_page), timeout=15)
							log("Page Request Successful", "D", True)
						except Exception as e:
							current_page -= 1
							log("Couldn't Fetch Page: " + str(e), "E")
						pagetree = html.fromstring(page.content)
						page_games = pagetree.xpath('//a[@class="list-item"]')


				# Check if game has been found in collection
				if (game_found):
					# Get game index, using it to get details page link
					game_index = game_titles_format.index(game_match)
					details_link = "https://gamesdb.launchbox-app.com" + pagetree.xpath('//a[@class="list-item"]/@href')[game_index]
					database_id = details_link.rsplit('/', 1)[-1]
					images_link = "https://gamesdb.launchbox-app.com/games/images/" + database_id

					# Get details page
					log("Attempting to get Details Page", "I")
					try:
						self.out.emit("Game Found, Getting Details Page")
						details_page = requests.get(details_link, timeout=15)
						log("Page Request Successful", "D", True)
					except Exception as e:
						self.out.emit("Couldn't get details, terminating app...")
						raise e
					details = html.fromstring(details_page.content)

					# Get Images page
					log("Attempting to get Images Page", "I")
					try:
						self.out.emit("Getting Images Page")
						images_page = requests.get(images_link, timeout=15)
						log("Page Request Successful", "D", True)
					except Exception as e:
						self.out.emit("Couldn't get details, terminating app...")
						raise e
					images = html.fromstring(images_page.content)

					# Get links and corresponding titles
					log("Parsing Page for Images", "D", True)
					image_links = images.xpath('//a[contains(@href, "https://images.launchbox-app.com")]/@href')
					image_titles = images.xpath('//a[contains(@href, "https://images.launchbox-app.com")]/@data-title')

					self.bar.emit(0, 1, 0)
					TASKS_COMPLETE = 0
					TOTAL_TASKS = 1
					TOTAL_TASKS += len(image_links)

					# Initialize metadata object
					meta = {}
					meta["File"] = in_file

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

					if (self.options_loc["video"] and meta["Video Link"]):
						TOTAL_TASKS += 1


					TASKS_COMPLETE += 1
					self.bar.emit(2, TASKS_COMPLETE, TOTAL_TASKS)


					## Image Downloads

					# Download each image
					index = 0
					self.out.emit("Downloading Images")

					# Replace accents in image titles (mismatches may occur otherwise)
					image_title_idx = 0
					for image_title in image_titles:
						image_titles[image_title_idx] = noaccent(image_title)
						image_title_idx += 1

					for link in image_links:
						# Get link
						image_title = image_titles[index]

						# Download the image
						#self.out.emit("Downloading Image " + str(index + 1) + " of " + str(len(image_links)))
						#self.bar.emit(2, index + 1, len(image_links))

						# Don't crash if the image can't download
						try:
							log("Attempting Image Download", "D", True)
							image = requests.get(link, timeout=15)
							log("Request Successful, Writing to file", "D", True)
							# Write to file
							open(os.path.join(paths["MEDIA"], system, game_match) + "/" + image_title + ".png", "wb").write(image.content)
						except Exception as e:
							log("Image Download Failed: " + str(e), "E")
							self.out.emit("Image " + str(index + 1) + " couldn't Download.")

						index += 1
						TASKS_COMPLETE += 1
						self.bar.emit(2, TASKS_COMPLETE, TOTAL_TASKS)

					# List image titles in metadata
					meta["Images"] = (image_titles if len(image_titles) > 0 else ["NULL"])



					## Video Downloads
					if self.options_loc["video"] and meta["Video Link"]:
						# Option is set: Download video

						# Get video info
						# info = ydl.sanitize_info(ydl.extract_info(meta["Video Link"][0], download=False))

						dl_options = {
							"match_filter": video_len_test,
							"outtmpl": os.path.join(paths["MEDIA"], system, game_match) + "/" + noaccent(meta["Name"][0]) + " - Video.%(ext)s",
							"progress_hooks": [self.video_progress_hook]
						}

						self.out.emit("Attempting Video Download")
						try:
							download_video(meta["Video Link"][0], dl_options)
							TASKS_COMPLETE += 1
							self.bar.emit(2, TASKS_COMPLETE, TOTAL_TASKS)
						except Exception as e:
							log("Video Download Failed: " + str(e), "E")
							self.out.emit("Couldn't Download Video")



					# Write Metadata
					meta_json = json.dumps(meta, indent = 4)
					log("Writing Metadata to File", "D", True)
					open(os.path.join(paths["METADATA"], system) + "/" + game_match + ".json", "w").write(meta_json)

					# Complete.
					self.bar.emit(0, 0, 0)
					self.out.emit("Scraping Complete. Exiting...")

				else:
					self.out.emit("Game Not Found, Exiting...")

			else:
				log("Game Already Scraped", "I")
				self.out.emit("Game Already Scraped. Exiting...")

			self.bar.emit(0, 0, 0)
			self.bar.emit(1, 0, 0)

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

			log("Data formatted to " + str([mame_id, system]), "I")



			# Check if game is already scraped with adb.json
			do_scrape_game = True
			if (os.path.isfile(os.path.join(paths["EXTRA"], "adb.json")) and not self.options_loc["recache"]):
				log("Checking adb.json", "D", True)
				adb = json.load(open(os.path.join(paths["EXTRA"], "adb.json")))

				if mame_id in adb:
					do_scrape_game = False


			# Only Scrape if permitted
			if (do_scrape_game):
				# Get the page for the game
				log("Attempting to get page", "I")
				try:
					self.out.emit("Getting Metadata Page")
					page = requests.get(f"http://adb.arcadeitalia.net/service_scraper.php?ajax=query_mame&game_name={mame_id}", timeout=15)
					log("Page Request Successful", "D", True)
				except Exception as e:
					self.out.emit("Couldn't Get the game page")
					log(f"ERROR: {e}", "D", True)
					self.complete.emit()

				# Get the metadata object from the result
				page_content = page.json()
				raw_meta = page_content["result"][0]



				# Start Filtering metadata into format
				meta = {}
				meta["File"] = in_file

				# Basic Information
				meta["Name"] = [raw_meta["short_title"]]
				meta["Platform"] = ["Arcade"]
				meta["Release Date"] = [raw_meta["year"]] # There's already support for year-only release dates, no concern there

				# Developers, Publishers, Genres
				meta["Developers"] = [raw_meta["manufacturer"]]
				meta["Publishers"] = [raw_meta["manufacturer"]]
				meta["Genres"] = raw_meta["genre"].split(" / ")

				# More Basic Info
				meta["Max Players"] = [str(raw_meta["players"])]

				real_rating = raw_meta["rate"] / 20
				if (real_rating > 0):
					meta["Rating"] = [float(real_rating)]

				meta["Video Link"] = ["https://youtu.be/" + raw_meta["youtube_video_id"]]
				meta["Overview"] = [raw_meta["history"]]

				game_name = form(meta["Name"][0])



				# Create Folders if necessary
				if not(os.path.isdir(os.path.join(paths["METADATA"], system))):
					log("Creating metadata path for " + system, "D", True)
					os.makedirs(os.path.join(paths["METADATA"], system), exist_ok=True)
				if not(os.path.isdir(os.path.join(paths["MEDIA"], system, game_name))):
					log("Creating media path for " + game_name, "D", True)
					os.makedirs(os.path.join(paths["MEDIA"], system, game_name), exist_ok=True)

				# Clear everything if recache on
				if (self.options_loc["recache"]):
					log("Resetting media directory for " + game_name + " (recache mode on)", "I")
					shutil.rmtree(os.path.join(paths["MEDIA"], system, game_name))
					os.makedirs(os.path.join(paths["MEDIA"], system, game_name), exist_ok=True)



				# Get Images
				self.out.emit("Getting Images")
				self.bar.emit(0, 1, 0)

				images_completed = 0
				current_image = 1
				total_images = len(list(ad_arts.keys()))

				images = []

				# Uses ad_arts to simplify the process, viewable in const.py
				for art in ad_arts:
					try:
						image = requests.get(raw_meta["url_" + art], timeout=15)
						log("Request Successful, Writing to file", "D", True)
						# Write to file
						for out_art in ad_arts[art]:
							image_title = noaccent(meta["Name"][0]) + " - " + out_art
							open(os.path.join(paths["MEDIA"], system, game_name) + "/" + image_title + ".png", "wb").write(image.content)

							images.append(image_title)

							log(f"Write Successful for {out_art}", "D", True)

						images_completed += 1
						self.bar.emit(2, images_completed, total_images)
					except Exception as e:
						self.out.emit(f"Error Ocurred while Downloading Image {current_image}")
						total_images -= 1
						log(f"ERROR: {e}", "D", True)

					current_image += 1

				meta["Images"] = images



				# Get Video
				if self.options_loc["video"] and "Video Link" in meta:
					dl_options = {
						"match_filter": video_len_test,
						"outtmpl": os.path.join(paths["MEDIA"], system, game_name) + "/" + noaccent(meta["Name"][0]) + " - Video.%(ext)s",
						"progress_hooks": [self.video_progress_hook]
					}

					self.out.emit("Attempting Video Download")
					try:
						download_video(meta["Video Link"][0], dl_options)
					except Exception as e:
						log("Video Download Failed: " + str(e), "E")
						self.out.emit("Couldn't Download Video")

				self.bar.emit(1, 0, 0)



				# Begin Output

				# Write game name to adb.json
				if (os.path.isfile(os.path.join(paths["EXTRA"], "adb.json"))):
					log("Adding to ADB Scraped Games list", "D", True)
					adb = json.load(open(os.path.join(paths["EXTRA"], "adb.json")))

					if not(mame_id in adb):
						adb.append(mame_id)

						adb_json = json.dumps(adb, indent = 4)
						open(os.path.join(paths["EXTRA"], "adb.json"), "w").write(adb_json)
						log("Saved ADB Scraped Games list to file", "D", True)
				else:
					log("Creating ADB Scraped Games list", "D", True)
					adb = [mame_id]
					adb_json = json.dumps(adb, indent = 4)

					open(os.path.join(paths["EXTRA"], "adb.json"), "w").write(adb_json)
					log("Saved ADB Scraped Games list to file", "D", True)


				# Write Metadata to [game].json
				meta_json = json.dumps(meta, indent = 4)
				log("Writing Metadata to File", "D", True)
				open(os.path.join(paths["METADATA"], system) + "/" + game_name + ".json", "w").write(meta_json)

				# Wrap Up
				self.out.emit("Scraping Complete. Exiting...")

			else:
				log("Game Already Scraped", "I")
				self.out.emit("Game Already Scraped. Exiting...")

			self.bar.emit(0, 0, 0)

		#
		#  ## ###  ##
		#  #  #    #
		# ##  ### ##
		#
		elif (self.options_loc["module"] == "ScreenScraper"):
			log("Scraping from ScreenScraper", "I")

			in_file = self.data[0].replace("file://", "")
			game = form(trimext(os.path.basename(in_file)))

			system_full = self.data[1]
			system = systems["ScreenScraper"][self.data[1]]
			system_id = sc_sysid[system]

			log("Data formatted to " + str([game, system, system_id]), "I")

			# Create Folders if necessary
			if not(os.path.isdir(os.path.join(paths["METADATA"], system))):
				log("Creating metadata path for " + system, "D", True)
				os.makedirs(os.path.join(paths["METADATA"], system), exist_ok=True)
			if not(os.path.isdir(os.path.join(paths["MEDIA"], system, game))):
				log("Creating media path for " + game, "D", True)
				os.makedirs(os.path.join(paths["MEDIA"], system, game), exist_ok=True)

			# Check if game is already downloaded
			if (not(os.path.isfile(os.path.join(paths["METADATA"], system) + "/" + game + ".json")) or self.options_loc["recache"]):

				game_size = os.path.getsize(in_file)
				infoappend = ""
				if (game_size > 128000000):
					infoappend = "(This may take a while)"

				#
				# Screenscraper has a policy of requiring hashes for game scrapes.
				# As a result, I need to get 3 hashes for every scraped game.
				# For large games, reading the whole file takes a while, causing slowdown.
				#

				# MD5
				self.out.emit(f"Processing MD5 Hash (1/3) {infoappend}...")
				hash_md5 = hashlib.md5(open(in_file, 'rb').read()).hexdigest()
				log(f"MD5 Hash: {hash_md5}", "D", True)

				# SHA1
				self.out.emit(f"Processing SHA1 Hash (2/3) {infoappend}...")
				hash_sha1 = hashlib.sha1(open(in_file, 'rb').read()).hexdigest()
				log(f"SHA1 Hash: {hash_sha1}", "D", True)

				# CRC32
				self.out.emit(f"Processing CRC32 Hash (3/3) {infoappend}...")
				hash_crc32 = zlib.crc32(open(in_file, 'rb').read())
				log(f"CRC32 Hash: {hash_crc32}, CRC32 Hex-Formatted Hash: {hex(hash_crc32)[2:]}", "D", True)

				# Get the Username and Password of the user, set in the options which is transferred here
				urlUserPass = ""

				if (self.options_loc["screenScraperUser"] != "" and self.options_loc["screenScraperPass"] != ""):
					urlUserPass = "&ssid=" + self.options_loc["screenScraperUser"] + "&sspassword=" + self.options_loc["screenScraperPass"]

				# Generate a url
				url = "https://www.screenscraper.fr/api2/jeuInfos.php?devid=Fr75s&devpassword=" + unstuff("169;216;221;197;183;184;141;180;163;214;234") + "&softname=bigscraperqt&output=json" + urlUserPass + "&crc=" + hex(hash_crc32)[2:] + "&md5=" + hash_md5 + "&sha1=" + hash_sha1 + "&systemeid=" + str(system_id) + "&romtype=rom&romnom=" + os.path.basename(in_file) + "&romtaille=" + str(game_size)

				#
				# Finally, we are ready to scrape.
				#

				if output_links:
					print(f"\033[94m[L] {url}\033[00m")

				# Attempt to get the game page
				log("Attempting to get info", "I")
				try:
					self.out.emit("Getting Metadata Page")
					page = requests.get(url, timeout=15)
					log("Page Request Successful", "D", True)
				except Exception as e:
					self.out.emit("Sorry, there was a network error.")
					log(f"ERROR: {e}", "D", True)
					self.complete.emit()

				# Check for errors returned by the response if invalid
				if "API totalement fermé" in page.text:
					self.out.emit("The ScreenScraper API is down right now. Exiting...")
					log(f"ScreenScraper Request Error: API Down", "I")
					self.complete.emit()

				if "Le logiciel de scrape utilisé a été blacklisté" in page.text:
					self.out.emit("Bigscraper-qt has been blacklisted. Exiting...")
					log(f"ScreenScraper Request Error: App Blacklisted", "I")
					self.complete.emit()

				if "Votre quota de scrape est" in page.text:
					self.out.emit("Your daily ScreenScraper scraping limit has been reached, try again tomorrow.")
					log(f"ScreenScraper Request Error: Daily Quota Reached", "I")
					self.complete.emit()

				if "Champ crc, md5 ou sha1 erroné" in page.text:
					self.out.emit("Your Game file's hashes are incorrect. Exiting...")
					log(f"ScreenScraper Request Error: Incorrect File Hashes (check the hashes of your files)", "I")
					self.complete.emit()

				if ("API fermé pour les non membres" in page.text) or ("API closed for non-registered members" in page.text):
					self.out.emit("ScreenScraper is down for unregistered users, Exiting...")
					log(f"ScreenScraper Request Error: Server Down for Unregistered users.", "I")
					self.complete.emit()

				if "Erreur de login : Vérifier vos identifiants développeur !" in page.text:
					self.out.emit("Please update bigscraper-qt. Exiting...")
					log(f"({game_name}) ScreenScraper Request Error: Wrong Dev Credentials (app probably needs updating)", "I")
					self.complete.emit()

				if ("Erreur : Jeu non trouvée !" in page.text) or ("Erreur : Rom/Iso/Dossier non trouvée !" in page.text):
					self.out.emit(f"No match was found for {game_name}. Skipping...")
					log(f"({game_name}) ScreenScraper Request Error: No Game Match Found (check if {game_name} is similar to the game name on screenscraper)", "I")
					self.complete.emit()

				if "Problème dans le nom du fichier rom" in page.text:
					self.out.emit(f"{game_name} has a bad name format. Skipping...")
					log(f"({game_name}) ScreenScraper Request Error: {game_name}'s file name format doesn't match ScreenScraper's list of names. Typically, the name should be in the form [My Game (REG)].", "I")
					self.complete.emit()

				if "Faite du tri dans vos fichiers roms et repassez demain !" in page.text:
					self.out.emit(f"This game probably doesn't match, and you have scraped too many games that didn't return anything. Skipping...")
					log(f"({game_name}) ScreenScraper Request Error: Too many bad requests. ScreenScraper has a separate limit for requests that don't return anything, and if it's too much an error is returned.", "I")
					self.complete.emit()

				if "Le nombre de threads autorisé pour le membre est atteint" in page.text:
					self.out.emit(f"Stopping thread for {game_name}...")
					log(f"({game_name}) ScreenScraper Request Error: Too many threads. Please take a note of the max number of threads you have.", "W")
					self.complete.emit()


				# Scan for content (if request is successful)
				page_content = page.json()

				# Check if file returned is empty
				if not(page_content):
					self.out.emit("ScreenScraper Returned Nothing. Exiting...")
					log(f"The JSON File ScreenScraper Returned is empty. ScreenScraper is probably down.", "I")
					self.complete.emit()

				# Check if any errors were returned by ScreenScraper
				if not(page_content["header"]["success"] == "true"):
					self.out.emit(f"ScreenScraper Error: {page_content['header']['error']}. Exiting...")
					log(f"ScreenScraper Returned An Error: {page_content['header']['error']}", "I")
					self.complete.emit()

				# Check if you've exceeded the daily request limit

				# If you're wondering why we're checking for ssuser, check the complaint in scrapemany.py.
				if "ssuser" in page_content["response"]:
					reqs_today = int(page_content["response"]["ssuser"]["requeststoday"])
					reqs_max = int(page_content["response"]["ssuser"]["maxrequestsperday"])

					ko_today = int(page_content["response"]["ssuser"]["requestskotoday"])
					ko_max = int(page_content["response"]["ssuser"]["maxrequestskoperday"])

					self.stat.emit(f"REQ: ({reqs_today}/{reqs_max})\nKO: ({ko_today}/{ko_max})")
					if (reqs_today >= reqs_max):
						self.out.emit("You've Exceeded the Max Number of Requests. Exiting...")
						log("You've exceeded the Max Daily Requests.", "I")
						self.complete.emit()


				# And after all that error checking, we can finally start getting the actual data.
				game_raw = page_content["response"]["jeu"]
				meta = {}

				self.out.emit("Collecting Metadata")
				log("Collecting Game Metadata", "I")

				# File for the game
				meta["File"] = in_file

				# Scan each regional code for data relevant to it
				for reg in regions_ss[self.options_loc["region"]]:

					# Name: Check if names of games match the regional name
					if not("Name" in meta) and ("noms" in game_raw):
						log("Checking for Game Name", "D", True)
						for uncat_name in game_raw["noms"]:
							if uncat_name["region"] == reg:
								meta["Name"] = [uncat_name["text"]]
								log("Adding Game Name", "D", True)
								break

					# Release Date: Check if regional release dates match
					if not("Release Date" in meta) and ("dates" in game_raw):
						log("Checking for Game Release", "D", True)
						for uncat_release in game_raw["dates"]:
							if uncat_release["region"] == reg:
								rd_raw = uncat_release["text"].split("-")

								log("Adding Game Release", "D", True)
								if len(rd_raw) == 3:
									log("Full Date Available", "D", True)
									meta["Release Date"] = [calendar_month_rev[rd_raw[1]] + " " + rd_raw[2] + ", " + rd_raw[0]]
								elif len(rd_raw) == 1:
									log("Only Year Available", "D", True)
									meta["Release Date"] = [rd_raw[0]]
								else:
									log(f"Unknown Date Format, Not applying. ({rd_raw})", "D", True)

								break

				# Also scan each language for data relevant to it
				langlist = langs_ss[self.options_loc["region"]]
				if self.options_loc["languageOverride"] != "None":
					langlist = [langs_universal[self.options_loc["languageOverride"]]]

				genrelist = []
				genre_indexes_namefound = []
				for lang in langlist:

					# Overview: Check if regional overview matches region
					if not("Overview" in meta) and ("synopsis" in game_raw):
						log("Checking for Game Overview", "D", True)
						for uncat_ov in game_raw["synopsis"]:
							if uncat_ov["langue"] == lang:
								meta["Overview"] = [uncat_ov["text"]]
								log("Adding Game Overview", "D", True)
								break

					# Genre: Scan through each genre and check if the language matches
					if ("genres" in game_raw):
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
				meta["Platform"] = [system_full]

				# Developers, Publishers
				log("Getting Developers", "D", True)
				if "developpeur" in game_raw:
					meta["Developers"] = [game_raw["developpeur"]["text"]]
				log("Getting Publishers", "D", True)
				if "editeur" in game_raw:
					meta["Publishers"] = [game_raw["editeur"]["text"]]

				# Max Players: Get the last number of the range
				log("Getting Max Players", "D", True)
				if "joueurs" in game_raw:
					meta["Max Players"] = [game_raw["joueurs"]["text"].split("-")[-1]]

				# Rating
				# ScreenScraper simply has the rating out of 20, do a little math and it is just dividing the rating by 4 to get a rating out of 5
				log("Getting Rating", "D", True)
				if "note" in game_raw:
					meta["Rating"] = [str((int(game_raw["note"]["text"])) / 4)]

				# Media Scraping

				# This will be a little different, as ScreenScraper lists all media together, so we must work from there.

				log("Starting to Get Media", "I", True)
				self.out.emit("Downloading Images")
				self.bar.emit(0, 1, 0)

				idx = 0
				images = []

				# Nobody uses the single scrape anyways, so nothing to worry about here. Right?
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
						image_id = noaccent(meta["Name"][0]) + " - " + ss_arts[mtype] + translated_mreg

					if mtype == "video-normalized":
						meta["Video Link"] = [murl]


					# If the image is unique, download it.
					if not(image_id in images) and (image_id != ""):
						# Actually Download the Image
						log(f"Downloading Media ({idx + 1} / {len(game_raw['medias'])})", "I")

						if (not(os.path.isfile(os.path.join(paths["MEDIA"], system, game) + "/" + image_id + "." + media["format"]))):
							try:
								image_data = requests.get(murl, timeout=15)
								# Write it to a file
								log("Download Successful, Writing to file", "D", True)
								open(os.path.join(paths["MEDIA"], system, game) + "/" + image_id + ".png", "wb").write(image_data.content)
							except Exception as e:
								log(f"Download Error: {e}", "D", True)
								idx += 1
								self.bar.emit(2, idx, len(game_raw["medias"]))
								continue

						images.append(image_id)

					else:
						log("This image is not unique or is already downloaded.", "D", True)

					idx += 1
					self.bar.emit(2, idx, len(game_raw["medias"]))

				meta["Images"] = images
				self.bar.emit(1, 0, 0)


				# Get Video
				if (self.options_loc["video"]) and ("Video Link" in meta) and not(os.path.isfile(os.path.join(paths["MEDIA"], system, game) + "/" + meta["Name"][0] + " - Video" + ".mp4")):

					self.out.emit("Downloading Video")
					try:
						video_data = requests.get(meta["Video Link"][0], timeout=15)
						meta["Video Link"] = [meta["Video Link"][0].replace("Fr75s", "[DEVID]").replace(unstuff("169;216;221;197;183;184;141;180;163;214;234"), "[DEVPASS]")]

						log("Download Successful, Writing to file", "D", True)
						open(os.path.join(paths["MEDIA"], system, game) + "/" + noaccent(meta["Name"][0]) + " - Video" + ".mp4", "wb").write(video_data.content)

					except Exception as e:
						log(f"Download Error: {e}", "D", True)
						meta["Video Link"] = [meta["Video Link"][0].replace("Fr75s", "[DEVID]").replace(unstuff("169;216;221;197;183;184;141;180;163;214;234"), "[DEVPASS]")]

				# Write Metadata to [game].json
				meta_json = json.dumps(meta, indent = 4)
				log("Writing Metadata to File", "D", True)
				open(os.path.join(paths["METADATA"], system) + "/" + game + ".json", "w").write(meta_json)

				# Wrap Up
				self.out.emit("Scraping Complete. Exiting...")

			else:
				log("Game Already Scraped", "I")
				self.out.emit("Game Already Scraped. Exiting...")

			self.out.emit("Exiting...")


		self.complete.emit()
