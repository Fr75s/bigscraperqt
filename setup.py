from setuptools import setup, find_packages

setup(
	name = "bigscraper-qt",
	version = "1.1.1",
	description = "Scrape Game Metadata from Launchbox",
	keywords = "scraper launchbox metadata",
	author = "Fr75s",

	packages = find_packages(exclude=["AppDir","appimage-build","build","share"]),

	include_package_data = True,
	install_requires = [
		"PyQt6"
		"xdg",
		"Unidecode",
		"yt_dlp",
		"lxml",
		"requests"
	]
)
