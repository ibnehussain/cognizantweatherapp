# Contributing Guide — CognizantWeatherApp

Thank you for considering a contribution to CognizantWeatherApp! This document explains how to set up a development environment, the branching strategy, coding standards, and the pull request process.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Branching Strategy](#branching-strategy)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
  - [Python (Backend)](#python-backend)
  - [JavaScript (Frontend)](#javascript-frontend)
  - [HTML / CSS](#html--css)
- [Commit Messages](#commit-messages)
- [Pull Request Checklist](#pull-request-checklist)
- [Reporting Bugs](#reporting-bugs)
- [Requesting Features](#requesting-features)

---

## Code of Conduct

Be respectful and constructive. We follow the [Contributor Covenant](https://www.contributor-covenant.org/) code of conduct.

---

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:

   ```bash
   git clone https://github.com/<your-username>/cognizantweatherapp.git
   cd cognizantweatherapp
   ```

3. Set the upstream remote:

   ```bash
   git remote add upstream https://github.com/ibnehussain/cognizantweatherapp.git
   ```

4. Follow the [Quick Start](../README.md#quick-start-local) to run the app locally.

---

## Branching Strategy

| Branch | Purpose |
|---|---|
| `main` | Production-ready code; deploys automatically to Azure |
| `feature/<short-description>` | New features (e.g. `feature/5-day-forecast`) |
| `fix/<short-description>` | Bug fixes (e.g. `fix/cache-lock-race`) |
| `docs/<short-description>` | Documentation-only changes |
| `chore/<short-description>` | Tooling, dependency updates, CI changes |

Never push directly to `main`. Always open a pull request.

---

## Development Workflow

```bash
# 1. Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main

# 2. Create a feature branch
git checkout -b feature/my-new-feature

# 3. Make your changes and run the app
cd backend
python app.py

# 4. Stage and commit (see Commit Messages section)
git add .
git commit -m "feat: add 5-day forecast endpoint"

# 5. Push and open a pull request
git push origin feature/my-new-feature
```

---

## Coding Standards

### Python (Backend)

- **Style:** Follow [PEP 8](https://peps.python.org/pep-0008/). Maximum line length: **100 characters**.
- **Type hints:** Add type hints to all public functions and methods (Python 3.11+ syntax is fine).
- **Docstrings:** Use Google-style or NumPy-style docstrings for all public functions.
- **Imports:** Standard library → third-party → local; separated by blank lines.
- **Error handling:** Raise `WeatherServiceError` with an explicit `status_code` for any service-level failure; do not swallow exceptions silently.
- **No hardcoded secrets:** All sensitive values must come from environment variables via `config.py`.

**Example function signature:**

```python
def get_weather(city: str, api_key: str, base_url: str,
                ttl: int, timeout: int) -> dict:
    """
    Returns structured weather data for *city*.

    Parameters
    ----------
    city     : city name as received from the route
    api_key  : OWM API key
    ...
    """
```

### JavaScript (Frontend)

- **Strict mode:** The file already includes `'use strict';` — keep it.
- **Style:** 2-space indentation, single quotes, semicolons.
- **Functions:** Use `function` declarations for named functions; JSDoc comments for public functions.
- **DOM access:** Store element references at the top of the file (already done); do not call `getElementById` repeatedly inside loops.
- **Error handling:** Always `.catch()` or `try/catch` async calls; display errors via `showError()` — never `alert()` or `console.error()` only.
- **No frameworks:** Keep the frontend dependency-free. If a library is genuinely needed, open an issue for discussion first.

**Example JSDoc:**

```js
/**
 * Converts Celsius to Fahrenheit.
 * @param {number} c  Temperature in Celsius
 * @returns {number}  Temperature in Fahrenheit (rounded)
 */
function toFahrenheit(c) {
  return Math.round((c * 9) / 5 + 32);
}
```

### HTML / CSS

- **Accessibility first:** All interactive elements must have accessible names (`aria-label`, `<label for="…">`, or visible text).
- **Semantic HTML:** Use `<header>`, `<main>`, `<section>`, `<footer>`, `<nav>` appropriately.
- **CSS custom properties:** New values should use the existing CSS variables defined in `:root` — avoid magic numbers.
- **Responsive:** Any new UI components must work at 360 px wide and up.
- **No inline styles:** All styling belongs in `styles.css`.

---

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <short description>

[optional body]
[optional footer]
```

| Type | When to use |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, whitespace — no logic change |
| `refactor` | Code restructure without behavior change |
| `perf` | Performance improvement |
| `test` | Adding or fixing tests |
| `chore` | Build, CI, dependency updates |

**Examples:**

```
feat(backend): add 5-day forecast endpoint
fix(cache): prevent race condition on concurrent cache writes
docs: expand API reference with cURL examples
chore(deps): bump flask from 3.0.0 to 3.1.0
```

---

## Pull Request Checklist

Before requesting a review, confirm that all items are complete:

- [ ] Branch is up to date with `main` (`git fetch upstream && git rebase upstream/main`)
- [ ] Code follows the style guidelines above
- [ ] New functions have docstrings / JSDoc comments
- [ ] No secrets, API keys, or `.env` files are committed
- [ ] `FLASK_DEBUG=false` is not accidentally enabled for production paths
- [ ] Any new environment variables are documented in `README.md` and `backend/.env.example`
- [ ] The app runs locally without errors (`python app.py`)
- [ ] Accessibility: new UI elements have ARIA labels and work with keyboard navigation
- [ ] PR description explains **what** changed and **why**

---

## Reporting Bugs

Open a [GitHub Issue](https://github.com/ibnehussain/cognizantweatherapp/issues) and include:

1. **Description** — what you expected vs. what happened.
2. **Steps to reproduce** — a minimal set of steps.
3. **Environment** — OS, Python version, browser (if frontend).
4. **Logs / screenshots** — attach any relevant console output or error messages.

---

## Requesting Features

Open a [GitHub Issue](https://github.com/ibnehussain/cognizantweatherapp/issues) with:

1. **Use case** — describe the problem the feature would solve.
2. **Proposed solution** — your suggested approach (optional).
3. **Alternatives** — any alternatives you considered.

Feature requests are welcome, but please check open issues first to avoid duplicates.
