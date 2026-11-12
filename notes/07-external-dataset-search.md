# 07 — Searching for an external accessibility dataset (and why none fit)

## The problem I was trying to solve

The baseline classifier (notes/06) hit a hard wall: only 16 real `wheelchair: no` examples in all of Downtown Toronto — nowhere near enough for a classifier to learn the minority class, and `class_weight="balanced"` couldn't fix it either (reweighting can't invent data that doesn't exist). Before accepting that limit, I went looking for a second, richer data source specifically for wheelchair/curb-ramp accessibility in Toronto.

## What I checked

1. **Project Sidewalk** — a real, well-known crowdsourced sidewalk-accessibility labeling platform, deployed in dozens of cities worldwide. Checked whether Toronto is one of them: the project's main domains all redirect to a Chicago-specific deployment, and nothing found confirms a Toronto instance exists.

2. **RampNet** (a 2025 curb-ramp detection dataset built from Street View images) — exists, but the specific cities it covers weren't confirmed, and nothing tied it to Toronto.

3. **City of Toronto Open Data — Pedestrian Network ("pednet")** — this looked like the best lead by its description ("an attempt to semi-automate the creation of a pedestrian network model for **accessibility routing**"). Downloaded the real CSV (87,105 rows) and inspected its actual columns directly, not just the dataset's description:

   ```
   ROAD_TYPE, SIDEWALK_CODE, SIDEWALK_DESCRIPTION, CROSSWALK, CROSSWALK_TYPE, PX, PX_TYPE, LENGTH, geometry
   ```

   `SIDEWALK_DESCRIPTION` only has values like `"Sidewalk on both sides"` or `"No sidewalk on either side"` — sidewalk *presence/location*, not condition. `CROSSWALK_TYPE`/`PX_TYPE` are just crossing-type codes (`pc`, `ts`, `ns`), with no accessibility flag at all. **The word "accessibility" in this dataset's own description turned out to mean something different than I assumed** — it's used in the urban-planning sense (how long it takes to walk to amenities like schools and hospitals), not the disability-accommodation sense I was looking for. Same word, different field entirely.

4. **City of Toronto Open Data — Traffic Signals Tabular** — possibly has an "Audible tone" field (relevant to Accessible Pedestrian Signals at crossings specifically), but this is intersection-level, not path-level, and wasn't independently verified by downloading and checking columns the way pednet was.

## The real finding

**No ready-made external dataset solves this gap for Toronto specifically.** This isn't a failure of the search — it's a genuine, documented limitation that mirrors why this project's whole premise (accessibility data being sparse and inconsistently collected) is a real problem worth working on in the first place.

## Decision: proceed to the GNN anyway, with the limitation stated upfront

Rather than stall on data collection (manual labeling from Street View, or waiting for a better public dataset), the decision was to build the GNN on the real 16/178 labeled edges that exist, clearly documenting the small-sample limitation rather than hiding it. The value of this step isn't a production-ready classifier — it's demonstrating the actual mechanism (how a GNN uses graph neighborhood structure differently from the baseline) correctly, honestly scoped to what the real data can support.

**Next:** build the GNN model (`src/ml/`), compare it against the Module 6 baseline on the same small, real, geographically-split dataset.
