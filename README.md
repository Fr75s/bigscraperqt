# bigscraper-qt

## LaunchBox scraping tool

Bigscraper-qt is a tool you can use to scrape [the LaunchBox Games Database.](https://gamesdb.launchbox-app.com/) With a simple GUI, you can easily scrape metadata from a variety of systems.

If you want more information, head to the website. This README will mainly serve as information regarding the development of bigscraper-qt.

## Running from Source

To run the source code, first download the source code.

	git clone https://github.com/Fr75s/bigscraperqt.git
	cd bigscraperqt

After you download the source code, simply run the following. You may append a `-n` flag to test the flatpak version behavior.

	python3 -m bsqt

## Building from Source

To build from source, first clone the repository.

	git clone https://github.com/Fr75s/bigscraperqt.git
	cd bigscraperqt

Once you clone the repository, switch to the build branch of choice. You can switch to either the `build-appimage` or `build-flatpak` branch for each build respectively.

	git checkout [build branch]

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
- More efficient folder scraping

Some of these features were in previous iterations; I hope to add them to bigscraper-qt as well:

- Asynchronous scraping (even more efficient)
- Clearing Cached data from application
