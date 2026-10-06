# Online Gate Project Dashboard – Phase II

A Streamlit dashboard for tracking progress on the Online Gate project at the German Jordanian University (GJU). It covers instructional design activities and instructor content readiness for each course and unit, and pulls its data live from Google Sheets.

## Features

- **Password-protected access**
- **Key metrics:** total progress, the active unit and its days left, active unit progress, the next unit, and the project deadline countdown
- **Sidebar filters:** semester, instructional designer, and course
- **Course snapshot:** select one course to see its progress, content readiness, remaining activities, status, and a unit-by-unit breakdown
- **Instructional designer progress** cards, from the Activity Log
- **Course status table:** Completed / In Progress / At Risk / Delayed
- **Charts:** progress per unit, active unit progress per course, and overall content readiness per course

## Data sources

The app reads four Google Sheets tabs, each published to the web as CSV (**File → Share → Publish to web → CSV**):

| Secret key | Sheet | Required columns |
|---|---|---|
| `URL_ACT` | Activity Log | `Course Name`, `Unit`, `Done`, `Led ID`, `Instructor` |
| `URL_CONT` | Content Readiness | `Course Name`, `Unit`, `Done`, `Led ID`, `Instructor` |
| `URL_INFO` | Course Info | `Course_Name`, `Term`, `ID_Lead`, `Instructor` |
| `URL_DEAD` | Unit Deadlines | `unit`, `start`, `End` |

A row counts as complete when its `Done` column contains `Done`.

## Running locally

1. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create `.streamlit/secrets.toml`. This file is ignored by Git, so it is **never committed**.
   ```toml
   APP_PASSWORD = "choose-a-password"
   URL_ACT  = "https://docs.google.com/spreadsheets/d/e/.../pub?gid=...&single=true&output=csv"
   URL_CONT = "https://docs.google.com/spreadsheets/d/e/.../pub?gid=...&single=true&output=csv"
   URL_INFO = "https://docs.google.com/spreadsheets/d/e/.../pub?gid=...&single=true&output=csv"
   URL_DEAD = "https://docs.google.com/spreadsheets/d/e/.../pub?gid=...&single=true&output=csv"
   ```
3. Start the app:
   ```bash
   streamlit run app.py
   ```

On Streamlit Community Cloud, add the same keys under **App settings → Secrets**.

## Configuration

- **Project deadline:** set `project_deadline` in `app.py`. It is the only place to change it.
- **Data refresh:** data is cached for 30 seconds (`@st.cache_data(ttl=30)`).

## Author

Designed and developed by Eng. Waed Alswaeer, waed.alswaer@gju.edu.jo
