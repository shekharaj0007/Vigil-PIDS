# Presentation Outline — Vigil PIDS Weather Calibration

Suggested 6–8 slide deck for the review panel. Export to PDF and include your **video demo link** in the final submission PDF (`TeamName_CollegeName_A-1Launchpad_2026.pdf`).

## Slide 1 — Title

- Weather-Based Sensor Calibration Suggestion System  
- Specialization: Software Development + AI/ML  
- Team name, college, date

## Slide 2 — Problem

- PIDS false alarms rise with wind, rain, storms, humidity, temperature swings  
- Operators need timely sensitivity guidance linked to live environment

## Slide 3 — Solution overview

- Live Open-Meteo weather → risk scoring → sensitivity recommendation → operator dashboard  
- Persisted history for analytics/reporting

## Slide 4 — Architecture

- React dashboard ↔ FastAPI ↔ Open-Meteo + SQLite  
- (Use diagram from `docs/ARCHITECTURE.md`)

## Slide 5 — Recommendation logic

- Weighted factors: wind 40%, rain 22%, storm 23%, temp 8%, humidity 7%  
- Examples: High wind → Low; Calm → High; Heavy rain → Medium; Storm → Very Low

## Slide 6 — Demo highlights

- Live city presets  
- Scenario buttons for presentations  
- Analytics & history

## Slide 7 — Deliverables & stack

- GitHub source, docs, sample data, this presentation, video link  
- FastAPI, React, Open-Meteo, SQLite

## Slide 8 — Future work

- Zone-level profiles per fence segment  
- ML model trained on historical false-alarm labels  
- Direct push of sensitivity profiles into Vigil PIDS controllers  
- Auth + multi-site fleet view

## Video link (add before submission)

```
Demo video: <paste Unlisted YouTube / Drive link here>
```
