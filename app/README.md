# app/ — web server and UI

**Owner:** Jonathan (see `ROLES.md`).

- `server.py`: stdlib `http.server` on port 8803 (`T3_PORT`). It serves `static/` and the JSON API in CONTRACT §8.
- `static/`: `index.html`, `app.js`, `styles.css`. Vanilla JS, no CDN, no build step, works offline.

Every page shows the `模拟 / SIMULATED` badge.
