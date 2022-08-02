# scrape1

## Scrapes any one game based on the chosen file and system.

import os, sys, json, shutil, requests
from lxml import html

from .const import *

from PyQt5.QtCore import *

class ScrOneTask(QObject):
	complete = pyqtSignal()
	out = pyqtSignal(str)

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
				page = requests.get("https://gamesdb.launchbox-app.com/platforms/games/" + lb_sysid[system] + "|" + str(current_page))
				log("Page Request Successful", "D", True)
				pagetree = html.fromstring(page.content)
				page_games = pagetree.xpath('//a[@class="list-item"]')

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
							page = requests.get("https://gamesdb.launchbox-app.com/platforms/games/" + lb_sysid[system] + "|" + str(current_page), timeout=15)
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
							"outtmpl": os.path.join(paths["MEDIA"], system, game_match) + "/" + meta["Name"][0] + " - Video.%(ext)s",
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
							image_title = meta["Name"][0] + " - " + out_art
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





		self.complete.emit()
