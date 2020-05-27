import React from 'react';
import ReactDOM from 'react-dom';
import GoogleMapReact from 'google-map-react';

import {Wordcloud} from '../../../../wordcloud/static/wordcloud/js/Wordcloud';
import {GoogleMapsOverlay} from '@deck.gl/google-maps';
import {HexagonLayer} from '@deck.gl/aggregation-layers';
import {GeoJsonLayer} from '@deck.gl/layers';
import {AmbientLight, PointLight, LightingEffect} from '@deck.gl/core';

import {map_styles} from './map_styles';
import DatePicker from 'react-datepicker';
import Select from 'react-select';

// prefix urls with /wordcrowd for on the production server
const prefix = window.prefix;

// Lighting effects for deckgl
const ambientLight = new AmbientLight({
    color: [255, 255, 255],
    intensity: 1.0
});
const pointLight1 = new PointLight({
    color: [255, 255, 255],
    intensity: 0.8,
    position: [-0.144528, 49.739968, 80000]
});
const pointLight2 = new PointLight({
    color: [255, 255, 255],
    intensity: 0.8,
    position: [-3.807751, 54.104682, 8000]
});
const lightingEffect = new LightingEffect({ambientLight, pointLight1, pointLight2});
const material = {
    ambient: 0.64,
    diffuse: 0.6,
    shininess: 32,
    specularColor: [51, 51, 51]
};


class CovidMap extends React.Component {
    static defaultProps = {
        center: {
            lat: 51.0531275,
            lng: 3.7230032
        },
        zoom: 4
    };

    static colors = ['#377eb8', '#ff0029', '#66a61e', '#984ea3', '#00d2d5',
        '#ff7f00', '#af8d00', '#7f80cd', '#b3e900', '#c42e60', '#a65628',
        '#f781bf', '#8dd3c7', '#bebada', '#fb8072'];

    constructor(props) {
        super(props);
        const latlng = {lat: 51.0531275, lng: 3.7230032};
        this.state = {
            // Zoom level 0 - 22, 22 is most zoomed in
            zoom: 4,
            // Words that will be shown in wordcloud for current position
            // OR for clicked Hex/Country
            words: [],
            wordsPos: [],
            wordsNeg: [],
            wordsMeta: null,
            maxWords: 100,
            wordcloudVisible: false,
            orientations: [],
            tweetsVisible: true,
            mapRef: null,
            mapsRef: null,
            // Array of all tweets containing:
            // ID,polarity,timestamp,coordinates,language
            all_tweets: [],
            // Array of tweets visible (used to filter the data client side)
            visible_tweets: [],
            overlay: null,
            startDate: new Date(),
            endDate: new Date(),
            langOptions: [],
            selectedLang: null,
            minDate: new Date(),
            maxDate: new Date(),
            countries: [],
            geojsonLayers: [],
            countriesVisible: false,
            amounts: []
        };
    }

    componentDidMount() {
        // Initialize the pop-up modals and their events
        const wordcloudModal = $('#wordcloud-modal');
        const multiWordcloudModal = $('#multi-wordcloud-modal');
        wordcloudModal.on('shown.bs.modal', () => {
            this.setState({wordcloudVisible: true});
        });
        wordcloudModal.on('hide.bs.modal', () => {
            this.setState({wordcloudVisible: false})
        });


        multiWordcloudModal.on('shown.bs.modal', () => {
            this.setState({wordcloudVisible: true});
        });
        multiWordcloudModal.on('hide.bs.modal', () => {
            this.setState({wordcloudVisible: false})
        });

        // Toggle hex/countries
        $('#toggle-countries').click(() => {
            if (this.state.countriesVisible) {
                this.setState({countriesVisible: false}, () => this.redrawOverlays());
            } else {
                this.setState({countriesVisible: true}, () => this.redrawOverlays());
            }
        });

        // Filter visible data
        $('#filter-data').click(() => {
            // Get the ISO datestring to compare
            const startDateString = this.state.startDate.toISOString().split('T')[0];
            const endDateString = this.state.endDate.toISOString().split('T')[0];

            const filtered_tweets = this.state.all_tweets.filter(t => {
                if (this.state.selectedLang) {
                    return t.timestamp >= startDateString && t.timestamp <= endDateString
                        && t.lang.toLowerCase() === this.state.selectedLang
                } else return t.timestamp >= startDateString && t.timestamp <= endDateString
            });
            this.setState({visible_tweets: filtered_tweets}, () => {
                this.redrawOverlays();
            });

        });

        // Get range of dates for tweets + different languages
        fetch(prefix + '/location/getFilterOptions/')
            .then(res => res.json())
            .then(data => {
                const minDate = new Date(data.min_date);
                const maxDate = new Date(data.max_date);
                this.setState({
                    langOptions: data.lang_options.map(d => ({value: d, label: d})), minDate: minDate, maxDate: maxDate,
                    startDate: minDate, endDate: maxDate
                })
            })
    }

    // Called on zoom in/out
    updateState = (map) => {
        const zoomLevel = map.getZoom();
        this.setState({zoom: zoomLevel});
        this.redrawOverlays();
    };


    // Create hexgonLayer
    hexagon = () => {

        const onHexClick = (object) => {
            // Get tweet ids and aggregate info of tweets inside the Clicked Hex

            const tweet_ids = {'tweet_ids': object.points.map(p => p.tweet_id)};
            const amount = object.points.length;
            const avg_polarity = Math.round((object.colorValue + Number.EPSILON) * 100) / 100;
            let sentiment;
            if (avg_polarity > 0.2) sentiment = 'Very Positive';
            else if (avg_polarity > 0.1) sentiment = 'Relatively Positive';
            else if (avg_polarity > -0.1) sentiment = 'Fairly Neutral';
            else if (avg_polarity > -0.2) sentiment = 'Relatively Negative';
            else sentiment = 'Very Negative';

            const meta = {'sentiment': sentiment, 'amount': amount, 'polarity': avg_polarity};

            // Get top 100 words for current tweet ids
            fetch(prefix + '/location/getWordcloud/', {
                method: 'POST',
                headers: {
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                },
                body: JSON.stringify(tweet_ids),
            }).then(res => res.json())
                .then(data => {
                    // Open modal and show wordcloud
                    this.setState({words: data.words, wordsMeta: meta}, () => {
                        $('#wordcloud-modal').modal('toggle');
                    });
                })
        };

        // Show info of hovered Hex
        const onHexHover = (object, x, y) => {
            const el = document.getElementById('tooltip');
            if (object) {
                const amount = object.points.length;
                const avg_polarity = Math.round((object.colorValue + Number.EPSILON) * 100) / 100;
                const sentiment = this.getSentiment(avg_polarity);
                el.innerHTML = `<h6>Amount of Tweets: ${amount}</h6>
                <h6>Polarity: ${avg_polarity}</h6>
                <h6>Sentiment: ${sentiment}</h6>`
                el.style.display = 'block';
                el.style.opacity = 0.9;
                el.style.left = x + 'px';
                el.style.top = y + 'px';
            } else {
                el.style.opacity = 0.0;
            }
        };
        // See deck.gl documentation for more info
        return new HexagonLayer({
            id: 'hex',
            data: this.state.visible_tweets,
            getPosition: t => [t.coords.lng, t.coords.lat],
            getColorWeight: t => t.polarity,
            colorAggregation: 'MEAN',
            colorRange: [[255, 0, 0], [255, 57, 0], [249, 198, 0], [238, 255, 0], [193, 255, 0], [102, 255, 0]],
            colorDomain: [-.5, .5],
            extruded: false,
            radius: 250000 * Math.pow(2, 4 - this.state.zoom),
            opacity: 0.4,
            coverage: 0.8,
            visible: !this.state.countriesVisible,
            material,
            pickable: true,
            autoHighlight: true,
            onClick: ({object}) => {
                onHexClick(object)
            },
            onHover: ({object, x, y}) => onHexHover(object, x, y)
        });
    };

    // Return sentiment for given polarity
    // We made it a bit more nuanced than simply positive/negative
    getSentiment = (polarity) => {
        let sentiment;
        if (polarity > 0.2) sentiment = 'Very Positive';
        else if (polarity > 0.1) sentiment = 'Relatively Positive';
        else if (polarity > -0.1) sentiment = 'Fairly Neutral';
        else if (polarity > -0.2) sentiment = 'Relatively Negative';
        else sentiment = 'Very Negative';
        return sentiment;
    };


    // Create geojson layers, one for each country (keeps the code simple that way)
    geojson = () => {

        const onGeojsonClick = (object) => {
            // Similar to onHexClick
            const amount = object.properties.amount;
            const polarity = Math.round((object.properties.polarity + Number.EPSILON) * 100) / 100;
            const sentiment = this.getSentiment(polarity);
            const meta = {
                'sentiment': sentiment,
                'amount': amount,
                'polarity': polarity,
                'country': object.properties.ADMIN
            };
            const tweet_ids = {'tweet_ids': object.properties.tweet_ids};
            fetch(prefix + '/location/getWordcloud/?country=1', {
                method: 'POST',
                headers: {
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                },
                body: JSON.stringify(tweet_ids),
            }).then(res => res.json())
                .then(data => {
                    this.setState({
                        words: data.words[0],
                        wordsPos: data.words[1],
                        wordsNeg: data.words[2],
                        amounts: data.amounts,
                        wordsMeta: meta
                    }, () => {
                        $('#multi-wordcloud-modal').modal('toggle');
                    });
                })
        };

        // Shows info on hover of country polygon
        const onGeojsonHover = (object, x, y) => {
            const el = document.getElementById('tooltip');
            if (object) {
                const amount = object.properties.amount;
                const polarity = Math.round((object.properties.polarity + Number.EPSILON) * 100) / 100;
                const sentiment = this.getSentiment(polarity);
                document.body.style.cursor = 'pointer';
                //const avg_polarity = Math.round((object.colorValue + Number.EPSILON) * 100) / 100;
                el.innerHTML = `<h5>${object.properties.ADMIN}</h5>
                <h6>Amount of Tweets: ${amount}</h6>
                <h6>Polarity: ${polarity}</h6>
                <h6>Sentiment: ${sentiment}</h6>`
                el.style.display = 'block';
                el.style.opacity = 0.9;
                el.style.left = x + 'px';
                el.style.top = y + 'px';

            } else {
                document.getElementById("body").style.cursor = "default";
                el.style.opacity = 0.0;
            }
        };


        let layers = [];

        // Get tweets for each country and calculate aggregate data
        for (let i in this.state.countries) {

            const current = this.state.countries[i];
            const country = current.name_iso;


            const tweets = this.state.visible_tweets.filter(t => t.country === country);
            const amount = tweets.length;
            const polarity = tweets.reduce((total, curr) => total + curr.polarity, 0) / amount;


            let color;
            if (polarity > 0.1) color = [102, 255, 0];
            else if (polarity > 0.05) color = [193, 255, 0];
            else if (polarity > 0) color = [238, 255, 0];
            else if (polarity > -0.05) color = [249, 198, 0];
            else if (polarity > -0.1) color = [255, 57, 0];
            else color = [255, 0, 0];


            let data = current.geojson;
            data.properties.amount = amount;
            data.properties.polarity = polarity;
            data.properties.tweet_ids = tweets.map(t => t.tweet_id);

            // See deck.gl documentation
            const layer = new GeoJsonLayer({
                id: current.name_iso,
                data: data,
                pickable: true,
                stroked: true,
                filled: true,
                extruded: true,
                lineWidthScale: 20,
                lineWidthMinPixels: 2,
                getFillColor: [...color, 180],
                getLineColor: [225, 225, 225, 180],
                getLineWidth: 10,
                autoHighlight: true,
                material,
                visible: this.state.countriesVisible,
                onHover: ({object, x, y}) => onGeojsonHover(object, x, y),
                onClick: ({object}) => onGeojsonClick(object)
            });
            layers.push(layer)
        }
        return layers
    };


    // Need to redraw overlays because dynamic changing is apparently not supported with Google maps
    redrawOverlays = () => {

        // Make layers
        const hexagonLayer = this.hexagon();
        const geojsonLayers = this.geojson();

        // Remove previous overlays
        if (this.state.overlay) {
            this.state.overlay.finalize();
        }

        const overlay = new GoogleMapsOverlay({
            layers: [
                hexagonLayer,
                ...geojsonLayers
            ],
            effects: [lightingEffect]
        });
        overlay.setMap(this.state.mapRef);
        this.setState({overlay: overlay, geojsonLayers: geojsonLayers});
    };


// Google Maps API is loaded
    apiIsLoaded = (map, maps) => {

        // Keep reference to api objects
        this.setState({mapRef: map, mapsRef: maps});


        maps.event.addListener(map, 'zoom_changed', () => {
            this.updateState(map);
        });

        this.updateState(map, maps);

        // Get country geojson data
        fetch(prefix + '/location/getGeojson/')
            .then(res => res.json())
            .then(data => {

                this.setState({countries: data.geojson});

                // Get tweet data and show it on the map
                fetch(prefix + '/location/getTweets/?a')
                    .then(res => res.json())
                    .then(data => {
                        const all_tweets = data['tweets'];
                        this.setState({all_tweets: all_tweets, visible_tweets: all_tweets});
                        this.redrawOverlays();
                    });
            })
    };


    render() {

        // On right click of word in wordcloud, it is removed
        setTimeout(() => {
            const wc_words = $('.wordcloud-word');
            wc_words.off('contextmenu');
            wc_words.on('contextmenu', (e) => {
                e.preventDefault();
                if (this.state.countriesVisible) return;
                const clicked_text = $(e.target).text();
                this.setState({words: this.state.words.filter(w => w.text !== clicked_text)})
            });
        }, 1000);


        $('#spinner').hide(500);

        // Only show wordcloud(s) if they are visible (duh)
        let wordcloud;
        if (this.state.wordcloudVisible && !this.state.countriesVisible) {
            wordcloud = <Wordcloud words={this.state.words} maxWords={this.state.maxWords}
                                   orientations={this.state.orientations}/>
        }

        let wordclouds;
        if (this.state.wordcloudVisible && this.state.countriesVisible) {
            wordclouds = (
                <>
                    <h5>All tweets ({this.state.amounts[0]}):</h5>
                    <Wordcloud words={this.state.words} key='words' maxWords={this.state.maxWords}
                               orientations={this.state.orientations}/>
                    <h5>Positive tweets ({this.state.amounts[1]}):</h5>
                    <Wordcloud words={this.state.wordsPos} key='wordsPos' maxWords={this.state.maxWords}
                               orientations={this.state.orientations}/>
                    <h5>Negative tweets ({this.state.amounts[2]}):</h5>
                    <Wordcloud words={this.state.wordsNeg} key='wordsNeg' maxWords={this.state.maxWords}
                               orientations={this.state.orientations}/>
                </>
            )
        }

        // Same with the headings in the popup
        let headings;
        if (this.state.wordcloudVisible) {
            headings = (<div>
                <h6 className="modal-title mt-1">Amount of tweets: {this.state.wordsMeta.amount}</h6>
                <h6 className="modal-title">Average
                    Polarity: {this.state.wordsMeta.polarity}</h6>
                <h6 className="modal-title">Average Sentiment: {this.state.wordsMeta.sentiment}</h6>
            </div>)
        }
        const title = this.state.countriesVisible && this.state.wordsMeta ?
            'Wordcloud of tweets for ' + this.state.wordsMeta.country :
            'Wordcloud of tweets in selected area';


        return (
            <div>
                <div style={{height: '80vh', width: '100%', overflow: 'hidden', padding: 0, margin: 0}}>
                    <GoogleMapReact
                        bootstrapURLKeys={{key: 'AIzaSyC8aWWMnseiUF0hTk10mcg1SIu-eKxcMW0'}}
                        defaultCenter={this.props.center}
                        defaultZoom={this.props.zoom}
                        yesIWantToUseGoogleMapApiInternals={true}
                        onGoogleApiLoaded={({map, maps}) => this.apiIsLoaded(map, maps)}
                        heatmapLibrary={true}
                        options={{
                            gestureHandling: 'greedy', styles: map_styles
                        }}
                    >
                    </GoogleMapReact>
                </div>

                <div className="row mt-1 mb-0">
                    <div className="col">
                        <label className="mb-0">Total tweets: {this.state.visible_tweets.length}</label>
                    </div>
                </div>
                <h5 className="mt-2">Filter data</h5>
                <div className="row mt-2 mb-0">
                    <div className="col-4">
                        <label className="mb-1 mr-1"><strong>Language: </strong></label>
                        <Select
                            className="basic-single"
                            classNamePrefix="select"
                            defaultValue={null}
                            isClearable={true}
                            name="lang-select"
                            options={this.state.langOptions}
                            onChange={({value}) => this.setState({selectedLang: value})}
                        />
                    </div>
                </div>
                <div className="row mt-2 mb-0">
                    <div className="col-4">
                        <label className="mb-0 mr-1"><strong>Start date: </strong></label>
                        <DatePicker
                            name="startDate"
                            selected={this.state.startDate}
                            onChange={date => this.setState({startDate: date})}
                            selectsStart
                            startDate={this.state.startDate}
                            endDate={this.state.endDate}
                            minDate={this.state.minDate}
                            maxDate={this.state.maxDate}
                        />
                    </div>
                </div>
                <div className="row mt-2 mb-0">
                    <div className="col-4">
                        <label className="mb-0" style={{marginRight: '.7rem'}}><strong>End date:</strong></label>
                        <DatePicker
                            name="endDate"
                            selected={this.state.endDate}
                            onChange={date => this.setState({endDate: date})}
                            selectsEnd
                            startDate={this.state.startDate}
                            endDate={this.state.endDate}
                            minDate={this.state.startDate}
                            maxDate={this.state.maxDate}
                        />
                    </div>
                </div>

                {/*
                 Because the elevationLowerPercentile does not seem to be working with Google Maps, we skip this filter

                <div className="row mt-2 mb-0">
                    <div className="col-4">
                        <label className="mb-0"><strong>Min # of tweets per Hex:</strong></label>
                    </div>
                    <div className="col">
                        <input type="number" id="min-tweets" min="1"
                               onChange={event => this.setState({minTweets: event.target.value})}
                               value={this.state.minTweets}/>
                    </div>
                </div>
                 */}
                <div className="modal fade bd-example-modal-lg" id="wordcloud-modal" tabIndex="-1" role="dialog"
                     aria-labelledby="myLargeModalLabel"
                     aria-hidden="true">
                    <div className="modal-dialog modal-lg">
                        <div className="modal-content">
                            <div className="modal-header d-block">
                                <div className="d-flex">
                                    <h4 className="modal-title align-content-center">{title}</h4>
                                    <button type="button" className="close" data-dismiss="modal" aria-label="Close">
                                        <span aria-hidden="true">&times;</span>
                                    </button>
                                </div>
                                {headings}
                            </div>
                            <div className="modal-body" style={{padding: '.5rem'}} id="modalBody">
                                {wordcloud}
                            </div>
                            <div className="modal-footer">
                                <button type="button" className="btn btn-secondary" data-dismiss="modal">Close</button>
                            </div>
                        </div>
                    </div>
                </div>


                <div className="modal fade bd-example-modal-lg" id="multi-wordcloud-modal" tabIndex="-1" role="dialog"
                     aria-labelledby="myLargeModalLabel"
                     aria-hidden="true">
                    <div className="modal-dialog modal-lg">
                        <div className="modal-content">
                            <div className="modal-header d-block">
                                <div className="d-flex">
                                    <h4 className="modal-title align-content-center">{title}</h4>
                                    <button type="button" className="close" data-dismiss="modal" aria-label="Close">
                                        <span aria-hidden="true">&times;</span>
                                    </button>
                                </div>
                                {headings}
                            </div>
                            <div className="modal-body" style={{padding: '.5rem'}} id="modalBody">
                                {wordclouds}
                            </div>
                            <div className="modal-footer">
                                <button type="button" className="btn btn-secondary" data-dismiss="modal">Close</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}

export default CovidMap;


ReactDOM.render(<CovidMap/>, document.getElementById('map-app'));



