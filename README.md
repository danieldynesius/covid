# Europe Wastewater Data Viz - EARLY WIP
This is a work in progress to visualize Swedish covid wastewater data.
!DONT MAKE INTERPRETATIONS ON THESE GRAPHS YET!


## Please Note
This is a WIP. It has only undergone minor quality control.


## Current Status
![Geo Map Viz](https://github.com/danieldynesius/covid/blob/main/docs/c19_wastewater_v0.3.1.gif)

#### Countries visualized on Map (choropleth)

## SARS-CoV-2 Wastewater Plotting Variable (indicating color)
At the current stage of development Min-Max normalization was used for each country based on frequent data quality checks (for details see dataprocessing steps under step 2 in the repo). This makes within country comparisons possible.
From first glance it might SEEM that its possible to interpret across countries but that's probably Not the case. The reason for that is that is that underneath the normalization one country can still measure something thats not quite reflective of another country.


## Relative Copy Number - Heuristic (OLD METHOD for Sweden data only)
Relative Copy Number Cap was created by simple heuristic to in order to have the color meaning not being relative to included time period or country overall (which also might be effected by data of other countries or lack of reporting of one or another country. This will facilitate and standardize interpretability within Sweden for now, which later will be reviewed as more countries are added.

The range of Relative Copy Number is fixed based a heuristic based on Uppsala Wastewater during the first data wave. Uppsala a stable measurement across time, and as far as I remember Sweden had a very high transmission of SARS-CoV-2 during this time. I think it should serve as a decent estimate on the degree of covid transmission. 

![Trendline Viz](docs/se_uppsala_c19_first_recorded_peak.png)

#### Trendline Charts
![Trendline Viz](docs/c19-trends.png)


## Questions?
For questions, suggestions, requests or ideas:
Contact me on twitter or linkedin.

[![Twitter URL](https://img.shields.io/twitter/url/https/twitter.com/dynesius_.svg?style=social&label=Follow%20%40dynesius_)](https://twitter.com/dynesius_)


[![Linkedin](https://i.stack.imgur.com/gVE0j.png) LinkedIn](https://www.linkedin.com/in/danieldynesius/)&nbsp;
