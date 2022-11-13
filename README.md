# bigscraper-qt

[VISIT THE WEBSITE HERE](https://fr75s.github.io/bigscraperqt/)

## GUI Scraping tool

Bigscraper-qt is a tool you can use to scrape [the LaunchBox Games Database](https://gamesdb.launchbox-app.com/) and more. With a simple GUI, you can easily scrape metadata for a variety of systems.

If you want more information, head to [the website.](https://fr75s.github.io/bigscraperqt/) This README mainly serves as information regarding the development of bigscraper-qt.

Need help? For quick support or light feature suggestions, [Visit the Discord Server.](https://discord.gg/DUAFMgrhAY) If it is a problem of a big enough scope, you may put it into the [issue tracker.](https://github.com/Fr75s/bigscraperqt/issues).

## Running from Source

Ensure you have the following dependencies installed:

- Python 3
- Qt5

- The following python packages:
	- PyQt5
	- Unidecode
	- requests
	- inputs
	- yt_dlp
	- lxml
	- xdg

Then, download the source code.

	$ git clone https://github.com/Fr75s/bigscraperqt.git
	$ cd bigscraperqt

After you download the source code, simply run the following. To see available flags, append `-h`.

	$ python3 -m bsqt


## Building from Source

To build from source, first clone the repository.

	$ git clone https://github.com/Fr75s/bigscraperqt.git
	$ cd bigscraperqt

Then, simply run one of the following, depending on which version to build:

	build-appimage:
	$ appimage-builder --skip-tests

	build-flatpak:
	# flatpak-builder build io.github.fr75s.bigscraper-qt.json --force-clean [...]

## Planned Features

A list of new planned features are below.

- Flathub Release
- LaunchBox Asynchronous Scraping
- Clearing Cached data by system
