####
#### this is broken as the lib in use is broken
#### fix is out there..
####

#from ttsfix import scraper
from torrent_tracker_scraper import scraper

scraper = scraper.Scraper(
    infohashes=[
        "82026E5C56F0AEACEDCE2D7BC2074A644BC50990",
        "04D9A2D3FAEA111356519A0E0775E5EAEE9C944A",
    ]
)
results = scraper.scrape()
print(results)
