# BDS-Project

The goal of this project is to provide an attractive dashboard for visualization of the coronavirus epidemic using geolocated tweets. These enable a spatiotemporal analysis of the global sentiment and its evolution as the crisis progresses.

Built with [`Django`](https://www.djangoproject.com/) & [`React`](https://reactjs.org/), 
uses [`React-wordcloud`](https://github.com/chrisrzhou/react-wordcloud) to generate the word clouds 
and [`Google-Map-React`](https://github.com/google-map-react/google-map-react) + [`deck.gl`](https://deck.gl/#/) for the map rendering.

Link to live demo: https://tw06v072.ugent.be/wordcrowd/covid/

## Project Structure

Because the website is built within the framework of a larger project, the code cannot be run as standalone code. Making a minimal working example of the website would require a lot of work and installation of many libraries and packages. Also the installation and configuration of NGINX/Gunicorn/Postgres/GEOS/npm/webpack can be tricky. We hope that this code can give enough insight into the project, paired with the live demo. We hope that this does not pose a problem, but shows we are capable of building and maintaining complex and scalable web services. The notebooks which were used for preprocessing can be run separately though.

The tweet data (tweets.zip) was zipped, because of the file size limits on Github. The files relating to the web application are saved under the folder app. Note that the filepaths in the app/ files will not be correct, as they were taken from the larger project. 

### Preprocessing & Sentiment Analysis
- **get_tweets_countries.py**: Code to gather tweets geolocated around selected cities
- **Hydration.ipynb**: Code to hydrate the tweet IDs contained in **april28-may26.json**, gathered from: https://ieee-dataport.org/open-access/corona-virus-covid-19-geolocation-based-sentiment-data
- **flair_classifier.py**: Code to test the Flair sentiment analysis
- **textBlob_vs_Flair.txt**: Results from textBlob and Flair, explains why we chose Flair
- **countries.geojson**: Geojson data for all countries on earth, gathered from: https://datahub.io/core/geo-countries
- **tweets.zip**: Zip file containing the extracted and preprocessed tweets
- **Merge_countries.ipynb**: Code to merge results from both datasets and aggregate per country (results are in tweets.zip)

### Web Application



## Project Architecture

The website runs on an NGINX server, with a Django/PostgresSql(+ GEOS) backend. For the frontend, we used Reactjs with Google Maps and Deck.gl. This enforces the standard MVC pattern and allows easy customization of both the backend and frontend with Python and Javascript.

After gathering and preprocesssing the tweets with the notebooks, we save them in a json file and later import them into our database. With Django, model classes are created, which represent the tweet objects in the SQL database. This eliminates the need for any SQL queries, making data manipulation much easier. The backend does most of the data manipulation and processing and exposes an API to the frontend.

When the application is started, it requests all of the available data from the backend server, this may take some seconds on the first load. Afterwards, the data is aggregated and visualized in two ways. A hexmap visualization (clustered on location) and a geojson visualization per country. The data in the app can also be filtered on date and language, our dataset however contains only English tweets, but the functionality is there. The filtering is done on the client side, to avoid unnecessary requests. Clicking on a feature on the map, will request the top 100 most frequent words associated with the tweets inside of the object and visualize them in a word cloud. This is done dynamically, so only the data for the current filter options is considered. For the country visualisation, we have made 3 wordclouds, one for all of the tweets, one for the positive tweets and one for the negative tweets.

**Note:** In order to increase performance, we recommend the Chrome browser with the setting **Use hardware acceleration when available** enabled.

## Authors
- **Kenzo Milleville** - kenzo.milleville@ugent.be
- **Dilawar Ali** - dilawar.ali@ugent.be


## Directory structure
- **assets/** - general assets such as json and csv files
- **static/** - static content such as javascript, (s)css, images... Collected from the apps using the `collectstatic` command (https://docs.djangoproject.com/en/2.1/howto/static-files/#deployment).
- **media/** - media content related to a model (https://docs.djangoproject.com/en/2.1/topics/files/)
- **wordcrowd/** - the project directory containing the root urls and settings
- all other directories are Django apps
