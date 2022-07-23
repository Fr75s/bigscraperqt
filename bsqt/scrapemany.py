#!/usr/bin/python3

import os, sys, json, shutil, requests
from lxml import html

from .const import *

from PyQt5.QtCore import *

class ScrapeTask(QObject):
	complete = pyqtSignal()
	out = pyqtSignal(str)

	bar = pyqtSignal(int, int, int)

	data = []
	options_loc = []

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

		# Get system
		system_name = self.data[1]
		system = convert[self.data[1]]

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

		# Format game files into names of games for finding
		game_names = []
		for f in game_files:
			game_name_format = form(trimext(os.path.basename(f)))

			# Check if games exist
			if (not(os.path.isfile(os.path.join(paths["METADATA"], system) + "/" + game_name_format + ".json")) or self.options_loc["recache"]):
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
			page = requests.get("https://gamesdb.launchbox-app.com/platforms/games/" + cv_id[system] + "|" + str(current_page), timeout=15)
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
						page = requests.get("https://gamesdb.launchbox-app.com/platforms/games/" + cv_id[system] + "|" + str(current_page), timeout=15)
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

		self.complete.emit()

