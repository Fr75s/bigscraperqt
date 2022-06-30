#!/usr/bin/python3

import os, sys, json, shutil, requests
from lxml import html

from .const import *

from PyQt5.QtCore import *

class ScrapeTask(QObject):
	complete = pyqtSignal()
	out = pyqtSignal(str)

	data = []

	def __init__(self, data_i):
		super().__init__()
		self.data = data_i

	def run(self):

		self.out.emit("Starting...")

		print("[I]: Data is " + str(self.data))
		print("[I]: Will write to " + paths["APP_DATA"])

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
			game_names.append(form(trimext(os.path.basename(f))))

		# Get system
		system_name = self.data[1]
		system = convert[self.data[1]]

		print("[I]: Data formatted to " + str([game_names, game_files, system]))



		# Create Folders if necessary
		if not(os.path.isdir(os.path.join(paths["METADATA"], system))):
			os.makedirs(os.path.join(paths["METADATA"], system), exist_ok=True)

		for g in game_names:
			# Iterate through each game's name for file creation to make it *organized*
			if not(os.path.isdir(os.path.join(paths["MEDIA"], system, g))):
				os.makedirs(os.path.join(paths["MEDIA"], system, g), exist_ok=True)



		# BEGIN
		# Prepare for page downloading
		current_page = 1
		games_found = 0

		# Download 1st Page
		self.out.emit("Getting Page " + str(current_page))
		page = requests.get("https://gamesdb.launchbox-app.com/platforms/games/" + cv_id[system] + "|" + str(current_page))
		pagetree = html.fromstring(page.content)
		page_games = pagetree.xpath('//a[@class="list-item"]')

		while (len(page_games) > 0):

			# Scan through each text item
			game_titles = pagetree.xpath("//div[@class='col-sm-10']/h3[1]/text()")
			game_titles_format = []

			# Format game titles
			for t in game_titles:
				game_titles_format.append(form(t))

			# Check for games that match any in the games list
			for g in game_names:
				if (g in game_titles_format):
					games_found += 1
					self.out.emit("Getting metadata for " + g + " (" + str(games_found) + " of " + str(len(game_names)) + ")")

					game_index = game_titles_format.index(g)
					details_link = "https://gamesdb.launchbox-app.com" + pagetree.xpath('//a[@class="list-item"]/@href')[game_index]
					database_id = details_link.rsplit('/', 1)[-1]
					images_link = "https://gamesdb.launchbox-app.com/games/images/" + database_id

					# Get details page
					details_page = requests.get(details_link)
					details = html.fromstring(details_page.content)

					# Initialize metadata object
					meta = {}
					meta["File"] = game_files[game_names.index(g)]

					# Get details from page
					info = details.xpath('//td[@class="row-header"]/text()')
					for i in info:
						# Standard
						if i in ("Name", "Platform", "Release Date", "Game Type", "ESRB", "Max Players", "Cooperative"):
							meta[i] = details.xpath('//td[@class="row-header" and text()="' + i + '"]/../td[2]/span[1]/text()')
						# Links
						if i in ("Developers", "Publishers", "Genres", "Wikipedia", "Video Link"):
							meta[i] = details.xpath('//td[@class="row-header" and text()="' + i + '"]/../td[2]/span[1]/a/text()')
						# Overview Text Block
						if i in ("Overview"):
							meta[i] = details.xpath('//div[@class="view"]/text()')
						# Rating
						if i in ("Rating"):
							meta[i] = details.xpath('//span[@id="communityRating"]/text()')

					## Image Downloads
					# Get Images page
					self.out.emit("Getting Images Page for " + g)
					images_page = requests.get(images_link)
					images = html.fromstring(images_page.content)

					# Get links and corresponding titles
					image_links = images.xpath('//a[contains(@href, "https://images.launchbox-app.com")]/@href')
					image_titles = images.xpath('//a[contains(@href, "https://images.launchbox-app.com")]/@data-title')

					# Download each image
					index = 0
					for link in image_links:
						# Get link
						image_title = image_titles[index]

						# Download the image
						self.out.emit("Downloading Image " + str(index + 1) + " of " + str(len(image_links)) + " for " + g)
						image = requests.get(link)

						# Write to file
						open(os.path.join(paths["MEDIA"], system, g) + "/" + image_title + ".png", "wb").write(image.content)

						index += 1

					# List image titles in metadata
					meta["Images"] = (image_titles if len(image_titles) > 0 else ["NULL"])



					## Video Downloads
					if options["video"]:
						# Option is set: Download video

						# Get video info
						info = ydl.sanitize_info(ydl.extract_info(meta["Video Link"][0], download=False))

						# Only download video if less than 5 minutes or option is set
						if (info["duration"] < VIDEO_LEN_LIMIT or options["videoOverLimit"]):
							self.out.emit("Downloading Video for " + g)
							download_video(meta["Video Link"][0], {"outtmpl": os.path.join(paths["MEDIA"], system, g) + "/" + meta["Name"][0] + " - Video.%(ext)s"})

					# Write Metadata
					meta_json = json.dumps(meta, indent = 4)
					open(os.path.join(paths["METADATA"], system) + "/" + g + ".json", "w").write(meta_json)
					self.out.emit("Collection Complete for " + g + " (" + str(games_found) + " of " + str(len(game_names)) + ")")

			current_page += 1
			self.out.emit("Getting Page " + str(current_page))

			page = requests.get("https://gamesdb.launchbox-app.com/platforms/games/" + cv_id[system] + "|" + str(current_page))
			pagetree = html.fromstring(page.content)
			page_games = pagetree.xpath('//a[@class="list-item"]')


		self.out.emit("Process Complete: Found " + str(games_found) + " of " + str(len(game_names)) + " Games. Exiting...")

		self.complete.emit()

