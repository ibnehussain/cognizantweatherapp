/* ═══════════════════════════════════════════════════════════════
   Weather Dashboard — app.js
   Handles: search, API calls, DOM updates, unit toggle, history
   ═══════════════════════════════════════════════════════════════ */

'use strict';

/* ─── Config ────────────────────────────────────────────────── */
const API_BASE        = '/api/weather';
const MAX_HISTORY     = 5;
const HISTORY_KEY     = 'weatherDash_history';

/* ─── DOM References ────────────────────────────────────────── */
const searchForm      = document.getElementById('search-form');
const cityInput       = document.getElementById('city-input');
const inputError      = document.getElementById('input-error');
const loader          = document.getElementById('loader');
const errorBanner     = document.getElementById('error-banner');
const errorMessage    = document.getElementById('error-message');
const weatherCard     = document.getElementById('weather-card');
const historySection  = document.getElementById('history-section');
const historyList     = document.getElementById('history-list');
const clearHistoryBtn = document.getElementById('clear-history-btn');
const btnCelsius      = document.getElementById('btn-celsius');
const btnFahrenheit   = document.getElementById('btn-fahrenheit');

/* ─── State ─────────────────────────────────────────────────── */
let currentUnit = 'C';          // 'C' | 'F'
let lastWeatherData = null;     // cache latest response for unit toggling

/* ══════════════════════════════════════════════════════════════
   1. FETCH WEATHER
   ══════════════════════════════════════════════════════════════ */

/**
 * Fetches weather data from the Flask backend for a given city.
 * @param {string} city
 * @returns {Promise<object>} parsed JSON weather object
 */
async function fetchWeather(city) {
  const url = `${API_BASE}?city=${encodeURIComponent(city.trim())}`;
  const response = await fetch(url);

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const msg = body.error || getHttpErrorMessage(response.status);
    throw new Error(msg);
  }

  return response.json();
}

/**
 * Returns a human-readable message for known HTTP error codes.
 * @param {number} status
 * @returns {string}
 */
function getHttpErrorMessage(status) {
  const messages = {
    400: 'Invalid city name. Please check your input.',
    404: 'City not found. Try a different name.',
    429: 'Too many requests. Please wait a moment.',
    500: 'Server error. Please try again later.',
    503: 'Weather service unavailable. Please try again later.',
  };
  return messages[status] || `Unexpected error (${status}). Please try again.`;
}

/* ══════════════════════════════════════════════════════════════
   2. DOM UPDATES
   ══════════════════════════════════════════════════════════════ */

/**
 * Renders all weather data onto the weather card.
 * @param {object} data  — the JSON returned by the Flask API
 */
function renderWeather(data) {
  /* City & country */
  document.getElementById('city-name').textContent    = data.city;
  document.getElementById('city-country').textContent = data.country;
  document.getElementById('weather-date').textContent = formatDate(new Date());

  /* Icon */
  const icon = document.getElementById('weather-icon');
  icon.src = `https://openweathermap.org/img/wn/${data.icon}@2x.png`;
  icon.alt = data.condition;

  /* Condition */
  document.getElementById('weather-condition').textContent = data.condition;

  /* Temperature (respects current unit) */
  updateTemperatureDisplay(data.temp_c);

  /* Stats */
  document.getElementById('humidity').textContent  = `${data.humidity}%`;
  document.getElementById('wind-speed').textContent = `${data.wind_speed} km/h`;

  const feelsC = data.feels_like_c;
  document.getElementById('feels-like').textContent =
    currentUnit === 'C'
      ? `${Math.round(feelsC)}°C`
      : `${toFahrenheit(feelsC)}°F`;

  /* Show card */
  weatherCard.hidden = false;
  weatherCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/**
 * Updates just the temperature and feels-like values when unit toggles.
 * @param {number} tempC  — temperature in Celsius
 */
function updateTemperatureDisplay(tempC) {
  const tempEl   = document.getElementById('temperature');
  const unitEl   = document.getElementById('unit-label');
  const feelsEl  = document.getElementById('feels-like');

  if (currentUnit === 'C') {
    tempEl.textContent  = Math.round(tempC);
    unitEl.textContent  = '°C';
  } else {
    tempEl.textContent  = toFahrenheit(tempC);
    unitEl.textContent  = '°F';
  }

  if (lastWeatherData) {
    feelsEl.textContent = currentUnit === 'C'
      ? `${Math.round(lastWeatherData.feels_like_c)}°C`
      : `${toFahrenheit(lastWeatherData.feels_like_c)}°F`;
  }
}

/* ──── UI state helpers ─────────────────────────────────────── */

function showLoader() {
  loader.hidden        = false;
  errorBanner.hidden   = true;
  weatherCard.hidden   = true;
  inputError.hidden    = true;
}

function hideLoader() {
  loader.hidden = true;
}

function showError(msg) {
  errorMessage.textContent = msg;
  errorBanner.hidden       = false;
  weatherCard.hidden       = true;
}

function showInputError(msg) {
  inputError.textContent = msg;
  inputError.hidden      = false;
  cityInput.setAttribute('aria-invalid', 'true');
}

function clearInputError() {
  inputError.hidden = true;
  inputError.textContent = '';
  cityInput.removeAttribute('aria-invalid');
}

/* ══════════════════════════════════════════════════════════════
   3. FORM SUBMISSION & MAIN FLOW
   ══════════════════════════════════════════════════════════════ */

searchForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  clearInputError();

  const city = cityInput.value.trim();

  /* Client-side validation */
  if (!city) {
    showInputError('Please enter a city name.');
    cityInput.focus();
    return;
  }

  if (!/^[a-zA-Z\u00C0-\u024F\s\-'.]+$/.test(city)) {
    showInputError('City name contains invalid characters.');
    cityInput.focus();
    return;
  }

  showLoader();

  try {
    const data = await fetchWeather(city);
    lastWeatherData = data;
    hideLoader();
    errorBanner.hidden = true;
    renderWeather(data);
    addToHistory(data.city);
  } catch (err) {
    hideLoader();
    showError(err.message);
  }
});

/* ══════════════════════════════════════════════════════════════
   4. UNIT TOGGLE (°C / °F)
   ══════════════════════════════════════════════════════════════ */

btnCelsius.addEventListener('click', () => setUnit('C'));
btnFahrenheit.addEventListener('click', () => setUnit('F'));

/**
 * Switches the active temperature unit and refreshes the display.
 * @param {'C'|'F'} unit
 */
function setUnit(unit) {
  if (currentUnit === unit) return;
  currentUnit = unit;

  btnCelsius.classList.toggle('active', unit === 'C');
  btnCelsius.setAttribute('aria-pressed', String(unit === 'C'));
  btnFahrenheit.classList.toggle('active', unit === 'F');
  btnFahrenheit.setAttribute('aria-pressed', String(unit === 'F'));

  if (lastWeatherData) {
    updateTemperatureDisplay(lastWeatherData.temp_c);
  }
}

/* ══════════════════════════════════════════════════════════════
   5. SEARCH HISTORY
   ══════════════════════════════════════════════════════════════ */

/**
 * Adds a city to the top of the history list (deduped, max 5).
 * Persists to localStorage.
 * @param {string} city
 */
function addToHistory(city) {
  let history = loadHistory();
  history = [city, ...history.filter(c => c.toLowerCase() !== city.toLowerCase())];
  history = history.slice(0, MAX_HISTORY);
  saveHistory(history);
  renderHistory(history);
}

function loadHistory() {
  try {
    return JSON.parse(localStorage.getItem(HISTORY_KEY)) || [];
  } catch {
    return [];
  }
}

function saveHistory(history) {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
}

/**
 * Renders search history chips into the history list.
 * @param {string[]} history
 */
function renderHistory(history) {
  historyList.innerHTML = '';

  if (!history.length) {
    historySection.hidden = true;
    return;
  }

  history.forEach(city => {
    const li = document.createElement('li');
    li.className = 'history-item';
    li.setAttribute('role', 'listitem');
    li.innerHTML = `<i class="fa-solid fa-clock-rotate-left" aria-hidden="true"></i>${city}`;
    li.addEventListener('click', () => searchCity(city));
    historyList.appendChild(li);
  });

  historySection.hidden = false;
}

clearHistoryBtn.addEventListener('click', () => {
  localStorage.removeItem(HISTORY_KEY);
  renderHistory([]);
});

/**
 * Programmatically searches for a city (used by history chips).
 * @param {string} city
 */
async function searchCity(city) {
  cityInput.value = city;
  clearInputError();
  showLoader();

  try {
    const data = await fetchWeather(city);
    lastWeatherData = data;
    hideLoader();
    errorBanner.hidden = true;
    renderWeather(data);
    addToHistory(data.city);
  } catch (err) {
    hideLoader();
    showError(err.message);
  }
}

/* ══════════════════════════════════════════════════════════════
   6. UTILITIES
   ══════════════════════════════════════════════════════════════ */

/**
 * Converts Celsius to Fahrenheit.
 * @param {number} c
 * @returns {number}
 */
function toFahrenheit(c) {
  return Math.round((c * 9) / 5 + 32);
}

/**
 * Formats a Date object to a readable string, e.g. "Mon, 2 Mar 2026"
 * @param {Date} date
 * @returns {string}
 */
function formatDate(date) {
  return date.toLocaleDateString('en-GB', {
    weekday: 'short',
    day:     'numeric',
    month:   'short',
    year:    'numeric',
  });
}

/* ══════════════════════════════════════════════════════════════
   7. INIT
   ══════════════════════════════════════════════════════════════ */

(function init() {
  /* Restore history on page load */
  renderHistory(loadHistory());

  /* Auto-focus search input */
  cityInput.focus();
})();
