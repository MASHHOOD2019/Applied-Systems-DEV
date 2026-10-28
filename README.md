# Industry-Level Projects — Mashhood Ali

Three complete, working projects built for industry and PAEC/DTS-track
recruiters. Each has its own README with setup and run instructions.

| # | Project | Stack | Industry angle |
|---|---|---|---|
| 1 | `telemetry-logger` | Python, FastAPI, SQLite, JS | Plant/industrial data-logging + live dashboard |
| 2 | `secure-vault` | Python, cryptography (Fernet, PBKDF2) | Secure offline credential storage |
| 3 | `qa-bug-tracker` | HTML, CSS, JavaScript | QA workflow tool with exportable reports |

All three were tested end-to-end before delivery: API endpoints,
encryption round-trip (including wrong-password rejection), and JS
syntax checks all pass.

## Suggested next steps
1. Push these to GitHub (one repo, e.g. `industry-projects`).
2. LinkedIn post per project: problem → what you built → one lesson.
3. Next level after these: rebuild the bug tracker frontend in React +
   Tailwind, and add JWT auth + alert thresholds to the telemetry API.
