# Courier Assignment and Bottleneck Detection in Urban Food Delivery

This project studies food delivery in Washington, DC as a network problem. The main
goal is to measure how the structure of the road network constrains delivery
operations, first by locating bottlenecks, restaurant clusters, and fragile edges in
the street graph, and then by running a discrete event courier simulation on top of
that graph to evaluate assignment strategies, fleet sizes, and peak load behavior.

Authors: Bryce Grover and Tianyu Zhao. Georgetown University, DSAN network analysis
course, Summer 2026.

## Data

All data comes from open sources and is fetched programmatically in the first
notebook:

- Drivable street network: OpenStreetMap via OSMnx (https://www.openstreetmap.org)
- Restaurant POIs: OpenStreetMap amenity tags for restaurant, fast food, and cafe
- Census tract population: ACS 5-Year tract layer from Open Data DC (https://opendata.dc.gov)
- Traffic volumes: DDOT 2024 AADT segments from Open Data DC
- Licensing cross-check: ABCA liquor license locations from Open Data DC

The `data/raw` and `data/clean` folders are not included in this repository because
of course guidance on large files. To reproduce them, run notebooks 01 and 02, which
download and clean everything from the sources above. Delivery orders are synthetic,
generated in notebook 05 from restaurant locations and census population density,
because no public delivery logs exist for DC.

## Research Questions

Structure: where does the network break?

**RQ1:** Do simple metrics find the choke points, or is a more robust method needed?

**RQ2:** Is there an order volume the network simply cannot move fast enough to meet?

**RQ3:** Which roads give the most improvement if upgraded?

**RQ4:** Do restaurant clusters help or hurt delivery?

Operations: who delivers, and how?

**RQ5:** Which assignment method gives the fastest average delivery time?

**RQ6:** How does performance shift during the lunch and dinner rushes?

**RQ7:** How much worse is a targeted road closure than a random one?

**RQ8:** What is the ideal number of couriers for the network?

## Methods

### Network analysis

The cleaned network keeps the largest strongly connected component (10,027 nodes,
26,938 directed edges) with free flow travel time weights, imputed by highway type
where speed tags are missing. Bottlenecks are ranked with travel time weighted edge
betweenness centrality and compared against observed AADT and edge speed. Renovation
and closure effects are measured with small counterfactual experiments against
random controls.

### Demand simulation

A synthetic day of 15,188 orders arrives as a nonhomogeneous Poisson process with
lunch and dinner peak multipliers. Pickups draw from the restaurant POIs and dropoff
probabilities are proportional to node level population density.

### Courier simulation

A discrete event simulation processes the day on a precomputed all pairs shortest
path travel time matrix. Nearest Available Courier dispatches greedily at order
arrival. System-wide Batching matches the full fleet to waiting orders every 120
seconds with a greedy cheapest pair heuristic. Five fleet sizes between 100 and 800
couriers are swept in parallel worker processes.

## Repository Structure

```
notebooks/
  01_fetch_data.ipynb           data ingestion from OSM and Open Data DC
  02_clean_data.ipynb           network cleaning, speed imputation, POI snapping
  03_eda.ipynb                  exploratory analysis and figure generation
  04_network_analysis.ipynb     bottlenecks, clustering, renovation, closures
  05_simulation_setup.ipynb     order generation and shortest path matrices
  06_courier_simulation.ipynb   assignment strategies and fleet sweep
  sim_engine.py                 discrete event simulation engine
outputs/                        figures 01 to 13 and analysis artifacts
paper.qmd                       the research paper (Quarto)
references.bib                  citations
```

## Reproducing the Results

Requires Python 3.10+ with osmnx, geopandas, networkx, scipy, pandas, matplotlib,
and altair. Run the notebooks in order from 01 to 06. Each executes top to bottom
and later notebooks read only the files earlier ones produce. Rendering the paper
requires Quarto:

```
quarto render paper.qmd --to pdf
```

## Key Findings

Betweenness centrality finds chokepoints that simple metrics miss, led by the
Southeast Freeway and the 3rd Street Tunnel, with only 8 percent overlap between
the top edges by observed volume and by betweenness. Restaurants cluster strongly
(Clark-Evans R of 0.32) and clustered restaurants reach demand about 16 percent
faster than isolated ones. The grid is robust to random closures but roughly forty
times more sensitive to targeted ones. Operationally, a fleet near 500 couriers
meets a 45 minute p95 standard against a 20.5 minute physical floor, system-wide
batching beats greedy dispatch by about 2 percent under courier scarcity, and
capacity binds at the dinner peak near 1,500 orders per hour rather than at daily
volume. Full results are in the paper.
