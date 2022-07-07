# bigscraper-qt

## LaunchBox scraping tool

Bigscraper-qt is a tool you can use to scrape [the LaunchBox Games Database.](https://gamesdb.launchbox-app.com/) With a simple GUI, you can easily scrape metadata from a variety of systems.

If you want more information, head to [the website](https://fr75s.github.io/bigscraperqt/). This README will mainly serve as information regarding the development of bigscraper-qt.

Need help? For quick support, [Visit the Discord Server.](https://discord.gg/DUAFMgrhAY). If it is a severe enough problem, you may put it into the [issue tracker.](https://github.com/Fr75s/bigscraperqt/issues)

## Running from Source

Ensure you have the following dependencies installed:

- Qt5

- The following python packages:
	- PyQt5
	- requests
	- yt_dlp
	- inputs
	- Unidecode
	- lxml
	- xdg

Then, download the source code.

	$ git clone https://github.com/Fr75s/bigscraperqt.git
	$ cd bigscraperqt

After you download the source code, simply run the following. You may append a `-n` flag to test the flatpak version behavior.

	$ python3 -m bsqt


## Building from Source

To build from source, first clone the repository.

	$ git clone https://github.com/Fr75s/bigscraperqt.git
	$ cd bigscraperqt

Then, simply run one of the following, depending on which version to build:

	build-appimage:
	$ appimage-builder --skip-tests
	build-flatpak:
	# flatpak-builder build io.github.fr75s.bigscraper-qt.json --install --force-clean

## Planned Features

A list of new planned features are below.

- Flathub Release (flatpak availability)
- "All" export system option
- Export to Secondary frontend

Some of these features were in previous iterations; I hope to add them to bigscraper-qt as well:

- Asynchronous scraping (even more efficient)
- Clearing Cached data from application
