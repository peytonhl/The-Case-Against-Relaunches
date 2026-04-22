# The Case Against the Relaunch

**A data-driven business case for long-term IP investment in Marvel's publishing model.**

Built by Peyton Lindogan · Python · Streamlit · Plotly · Pandas · SciPy

---

## What This Is

An interactive data product arguing that Marvel's relaunch publishing strategy erodes long-term franchise IP value — and that the comics pipeline is the upstream half of a $30B film franchise. The project combines original datasets, statistical analysis, and a structured executive brief to make a falsifiable, evidence-backed argument.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Data Sources                        │
│                                                         │
│  Comichron          Rotten Tomatoes     Box Office Mojo │
│  (sales estimates)  (MCU scores)        (gross figures) │
│        │                  │                   │         │
└────────┼──────────────────┼───────────────────┼─────────┘
         │                  │                   │
         ▼                  ▼                   ▼
┌─────────────────────────────────────────────────────────┐
│                     data/ (CSV layer)                   │
│                                                         │
│  asm_relaunches.csv       relaunch_multi.csv            │
│  writer_tenure.csv        mcu_films.csv                 │
│  mcu_characters.csv       franchise_boxoffice.csv       │
└────────────────────────────┬────────────────────────────┘
                             │  pandas.read_csv()
                             ▼
┌─────────────────────────────────────────────────────────┐
│                  src/pages/ (page modules)              │
│                                                         │
│  page0_exec_summary.py    page4_mcu.py                  │
│  page1_thesis.py          page5_business_case.py        │
│  page2_relaunch.py        page6_peter_parker.py         │
│  page3_tenure.py          page6_assumptions.py          │
│  page4_characters.py                                    │
│                                                         │
│  Each module exposes a single render() function         │
│  Called by app.py based on sidebar selection            │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│               src/utils/styling.py                      │
│                                                         │
│  inject_css()    page_header()    prose()               │
│  pull_quote()    stat_cards()     chart_annotation()    │
│  section_heading()  data_note()  rec_box()              │
│  PLOTLY_LAYOUT   AXIS_STYLE                             │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│                    app.py (entry point)                 │
│                                                         │
│  st.set_page_config()                                   │
│  PAGES dict -> sidebar radio -> PAGES[selection].render()│
└─────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Tool | Version |
|---|---|---|
| App framework | Streamlit | 1.32.2 |
| Visualization | Plotly | 5.22.0 |
| Data manipulation | Pandas | — |
| Statistical analysis | SciPy | — |
| Numerical computation | NumPy | — |
| Runtime | Python | 3.8 |

---

## Statistical Methods

**MCU Pipeline (Section 06)**
- Welch's two-sample t-test (unequal variance) comparing Strong vs. Weak source material RT scores
- 95% confidence intervals via Student's t-distribution
- Cohen's d effect size (pooled standard deviation)

**Relaunch Bump Decay (Section 02)**
- OLS linear regression (numpy.polyfit) fitted per relaunch volume on confirmed Comichron data
- R² computed from residual vs. total sum of squares
- Slope interpreted as thousands of copies lost per issue (decay rate)

---

## Data

| File | Source | Confidence |
|---|---|---|
| `asm_relaunches.csv` | Comichron (Diamond) / PRH estimates | Confirmed through 2021; estimated post-2021 |
| `relaunch_multi.csv` | Comichron; author estimates for Cap/Thor | Mixed — see Appendix |
| `writer_tenure.csv` | Marvel wikia / author-compiled | Author-compiled |
| `mcu_films.csv` | Rotten Tomatoes / author classification | RT scores confirmed; source depth is author judgment |
| `mcu_characters.csv` | Marvel wikia / author-compiled | Author-compiled |
| `franchise_boxoffice.csv` | Box Office Mojo / The Numbers | Confirmed |
| `data/marvel.db` | SQLite snapshot (ComicVine API + CSVs above) | Committed to repo; re-generate with `scripts/ingest.py` |

Data confidence is classified throughout as **Confirmed**, **Estimate**, or **PRH Estimate**.
See `src/pages/page6_assumptions.py` for full methodology documentation.

### Data Pipeline

The app reads from a committed SQLite snapshot (`data/marvel.db`) — no API keys required at runtime.

To refresh the data:

```bash
# Install dependencies
pip install requests pandas python-dotenv

# Set your ComicVine API key (free at comicvine.gamespot.com)
cp .env.example .env
# edit .env and add COMICVINE_API_KEY=your_key_here

# Re-run the ingest pipeline
python scripts/ingest.py
```

The script pulls character appearance counts from ComicVine for 18 major Marvel characters and seeds all CSV data into the database.

---

## Project Structure

```
Business Case for Comics/
├── app.py                        # Entry point, page registry, sidebar
├── README.md
├── .env.example                  # API key template (copy to .env)
├── scripts/
│   └── ingest.py                 # ETL pipeline: CSVs + ComicVine → marvel.db
├── data/
│   ├── marvel.db                 # SQLite snapshot (committed; re-generate with ingest.py)
│   ├── asm_relaunches.csv
│   ├── relaunch_multi.csv
│   ├── writer_tenure.csv
│   ├── mcu_films.csv
│   ├── mcu_characters.csv
│   └── franchise_boxoffice.csv
└── src/
    ├── pages/
    │   ├── page0_exec_summary.py
    │   ├── page1_thesis.py
    │   ├── page2_relaunch.py
    │   ├── page3_tenure.py
    │   ├── page4_characters.py
    │   ├── page4_mcu.py
    │   ├── page5_business_case.py
    │   ├── page6_peter_parker.py
    │   └── page6_assumptions.py
    └── utils/
        └── styling.py            # Design system: CSS, layout helpers, Plotly defaults
```

---

## Running Locally

```bash
pip install streamlit plotly pandas scipy numpy
streamlit run app.py
```

Or with pinned versions:

```bash
pip install streamlit==1.32.2 plotly==5.22.0 pandas scipy numpy
streamlit run app.py
```

The app runs entirely from the committed `data/marvel.db` — no external API calls needed at runtime. To refresh the database, see **Data Pipeline** above.

---

## Argument Structure

```
Executive Summary  -->  The Thesis (framework + definitions)
                              |
                    +---------v----------+
                    |  02: Relaunch Bump  |  Sales data: relaunch cycles
                    |      Decay         |  erode sustained readership
                    +---------+----------+
                              | anomaly: Spider-Man holds
                    +---------v----------+
                    |  03: Peter Parker   |  Why Spider-Man is resilient:
                    |      Effect        |  alter ego depth = durable IP
                    +---------+----------+
                              |
                    +---------v----------+
                    |  04: Writer Tenure  |  Structural cause: tenure
                    +---------+----------+  compression cuts runway
                              |
                    +---------v----------+
                    |  05: Character      |  How deep is the catalog?
                    |      Ledger        |  Years of development per MCU char
                    +---------+----------+
                              |
                    +---------v----------+
                    |  06: MCU Pipeline   |  Comics depth -> film quality
                    |      Quality       |  (statistically significant)
                    +---------+----------+
                              |
                    +---------v----------+
                    |  07: Business Case  |  Three concrete recommendations
                    +---------+----------+
                              |
                         Appendix
                    (data sourcing + methodology)
```

---

## Limitations and Honest Caveats

- **Sample size**: ~30 MCU films. Statistical tests are significant but should be interpreted with appropriate caution given n.
- **Source material depth classification**: Author judgment. Documented in the Appendix; reasonable to disagree at the margins.
- **Post-2021 sales data**: PRH does not publish Diamond-equivalent order data. Post-2021 figures are normalized estimates.
- **Causality**: Correlation between deep source material and RT scores does not establish that the comics *caused* the film quality — only that they co-occur consistently.

---

*By Peyton Lindogan*
