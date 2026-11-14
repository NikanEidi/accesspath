# Sensory & cognitive-load accessibility in Ontario — research before building

Pre-build research for a possible AccessPath extension: routing that accounts
for sensory/cognitive load (crowding, noise, construction) alongside the
existing physical accessibility weighting, specifically for Ontario/Toronto.
Written before writing any code, so the decision of what's actually worth
building is grounded in real sources, not assumptions.

## 1. The policy gap is real and confirmed

- Ontario's own accessibility law (AODA) set a target of full accessibility by
  2025. The **Fourth Independent AODA Review (the Donovan Review)** confirmed
  Ontario will not meet that goal. The public-sector deadline to file an
  accessibility compliance report was December 31, 2025, and it was missed by
  many organizations. [ontario.ca — accessibility rules for public sector
  organizations](https://www.ontario.ca/page/accessibility-rules-public-sector-organizations)
- The current legal web standard is WCAG 2.0 Level AA, with a planned move to
  WCAG 2.2 expected around 2027.

**One number from my original research pack does not hold up:** the claim
that "26% of Canadians with disabilities lack access to assistive technology
due to cost" is not the real national figure. Statistics Canada's actual 2022
table (3.5.A) puts unmet need due to cost for assistive aids/devices at
**15.5% nationally** (2022 Canadian Survey on Disability). A 2017 survey cycle
reported 17%. The number 26.4 does appear in StatCan's table, but attached to
a specific subgroup, not the general population of Canadians with
disabilities — using it as a headline stat would be a real mistake to avoid.
[StatCan Table 3.5.A, 2022](https://www150.statcan.gc.ca/n1/pub/89-654-x/2024001/tbl/tbl03_5a-eng.htm)
· [Canada.ca — extra costs of living with disabilities](https://www.canada.ca/en/employment-social-development/corporate/reports/research/extra-costs-living-disabilities.html)

## 2. Who this would actually be for, in Ontario specifically

There is **no published Ontario- or Canada-specific prevalence study for
"sensory processing disorder" as its own standalone condition** — it's
studied as a feature of other conditions, not tracked on its own. The
closest real numbers:

- Autism in Ontario adults: **~1.9%** (simulation-modelling study, national
  estimate 1.8%). [PMC — prevalence of autism among adults in Canada](https://pmc.ncbi.nlm.nih.gov/articles/PMC12198838/)
- Autism in children: rising, **2.0% → 3.0%** in recent years nationally.
- ADHD in children (ages 4–17, 5-province data including Ontario): **~8.6%
  prevalence**. [Canada.ca — chronic conditions in childhood](https://health-infobase.canada.ca/chronic-conditions/childhood/prevalence.html)
- Sensory difficulties show up as a *feature* of neurodevelopmental
  disorders at a wide, inconsistent range (20%–95% depending on the study and
  population) — not a single clean Ontario number to cite. Any single
  "X% of autistic Ontarians have sensory sensitivity" claim needs its source
  study named directly, or it shouldn't be used.

**Honest framing to use later (résumé/demo):** no precise Ontario "market
size" number exists for this yet. The honest claim is that autism, ADHD, and
chronic-fatigue/anxiety populations in Ontario are measured in the hundreds
of thousands, and none of the published figures above capture sensory needs
specifically — a real, acknowledged measurement gap, not evidence the need is
small.

## 3. Lived-experience evidence (not Ontario-specific, but directly relevant)

No Toronto/Ontario-specific advocacy report turned up directly, but the
underlying lived-experience research backs this closely — including one
detail I relate to personally, since I already wear headphones in crowded
places for the same reason:

- A 2026 *Disability & Society* study (Danish community project) found that
  "getting out into the city takes planning and mental effort" for disabled
  participants, who described carrying noise-canceling headsets and worrying
  about being drained afterward.
- A Wiley "Sensory City" chapter, drawing on autistic people's own writing,
  names fluorescent lighting and poorly sound-proofed buildings as causes of
  sensory overload that non-autistic designers often don't notice.
- The most methodologically relevant finding: a real applied pilot at
  **Adelaide Railway Station (Australia)**, run with autism-research partner
  Aspect, found through interviews that **noise is the dominant sensory
  channel**, and that *predictability* — not just low stimulation — is the
  underlying access need. That's a concrete, actionable finding for a
  weighting function: a route's *variance* in noise/crowding may matter as
  much as its average level. [iMOVE Australia — Adelaide pilot](https://imoveaustralia.com/project/project-outcomes/sensory-sensitivity-wayfinding-adelaide-railway-station-pilot)

## 4. Real, usable Ontario/Toronto data sources (checked, not assumed)

Checked directly against the Toronto Open Data CKAN API (`package_search`),
not just the (JavaScript-rendered, unreliable to scrape) catalogue website.

**Construction — real data, confirmed, better than expected:**
- **Road Reconstruction Program** — active/planned/completed full road
  rebuilds (drainage, curbs, boulevards, sidewalks); notes explicitly say
  work may close individual lanes or the entire road.
- **Road Resurfacing Program** — same kind of lane/road-closure detail, for
  resurfacing work.
- **Sidewalk Construction Program** — planned sidewalk construction
  locations along transportation corridors, refreshed 2026-11-13 (current).
- **Utility Cut Permits** — approximate locations where utility companies
  are permitted to excavate in the public right-of-way, **refreshed
  weekly** — the most current of the four.
- Correction: `building-permits-active-permits`, the dataset I originally
  pointed to, is **retired**. These four replace it as the real source for
  the construction dimension.
- All four are served under the Open Government Licence – Toronto. Their own
  notes caution that a planned project "doesn't guarantee the work is going
  to proceed" — treat as *planned/likely* closures, not certainties.

**Crowding — one real proxy exists:**
- **Traffic and Pedestrian Volumes** — camera-based counts, summary data
  covering 1984 to present, refreshed as recently as January 2025. Usable as
  a real "how busy is this street" signal. (The older "Pedestrian Network"
  dataset is retired; this replaces it.)

**Noise — no real dataset exists:**
- The only noise-related source is the **2017 Toronto Environmental Noise
  Study**, a PDF report, not an API-queryable dataset. Raw measurements would
  need to be requested from the city separately, and even then they're
  point-in-time, not a routable street-segment layer.
- No dataset found for real-time or historical noise at street-segment
  granularity.

**Implication for the build:** construction and crowding can use real
Toronto data directly — a genuinely different (better) situation than the
original wheelchair-tag problem. Noise is the one dimension that still needs
a proxy (e.g. proximity to arterial roads / highway tags from OSM) or a
synthetic stand-in, the same way `accessibility_weight()` already leans on
OSM tags rather than live sensor data where real data doesn't exist.


## 5. Academic grounding for methodology

- 2025 MDPI framework on neuroinclusive park wayfinding — treats cognitive
  load as the core design mechanism; recommends sensory zoning and calm
  parallel routes. Design guidance, not a routing algorithm.
  [doi.org/10.3390/architecture6030145](https://doi.org/10.3390/architecture6030145)
- PIUMA (Interactive Urban Maps for People with Autism Spectrum Disorder,
  2017) — point-of-interest filtering for quiet/low-crowd/soft-lighting
  conditions. Map personalization, not route-level scoring.
- ASSIST project — indoor navigation for blind and autistic users via
  Bluetooth beacons; found autistic participants responded well to visual
  and vibrotactile cues over complex verbal instructions.

## 6. The plan

**Scope:** extend AccessPath, don't restart it. Add a second accessibility
dimension — sensory/cognitive load — alongside the existing physical one.
Physical accessibility (wheelchair, surface, stairs) stays exactly as built.

**Core architecture decision: never blend physical and sensory into one
score.** Someone with a physical disability, someone with a sensory/cognitive
disability, and someone with both are three different people with different
needs — collapsing them into one number would hide *why* a route was chosen
or rejected, and could optimize for one person's need at the expense of
another's.

- `accessibility_weight()` (existing) stays untouched — physical only.
- A new `sensory_weight()` — crowding, construction, and (once a proxy
  exists) noise — stays fully separate.
- A `profile` selects which weight(s) apply to a given route request:
  `physical`, `sensory`, or `both` (and `both` composes the two explicitly,
  not by averaging them into something unreadable).
- This also keeps the system explainable: "avoided this street because of
  stairs" vs. "avoided this street because of construction noise" stay two
  distinct, reportable reasons, never merged into a single opaque score.

**Per-dimension data plan, based on section 4:**
- **Construction** → real Toronto data (Road Reconstruction Program, Road
  Resurfacing Program, Sidewalk Construction Program, Utility Cut Permits).
  Genuinely better data situation than physical accessibility ever had.
- **Crowding** → real Toronto data (Traffic and Pedestrian Volumes).
- **Noise** → no real dataset exists yet. Build a proxy from OSM (proximity
  to arterial/highway tags, commercial density) the same way the rest of
  `accessibility_weight()` already works, and document it honestly as a
  proxy, not real measured noise — same honesty standard as Clearwell.

**What stays honest in any write-up:** no invented Ontario-specific
prevalence number for sensory needs (section 2), no reused/incorrect 26%
stat (section 1), and noise explicitly labeled as a proxy, not real data.

**Not decided yet / next conversation:**
- Whether crowding + construction get folded into real-OSM-graph testing
  directly, or get their own Clearwell-style synthetic neighborhoods first
  (for controlled testing) before touching real Toronto data.
- Exact formula for `sensory_weight()` — construction/crowding are additive
  penalties like the physical function already does, but the Adelaide
  finding (variance/predictability matters, not just average level) may need
  a different shape than a flat penalty.
