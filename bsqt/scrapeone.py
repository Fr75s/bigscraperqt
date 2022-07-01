# scrape1

## Scrapes any one game based on the chosen file and system.

import os, sys, json, shutil, requests
from lxml import html

from .const import *

from PyQt5.QtCore import *

class ScrOneTask(QObject):
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

		in_file = self.data[0].replace("file://", "")
		game_match = form(trimext(os.path.basename(in_file)))

		system_name = self.data[1]
		system = convert[self.data[1]]

		print("[I]: Data formatted to " + str([game_match, system]))

		# Create Folders if necessary
		if not(os.path.isdir(os.path.join(paths["METADATA"], system))):
			os.makedirs(os.path.join(paths["METADATA"], system), exist_ok=True)
		if not(os.path.isdir(os.path.join(paths["MEDIA"], system, game_match))):
			os.makedirs(os.path.join(paths["MEDIA"], system, game_match), exist_ok=True)


		# Prepare for page downloading
		current_page = 1
		game_found = False


		# Start Downloading Pages
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

			# Check if game is in list
			if (game_match in game_titles_format):
				# Game is in list: Stop scraping pages
				self.out.emit("Game Found, Getting Metadata")
				game_found = True
				break
			else:
				current_page += 1

				# Get next page
				self.out.emit("Getting Page " + str(current_page))
				page = requests.get("https://gamesdb.launchbox-app.com/platforms/games/" + cv_id[system] + "|" + str(current_page))
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
			details_page = requests.get(details_link)
			details = html.fromstring(details_page.content)

			# Initialize metadata object
			meta = {}
			meta["File"] = in_file

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
			self.out.emit("Getting Images Page")
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
				self.out.emit("Downloading Image " + str(index + 1) + " of " + str(len(image_links)))

				# Don't crash if the image can't download
				try:
					image = requests.get(link)
					# Write to file
					open(os.path.join(paths["MEDIA"], system, game_match) + "/" + image_title + ".png", "wb").write(image.content)
				except:
					self.out.emit("Image " + str(index + 1) + " couldn't Download.")

				index += 1

			# List image titles in metadata
			meta["Images"] = (image_titles if len(image_titles) > 0 else ["NULL"])



			## Video Downloads
			if options["video"] and meta["Video Link"]:
				# Option is set: Download video

				# Get video info
				# info = ydl.sanitize_info(ydl.extract_info(meta["Video Link"][0], download=False))

				dl_options = {
					"match_filter": video_len_test,
					"outtmpl": os.path.join(paths["MEDIA"], system, game_match) + "/" + meta["Name"][0] + " - Video.%(ext)s"
				}

				self.out.emit("Attempting Video Download")
				try:
					download_video(meta["Video Link"][0], dl_options)
				except:
					self.out.emit("Couldn't Download Video")



			# Write Metadata
			meta_json = json.dumps(meta, indent = 4)
			open(os.path.join(paths["METADATA"], system) + "/" + game_match + ".json", "w").write(meta_json)

			# Complete.
			self.out.emit("Scraping Complete. Exiting...")

		else:
			self.out.emit("Game Not Found, Exiting...")

		self.complete.emit()
