# Software Requirements Specification (Epic 1)

## 1. Purpose
A web app that helps site engineers, small contractors and students audit site safety from photos,
diagnose cracks, estimate budgets/timelines/asset value, and plan work using the weather forecast.

## 2. Users
- Site engineer / supervisor
- Small contractor or home builder
- Student / learner

## 3. Functional requirements
| ID | Requirement |
|----|-------------|
| FR1 | User can upload a site photo and receive a structured safety audit (risk level, hazards, PPE, recommendations). |
| FR2 | User can upload a crack photo and receive type, severity, causes, repair steps and urgency. |
| FR3 | User can enter area, floors, quality grade and contingency to get a line-item budget. |
| FR4 | System generates a phase-wise timeline and Gantt chart from a start date. |
| FR5 | System estimates current building value using straight-line depreciation. |
| FR6 | AI layer explains the budget and suggests savings and risks. |
| FR7 | User can get 3-day weather-aware guidance for planned activities in a city. |
| FR8 | User can download the budget as CSV. |
| FR9 | Advisory engine converts safety, crack, weather and budget results into prioritised actions. |
| FR10 | User can chat with an assistant that knows the latest analysis results. |

## 4. Non-functional requirements
- Usability: single page, tabs, no login.
- Performance: images resized to <=1600 px before upload to the AI.
- Security: API key kept in session / `.env`, never committed (`.gitignore`).
- Reliability: friendly errors if the API or weather service fails.
- Safety: AI output is advisory; disclaimers shown in the UI.

## 5. Constraints and assumptions
- Needs internet and a Gemini API key (free tier available).
- Cost rates are editable rough figures in `data/material_rates.csv`.

## 6. Out of scope
User accounts, databases, exact structural calculations, real-time material price feeds.
