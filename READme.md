# Data Scraping Project

### Meta-Data

* Library(s) : Scrapy🧹
* WebSite : https://colouranddesign.com/ 🌐
* Data : All the product listed on the site mentioned above.

### Spiders is in Located In below Path:

`crowddatanalytix\canddspider\canddspider\spiders`

### There are two spiders:

1. coloranddesignspy : This spider doesn't use IteamLoader
2. canddspy : This Spider built using IteamLoader

### Run Spider:

##### **Step 1**: Cd to Spider Project Directory:

`cd canddspider`

##### **Step 2**: Run scrapy crawl [Spider name] ..E.g

`scrapy crawl canddspy`

##### For storing the data into json file you can run ..E.g

`scrapy crawl [spider name] -o filename.json`
