# Courier Assignment and Bottleneck Detection in Urban Food Delivery

This project studies food delivery in Washington, DC from two sides: the structure of the road network and the operational decisions made by a delivery platform. We identify road bottlenecks, estimate delivery capacity, test road upgrades and closures, compare courier assignment strategies, and determine a performance-based fleet size.

The analysis uses the Washington, DC OpenStreetMap road network, 2,043 restaurant locations, census tract population, observed 2024 traffic counts, and a simulated day of 15,188 delivery orders.

**Authors:** Bryce Grover and Tianyu Zhao  
**Course:** Georgetown University, Network Analysis, Summer 2026

## Research Questions

### Network structure

1. Do simple metrics find the choke points, or is a path-based method needed?
2. Is there an order volume the network cannot move fast enough to meet?
3. Which roads provide the most improvement if upgraded?
4. Do restaurant clusters help or hurt delivery?

### Delivery operations

5. Which courier assignment strategy gives the fastest average delivery time?
6. How does performance change during lunch and dinner peaks?
7. How much more damage do targeted road closures cause than random closures, and does assignment strategy matter?
8. What is the ideal number of couriers for the network?

## Data

The project combines open geographic data with simulated delivery demand:

- **Road network:** OpenStreetMap, downloaded with OSMnx
- **Restaurant locations:** OpenStreetMap restaurant, fast-food, and cafe POIs
- **Population:** ACS five-year census tract data from Open Data DC
- **Traffic volume:** DDOT 2024 Annual Average Daily Traffic data
- **Restaurant coverage check:** ABCA liquor-license locations
- **Delivery demand:** 15,188 synthetic orders with lunch and dinner peaks

The cleaned road network keeps the largest strongly connected component. It contains 10,027 intersections, 26,938 directed edges, and 1,928 km of streets. Missing speed values are estimated using the mean tagged speed for the same road type.

The `data/raw` and `data/clean` directories are not included because of their size. Run the data notebooks to download and rebuild them. Delivery orders are simulated because public delivery records are not available for Washington, DC.

## Methods

### Network analysis

- Rank road bottlenecks with travel-time-weighted edge betweenness centrality.
- Compare bottlenecks with observed traffic volume and road speed.
- Estimate hourly delivery capacity from the courier busy cycle.
- Test targeted road upgrades against random upgrades.
- Measure restaurant clustering with the Clark-Evans ratio.
- Compare travel time from clustered and isolated restaurants to the same demand sample.

### Delivery analysis

- Compare Nearest Available Courier (NAC) and System-wide Batching (SWB).
- Measure click-to-door time under fleets of 200 and 500 couriers.
- Compare lunch, dinner, and low-demand delivery performance.
- Close 1% of physical road segments and reroute all orders.
- Compare targeted closures with 30 random closure trials.
- Sweep fleet sizes from 100 to 800 couriers.

The ideal fleet is defined as the smallest tested fleet that delivers at least 99.5% of orders within 45 minutes under both strategies and gains less than one additional minute from the next tested fleet size.

## Key Findings

| RQ | Main result |
|:--:|---|
| 1 | Betweenness found bottlenecks that traffic volume and speed missed. Only 8% of the top 1% AADT and betweenness edges overlapped. |
| 2 | A 500-courier fleet can process about 1,461 orders per hour, below the dinner peak of 2,279 orders. |
| 3 | Targeted upgrades improved mean travel time by 0.09%; random upgrades produced almost no change. |
| 4 | Restaurants were strongly clustered (Clark-Evans R = 0.32), and clustered restaurants reached demand about 16% faster. |
| 5 | SWB was faster with 200 couriers, while NAC was slightly faster with 500 couriers. |
| 6 | A 200-courier fleet developed a large backlog during lunch and dinner. A 500-courier fleet kept average delivery time between 21 and 24 minutes. |
| 7 | Targeted closures caused about 4.25 times more delay and 4.5 times more route failures than random closures. NAC and SWB were affected almost equally. |
| 8 | The ideal tested fleet was 500 couriers. Both strategies delivered 100% of orders within 45 minutes, while larger fleets provided little improvement. |

Important bottlenecks included the 3rd Street Tunnel, Southeast Freeway, and Florida Avenue. The results show that delivery performance depends on both network structure and operational capacity.

## Repository Structure

```text
data/                                         Raw and cleaned project data
notebooks/
  01_fetch_data.ipynb                         Download OpenStreetMap and Open Data DC data
  02_clean_data.ipynb                         Clean the network and assign missing speeds
  03_eda.ipynb                                Explore the network, restaurants, and demand
  04_network_analysis.ipynb                   Analyze bottlenecks, clustering, and upgrades
  05_simulation_setup.ipynb                   Generate orders and shortest-path inputs
  06_courier_simulation.ipynb                 Run courier assignment simulations
  07_Fastest_Strategy.ipynb                   Compare NAC and SWB delivery times
  08_High_Demand_Delivery_Performance.ipynb   Analyze lunch and dinner delivery performance
  09_Targeted_vs_Random_Road_Closures.ipynb   Compare targeted and random road closures
  10_Ideal_Number_of_Couriers.ipynb           Identify the ideal fleet size
  sim_engine.py                               Discrete-event simulation engine
outputs/                                      Paper figures and analysis outputs
README.md                                     Project overview and instructions
references.bib                                Bibliography
paper.qmd                                     Quarto research paper
paper.pdf                                     PDF version of the paper
```