#!/usr/bin/python3

import os, sys, json, shutil

from .const import *

from PyQt5.QtCore import *

class ExportTask(QObject):
	complete = pyqtSignal()
	out = pyqtSignal(str)

	bar = pyqtSignal(int, int, int)

	data = []
	options_loc = []

	def __init__(self, data_i, opt_main):
		super().__init__()
		self.data = data_i
		self.options_loc = opt_main

	def run(self):

		self.out.emit("Starting...")

		log("Data is " + str(self.data), "I")

		# Initialize Variables from data
		out_folder = self.data[0].replace("file://", "")
		system_name = self.data[1]
		system = systems["LaunchBox"][self.data[1]]
		out_format = self.data[2]

		output = []

		game_meta_files = []
		valid = True

		log("Will write to " + out_folder, "I")

		# Check if metadata folder and images folder for system exists
		if not(os.path.isdir(os.path.join(paths["METADATA"], system))):
			valid = False
		else:
			game_meta_files = os.listdir(os.path.join(paths["METADATA"], system))
		if not(os.path.isdir(os.path.join(paths["MEDIA"], system))):
			valid = False

		# Split Based on Pegasus / EmulationStation Export
		if (out_format == "Pegasus Frontend"):
			# Export For Pegasus
			self.out.emit("Exporting For Pegasus...")
			log("Format: PEGASUS", "I")

			# System Values
			output.append("collection: " + system_name)
			output.append("shortname: " + system)
			output.append("command: [INSERT COMMAND HERE]")

			completed = 0

			# Go through each game's JSON file
			self.bar.emit(0, 1, 0)
			for meta_file_raw in sorted(game_meta_files):
				log("Reading Metadata File", "D", True)
				meta_file = os.path.join(paths["METADATA"], system) + "/" + meta_file_raw
				meta = json.load(open(meta_file))

				output.append("")
				output.append("")

				# Get File and Name. These Must exist, as they are required if the game was found while scraping.
				game_form = form(meta["Name"][0])
				output.append("game: " + meta["Name"][0])
				output.append("file: " + meta["File"])

				# Get the rest of the text metadata, which may or may not exist.
				if "Rating" in meta:
					if len(meta["Rating"]) > 0:
						output.append("rating: " + meta["Rating"][0])

				if "Overview" in meta:
					if len(meta["Overview"]) > 0:
						output.append("description: " + meta["Overview"][0])
						output.append("summary: " + meta["Overview"][0])

				# There may be multiple of the following, so iterate through each
				if "Developers" in meta:
					for m in meta["Developers"]:
						output.append("developers: " + m)

				if "Publishers" in meta:
					for m in meta["Publishers"]:
						output.append("publishers: " + m)

				if "Genres" in meta:
					for m in meta["Genres"]:
						output.append("genres: " + m)

				# One more normal metadatum
				if "Max Players" in meta:
					if len(meta["Max Players"]) > 0:
						output.append("players: " + meta["Max Players"][0])

				# Release Date Special Case
				if "Release Date" in meta:
					if len(meta["Release Date"]) > 0:
						# Check if full release date or only year
						if (len(meta["Release Date"][0]) > 4):
							# Full Release Date
							release_date_parts = meta["Release Date"][0].split()

							# Requires some formatting from MMMM DD, YYYY to [MM, DD, YYYY]
							release_date_parts[0] = calendar_month[release_date_parts[0]]
							release_date_parts[1] = release_date_parts[1].replace(",","")
							if int(release_date_parts[1]) < 10 and not("0" in release_date_parts[1]):
								release_date_parts[1] = "0" + release_date_parts[1]

							output.append("release: " + release_date_parts[2] + "-" + release_date_parts[0] + "-" + release_date_parts[1])
							output.append("releaseYear: " + release_date_parts[2])
							output.append("releaseMonth: " + release_date_parts[0])
							output.append("releaseDay: " + release_date_parts[1])

						else:
							# Year Only
							output.append("releaseYear: " + meta["Release Date"][0])

				#
				# Image Copying
				#

				# Get all images
				self.out.emit("Copying Images for " + meta["Name"][0])
				image_files = os.listdir(os.path.join(paths["MEDIA"], system, game_form))

				image_files_singlestr = ""
				for i in image_files:
					image_files_singlestr += i + ";;"

				output_imgs = {}

				for art in pegasus_artconv:
					for p_art in pegasus_artconv[art]:
						if not(os.path.isdir(os.path.join(out_folder, "media", p_art))):
							os.makedirs(os.path.join(out_folder, "media", p_art), exist_ok=True)

					images_with_art = []
					images_with_art_single = ";;"
					for img in meta["Images"]:
						if art in img:
							images_with_art.append(img)
							images_with_art_single += img + ";;"

					# Check Images By Region
					valid_image_exists = False
					for reg in regions[self.options_loc["region"]]:
						for img in images_with_art:
							if reg in img:
								# Valid
								valid_image_exists = True
								for p_art in pegasus_artconv[art]:
									# Check for file
									if (os.path.isfile(os.path.join(paths["MEDIA"], system, game_form) + "/" + img + ".png")):
										# Copy File
										log(f"Copying {img}.png to folder", "D", True)
										shutil.copyfile(os.path.join(paths["MEDIA"], system, game_form) + "/" + img + ".png", os.path.join(out_folder, "media", p_art) + "/" + img + ".png")
										# Add to Output
										output_imgs[p_art] = "assets." + p_art + ": " + os.path.join("media", p_art) + "/" + img + ".png"
									else:
										log(f"Couldn't copy {img}, doesn't exist", "I")
								break

						if valid_image_exists:
							break

					# Check Regionless Images
					if not(valid_image_exists):
						for img in images_with_art:
							if not("(" in img):
								# Valid
								valid_image_exists = True
								for p_art in pegasus_artconv[art]:
									# Check for file
									if (os.path.isfile(os.path.join(paths["MEDIA"], system, game_form) + "/" + img + ".png")):
										# Copy File
										log(f"Copying {img}.png to folder", "D", True)
										shutil.copyfile(os.path.join(paths["MEDIA"], system, game_form) + "/" + img + ".png", os.path.join(out_folder, "media", p_art) + "/" + img + ".png")
										# Add to Output
										output_imgs[p_art] = "assets." + p_art + ": " + os.path.join("media", p_art) + "/" + img + ".png"
									else:
										log(f"Couldn't copy {img}, doesn't exist", "I")
								break

				for o in output_imgs:
					output.append(output_imgs[o])

				## Iterate through every art
				#for art in pegasus_artconv:
					#if not(os.path.isdir(os.path.join(out_folder, "media", art))):
						#os.makedirs(os.path.join(out_folder, "media", art), exist_ok=True)

					#for img in meta["Images"]:
						#if art in img:

							#image_exists = False
							#for reg in regions[self.options_loc["region"]]:
								#if reg in img:
									#image_exists = True

									## Copy Image
									#shutil.copyfile(os.path.join(paths["MEDIA"], system, game_form) + "/" + img + ".png", os.path.join(out_folder, "media", art) + "/" + img + ".png")
									## Add to Output
									#output.append("assets." + art + ": " + os.path.join(out_folder, "media", art) + "/" + img + ".png")
							#if not(image_exists) and not("(" in img)

				#for img in meta["Images"]:
					## Get all arts
					#for art in pegasus_artconv:
						## Get all locales

						## Check if image has no locale
						#if not("(" in img):
							## Image has no locale: Copy over
							#if (art in img):
								## Match Found: Copy Over and add it.
								#art_found = True

								## Ensure destination media folder exists
								#if not(os.path.isdir(os.path.join(out_folder, "media", art))):
									#os.makedirs(os.path.join(out_folder, "media", art), exist_ok=True)

								## Get file
								#img_file_raw = os.path.join(paths["MEDIA"], system, game_form) + "/" + img + ".png"
								## Copy File
								#shutil.copyfile(img_file_raw, os.path.join(out_folder, "media", art) + "/" + img + ".png")
								## Add to Output
								#output.append("assets." + art + ": " + os.path.join(out_folder, "media", art) + "/" + img + ".png")
								#break
						#else:
							#art_found = False
							#for reg in regions[self.options_loc["region"]]:
								## Check for 2 things:
								## 1. The corresponding art is in the image title
								## 2. The image matches with any of the chosen locales
								#if (art in img) and (reg in img):
									## Match Found: Copy over and add it.
									#art_found = True

									## Ensure destination media folder exists
									#if not(os.path.isdir(os.path.join(out_folder, "media", art))):
										#os.makedirs(os.path.join(out_folder, "media", art), exist_ok=True)

									## Get file
									#img_file_raw = os.path.join(paths["MEDIA"], system, game_form) + "/" + img + ".png"
									## Copy File
									#shutil.copyfile(img_file_raw, os.path.join(out_folder, "media", art) + "/" + img + ".png")
									## Add to Output
									#output.append("assets." + art + ": " + os.path.join(out_folder, "media", art) + "/" + img + ".png")
									#break
							#if art_found:
								#break

				# Copy Video if it exists
				for f in os.listdir(os.path.join(paths["MEDIA"], system, game_form)):
					if "Video" in f:
						# Ensure destination media folder exists
						if not(os.path.isdir(os.path.join(out_folder, "media", "video"))):
							os.makedirs(os.path.join(out_folder, "media", "video"), exist_ok=True)

						# Copy Video
						shutil.copyfile(os.path.join(paths["MEDIA"], system, game_form, f), os.path.join(out_folder, "media", "video", f))
						output.append("assets.video: " + os.path.join("media", "video", f))
						break

				completed += 1
				self.bar.emit(2, completed, len(game_meta_files))

			# Output to document
			if (os.path.isfile(os.path.join(out_folder, "metadata.pegasus.txt"))):
				os.remove(os.path.join(out_folder, "metadata.pegasus.txt"))

			log("Writing Output", "I")
			output_file = open(os.path.join(out_folder, "metadata.pegasus.txt"), "a")

			for line in output:
				output_file.writelines(line + "\n")

			output_file.close()

			self.bar.emit(0, 0, 0)
			self.out.emit("Finished Output. Exiting...")

		elif (out_format == "EmulationStation"):
			self.out.emit("Exporting For EmulationStation...")
			log("Format: EmulationStation", "I")

			output = []
			output.append("<gameList>")

			# Get Games
			completed = 0
			self.bar.emit(0, 1, 0)
			for meta_file_raw in sorted(game_meta_files):
				log("Reading Metadata File", "D", True)
				meta_file = os.path.join(paths["METADATA"], system) + "/" + meta_file_raw
				meta = json.load(open(meta_file))

				game_form = form(meta["Name"][0])
				output.append("\t<game>")

				# File
				output.append(f'\t\t<path>{meta["File"]}</path>')

				# Name
				output.append(f'\t\t<name>{meta["Name"][0]}</name>')

				# Developer, Publisher, Genre
				if ("Developers" in meta):
					output.append(f'\t\t<developer>{meta["Developers"][0]}</developer>')
				if ("Publishers" in meta):
					output.append(f'\t\t<publisher>{meta["Publishers"][0]}</publisher>')
				if ("Genres" in meta):
					output.append(f'\t\t<genre>{meta["Genres"][0]}</genre>')

				# Description
				if ("Overview" in meta):
					output.append(f'\t\t<desc>{filter_escapes(meta["Overview"][0])}</desc>')

				# Players
				if ("Max Players" in meta):
					output.append(f'\t\t<players>{meta["Max Players"][0]}</players>')

				# Release Date
				if ("Release Date" in meta):
					if len(meta["Release Date"]) > 0:
						# Check if full release date or only year
						if (len(meta["Release Date"][0]) > 4):
							# Full Release Date
							release_date_parts = meta["Release Date"][0].split()

							# Requires some formatting from MMMM DD, YYYY to YYYYMMDD
							release_date_parts[0] = calendar_month[release_date_parts[0]]
							release_date_parts[1] = release_date_parts[1].replace(",","")
							if int(release_date_parts[1]) < 10 and not("0" in release_date_parts[1]):
								release_date_parts[1] = "0" + release_date_parts[1]

							output.append(f'\t\t<releasedate>{release_date_parts[2]}{release_date_parts[0]}{release_date_parts[1]}T000000</releasedate>')

						else:
							# Year Only
							output.append(f'\t\t<releasedate>{meta["Release Date"][0]}0101T000000</releasedate>')

				# Rating
				if ("Rating" in meta):
					rating_conv = float(meta["Rating"][0]) / 5
					output.append(f'\t\t<rating>{rating_conv}</rating>')


				# Images
				# Check Images By Region
				boxarts = []
				for img in meta["Images"]:
					if "Box - Front" in img:
						boxarts.append(img)

				valid_image_exists = False
				for reg in regions[self.options_loc["region"]]:
					for img in boxarts:
						if reg in img:
							# Valid
							valid_image_exists = True
							# Check for file
							if (os.path.isfile(os.path.join(paths["MEDIA"], system, game_form) + "/" + img + ".png")):
								# Copy File
								log(f"Copying {img}.png to folder", "D", True)
								shutil.copyfile(os.path.join(paths["MEDIA"], system, game_form) + "/" + img + ".png", os.path.join(out_folder, "media", "boxFront") + "/" + img + ".png")
								# Add to Output
								output.append(f"\t\t<image>media/boxFront/{img}.png</image>")
							else:
								log(f"Couldn't copy {img}, doesn't exist", "I")

							break

					if valid_image_exists:
						break

				# Check Regionless Images
				if not(valid_image_exists):
					for img in boxarts:
						if not("(" in img):
							# Valid
							valid_image_exists = True
							# Check for file
							if (os.path.isfile(os.path.join(paths["MEDIA"], system, game_form) + "/" + img + ".png")):
								# Copy File
								log(f"Copying {img}.png to folder", "D", True)
								shutil.copyfile(os.path.join(paths["MEDIA"], system, game_form) + "/" + img + ".png", os.path.join(out_folder, "media", "boxFront") + "/" + img + ".png")
								# Add to Output
								output.append(f"\t\t<image>media/boxFront/{img}.png</image>")
							else:
								log(f"Couldn't copy {img}, doesn't exist", "I")

							break


				# Video
				video_title = meta["Name"][0] + " - Video"

				for f in os.listdir(os.path.join(paths["MEDIA"], system, game_form)):
					if video_title in f:
						log(f"Copying {f} to video folder", "D", True)

						shutil.copyfile(os.path.join(paths["MEDIA"], system, game_form) + "/" + f, os.path.join(out_folder, "media", "video") + "/" + f)

						output.append(f"\t\t<video>media/video/{img}.png</video>")

				output.append("\t</game>")

				completed += 1
				self.bar.emit(2, completed, len(game_meta_files))

			output.append("</gameList>")

			# Output to document
			if (os.path.isfile(os.path.join(out_folder, "gamelist.xml"))):
				os.remove(os.path.join(out_folder, "gamelist.xml"))

			log("Writing Output", "I")
			output_file = open(os.path.join(out_folder, "gamelist.xml"), "a")

			for line in output:
				output_file.writelines(line + "\n")

			output_file.close()

			self.bar.emit(0, 0, 0)
			self.out.emit("Finished Output. Exiting...")






		else:
			self.out.emit("Please Scrape Games Before Exporting. Exiting...")
			log("Invalid Export", "I")


		self.complete.emit()
