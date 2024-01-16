<p>
    <img src="docs/red-sewer-fox.png" alt="Red Sewer Fox" width="128" height="128"> <br>
    <strong>Covid Fox Monitoring</strong> <br>
    <span class="subtext">A Covid Wastewater  Project</span>
</p>

## Project Direction
#### There are several <b>aims</b> that I want to fulfill with this project.<br>
* Give People An Overview of Current Covid Transmission Levels
* Collect & Share Data Sources for people to use for their Covid-projects
<br><br>
#### In order to fulfill these aims the current project direction is <br>
* Find more Datalinks to Covid Wastewater Data <span style="color: DarkOrange;">🔨👷🚧⚠️  In Progress</span>
* Find ways to use social media data <span style="color: Red;">❌ Cancelled</span>
* Find ways to pull aggregated google trends search terms data by region 
* Find ways to pull aggregated mobility data per region
* Forecast covid transmission per country 1-4+ weeks ahead <span style="color: green;">&#10004; Completed</span>
* Forecasts per region
* Improve forecasts
* Add variant data for better predictions <span style="color: DarkOrange;">🔨👷🚧⚠️  In Progress</span>
* Improved data standardization <span style="color: DarkOrange;">🔨👷🚧⚠️  In Progress</span>
<br><br>
#### Reliability of The Project
* Find ways of better hosting (URGENT - Exceeding free github tier)  <span style="color: green;">&#10004; Completed</span>
* Data Quality Control 
* Implementation of proper CI/CD pipeline
* Testing prior to releases
* Full automation of independent daily updates
<br><br>

#### Outside of Scope (Currently)
* Simulations of NPI's & transmission level
<br><br>
<br><br>
#### Please Note: The graphs and data are to be interpreted carefully.

<br>

### Current Status
![Geo Map Viz](https://github.com/danieldynesius/covid/blob/main/docs/c19_wastewater_v0.3.3.gif)

[Link to Covid-19 Wastewater Monitoring Website (Click Here!)](https://danieldynesius.github.io/covid/)

<br>

### Colorization Rule (Current)
<b>Interpretation</b>
* <b>Sweden:</b> Red = "High Transmission". Based on the height of Uppsala wastewater measures during wave 1 2020.
* <b>All Other Countries:</b> Red = "Relatively High Transmission". Based on each country separately relative to the Min-Max values in the timeperiod.
* <b>Withinin</b> country comparisons can be made.
* <b>Between</b> country comparisons should <i>ONLY</i> be made with careful interpretation. The colors are relative, so I *believe* only relative time dimension interpretations are possible. NOT degree of transmission on a specific week. The reason is that almost each country uses different metrics to track transmission.

<br>

The Heuristic of the Swedish Cut-off Value of 10 and above indicated as "high transmission" (red).
![Trendline Viz](docs/se_uppsala_c19_first_recorded_peak.png)
<br><br><br>

## Trendline Charts
Later might update the trend graphs. The trick is to figure out how to create a concise & intuitive overview.
![Trendline Viz](docs/c19-trends.png)

## Prediction Models
A simple Neural Net implemented. <b> Caution:</b> Very early stage. Interpret carefully.
Known issues: 
* Bugs when running for some countries e.g. Finland and Poland.
* Will <b>not</b> capture sudden strong spikes.
![prediction](docs/prediction_model_1.png)


## Questions?
For questions, suggestions, requests or ideas:
Contact me on twitter or linkedin.

[![Twitter URL](https://img.shields.io/twitter/url/https/twitter.com/dynesius_.svg?style=social&label=Follow%20%40dynesius_)](https://twitter.com/dynesius_)


[![Linkedin](https://i.stack.imgur.com/gVE0j.png) LinkedIn](https://www.linkedin.com/in/danieldynesius/)&nbsp;

[Email: daniel.dynesius@stratega.ai](mailto:daniel.dynesius@stratega.ai)