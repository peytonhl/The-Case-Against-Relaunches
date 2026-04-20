# The Case Against the Relaunch

A data-driven Streamlit application arguing that Marvel's short-term relaunch strategy is destroying long-term brand equity — and that this is a financially irrational decision for Disney.

## Thesis

Marvel Comics publishes more relaunch number ones than it has strong writers to fill them. Each new #1 generates a short-term sales bump, then collapses to a lower floor than the previous run. Writer tenures have shortened. Reader loyalty has eroded. And the MCU — which was built on decades of well-developed source material — is showing exactly what happens when that pipeline runs dry.

This application makes the argument in data across five sections:

1. **The Thesis** — The case laid out in full
2. **Relaunch Bump Decay** — ASM first-issue peaks and run trajectories, 1999–2022
3. **Writer Tenure Analysis** — ASM writer tenure lengths, 1963–2024
4. **MCU Pipeline Quality** — RT scores correlated with source material depth
5. **The Business Case** — A boardroom-style synthesis and five concrete recommendations

## Running the App

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project Structure

```
├── app.py                   # Entry point
├── requirements.txt
├── .streamlit/
│   └── config.toml          # Dark theme configuration
├── data/
│   ├── asm_relaunches.csv   # ASM relaunch sales data (pre-populated estimates)
│   └── mcu_films.csv        # MCU films with RT scores and source quality
├── src/
│   ├── pages/
│   │   ├── page1_thesis.py
│   │   ├── page2_relaunch.py
│   │   ├── page3_tenure.py
│   │   ├── page4_mcu.py
│   │   └── page5_business_case.py
│   └── utils/
│       └── styling.py       # CSS, layout helpers, Plotly theme
└── assets/                  # Reserved for images/logos
```

## Data Notes

### `data/asm_relaunches.csv`

Pre-populated with estimates based on Comichron historical data. To verify or update with precise figures, visit [comichron.com](https://www.comichron.com) and search for Amazing Spider-Man monthly sales data.

Schema:
| Column | Description |
|--------|-------------|
| `relaunch_volume` | ASM volume number (2, 3, 4, 5, 6) |
| `relaunch_year` | Year of the #1 issue |
| `writer` | Primary writer |
| `issue_num` | Issue number within the run (1, 2, 6, 12, 24, 36) |
| `orders` | Estimated North American direct market orders |

### `data/mcu_films.csv`

Pre-populated with RT critical scores as of April 2025 and author-classified source material quality.

Schema:
| Column | Description |
|--------|-------------|
| `film_title` | Film name |
| `year` | Release year |
| `rt_score` | Rotten Tomatoes critics score (%) |
| `phase` | MCU phase (1–6) |
| `source_quality` | `Strong` / `Moderate` / `Weak` |
| `source_run` | The comic run that served as primary source material |
| `source_writer` | Writer(s) of that run |

## Deploying to Streamlit Cloud

This app is Streamlit Cloud-ready with no modifications. Connect your GitHub repository, set the entry point to `app.py`, and deploy.

---

*A portfolio project in data storytelling. Argument and analysis are the author's own.*
