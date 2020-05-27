# BDS-Project

The goal of this project is to provide an attractive dashboard for visualization of the coronavirus epidemic using geolocated tweets. These enable a spatiotemporal analysis of the global sentiment and its evolution as the crisis progresses.

Built with [`Django`](https://www.djangoproject.com/) & [`React`](https://reactjs.org/), 
uses [`React-wordcloud`](https://github.com/chrisrzhou/react-wordcloud) to generate the word clouds 
and [`Google-Map-React`](https://github.com/google-map-react/google-map-react) + [`deck.gl`](https://deck.gl/#/) for the map rendering.

Link to live demo: https://tw06v072.ugent.be/wordcrowd/covid/

## Project Structure

Because the website is built within the framework of a larger project, the code cannot be run as standalone code. Making a minimal working example of the website would require a lot of work and installation of many libraries and packages. We hope that this code can give enough insight into the project, paired with the live demo. The notebooks which were used for preprocessing can be run separately though.

## Authors
- **Kenzo Milleville** - kenzo.milleville@ugent.be
- **Dilawar Ali** - dilawar.ali@ugent.be


## Directory structure
- **assets/** - general assets such as json and csv files
- **static/** - static content such as javascript, (s)css, images... Collected from the apps using the `collectstatic` command (https://docs.djangoproject.com/en/2.1/howto/static-files/#deployment).
- **media/** - media content related to a model (https://docs.djangoproject.com/en/2.1/topics/files/)
- **wordcrowd/** - the project directory containing the root urls and settings
- all other directories are Django apps
