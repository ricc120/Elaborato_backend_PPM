# Elaborato Back-end PPM 2026: Weather Forecast API

**Author:** Riccardo Chiti  
**Live Deployment:** https://ricc120.pythonanywhere.com/  
**Repository:** https://github.com/ricc120/Elaborato_backend_PPM/

## Project Overview
This project is a fully functional REST API built with Django and Django REST Framework (DRF), designed to provide weather forecasts with a role-based access control system. The architecture includes custom user roles (Basic, Premium, Editor), JWT authentication, rate limiting, and an automated tracking system for user search history. CORS is fully configured to allow external frontend integrations.

## Demo Accounts
The SQLite database (`db.sqlite3`) is pre-populated with weather data and demo users. Please use the following credentials to test the different permission levels:

| Role | Username | Password | Capabilities |
| :--- | :--- | :--- | :--- |
| **Editor** | `userEditor` | `us3r3password` | Full CRUD on weather data (`/api/manage/`). |
| **Premium** | `userPremium` | `us3r2password` | Unlimited weather queries, save favorite cities, access search history and stats. |
| **Basic** | `userBasic` | `us3r1password` | Read-only weather queries (Rate-limited to 5 per day). |

---

## API Endpoints Summary

* `POST /api/token/` - Obtain JWT Access and Refresh tokens.
* `GET /api/weather/` - Retrieve weather forecast (filters: `location`, `date`, `time`).
* `GET/POST/PUT/DELETE /api/history/` - CRUD for personal search history (Premium only).
* `GET/POST/PUT/DELETE /api/favorites/` - Manage favorite cities (Premium only).
* `GET /api/history/stats/` - Aggregated user search statistics (Premium only).
* `GET/POST/PUT/DELETE /api/manage/` - Database management for weather data (Editor only).

---

## Local Installation Instructions
To run this project locally on your machine, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ricc120/Elaborato_backend_PPM.git
   cd Elaborato_backend_PPM
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate 
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the server:**
   ```bash
   python manage.py runserver
   ```

---

## HTTPie Testing Scenarios
*Note: replace `<TOKEN>` with the actual long string received from the login endpoints.*

### Scenario 1: Authentication & Public Access
**1.1 Get Tokens (Login as Basic User)**
```bash
http POST https://ricc120.pythonanywhere.com/api/token/ username=userBasic password=us3r1password
```
**1.2 Public Weather Query (Rate Limited)**
```bash
http GET https://ricc120.pythonanywhere.com/api/weather/ location==Rome
```
*There are also advanced filter with Date and Time.*
```bash
http GET https://ricc120.pythonanywhere.com/api/weather/ location==Rome date==2026-06-01 time==12:00
```
*If you run this 6 times without a token (or with a basic user token), you will receive a `429 Too Many Requests` status, returning a custom exception message.*
```
{
    "error": "Request limit reached, upgrade to premium"
}
```
** 1.3 Verify Input Validation Handling
*Pass an invalid date format to verify the backend input sanitization and customized JSON error structure. Expected `400 Bad Request`.*
```bash
http GET https://ricc120.pythonanywhere.com/api/weather/ location==Rome date==01-06-2026
```

### Scenario 2: The Premium Experience (History & Stats)
**2.1 Login as Premium User**
```bash
http POST https://ricc120.pythonanywhere.com/api/token/ username=userPremium password=us3r2password
```
**2.2 Set a Favorite City**
```bash
http POST https://ricc120.pythonanywhere.com/api/favorites/ name="Milan" is_primary=true "Authorization: Bearer <TOKEN>"
```
**2.3 Smart Fallback Weather Query**
Query the weather without providing a location. The API will automatically read the user's primary favorite city (Milan) and return its weather.
```bash
http GET https://ricc120.pythonanywhere.com/api/weather/ "Authorization: Bearer <TOKEN>"
```
**2.4 Fetch Personal Search History Catalog**
```bash
http GET https://ricc120.pythonanywhere.com/api/history/ "Authorization: Bearer <TOKEN>"
```
**2.5 Check Aggregated Statistics**
Uses Django ORM aggregation to return the most searched city and total queries.
```bash
http GET https://ricc120.pythonanywhere.com/api/history/stats/ "Authorization: Bearer <TOKEN>"
```

### Scenario 3: Data Management (Editor CRUD)
**3.1 Login as Editor**
```bash
http POST https://ricc120.pythonanywhere.com/api/token/ username=userEditor password=us3r3password
```
**3.2 Create a New Forecast (POST)**
```bash
http POST https://ricc120.pythonanywhere.com/api/manage/ location="Atlantis" date="2026-10-10" time="12:00:00" temperature=30 humidity=80 condition="Sunny" "Authorization: Bearer <TOKEN>"
```
**3.3 Read the newly created forecast to get its ID (GET)**
Note: It is a public resource that returns all the forecasts in the database
```bash
http GET https://ricc120.pythonanywhere.com/api/manage/ 
```
**3.4 Update the Forecast (PATCH)**
The ID of the newly created forecast is in the response body of the request above.
```bash
http PATCH https://ricc120.pythonanywhere.com/api/manage/<ID> temperature=35 "Authorization: Bearer <TOKEN>"
```
**3.5 Delete the Forecast (DELETE)**
Returns `204 No Content` on success.
```bash
http DELETE https://ricc120.pythonanywhere.com/api/manage/<ID> "Authorization: Bearer <TOKEN>"
```

### Scenario 4: Permission Validation (Forbidden Actions)
**4.1 Basic User attempting Editor Actions (Expect 403 Forbidden)**
Attempt to insert data into the database using the Basic User token.
```bash
http POST https://ricc120.pythonanywhere.com/api/manage/ location="Paris" date="2026-11-11" time="10:00" temperature=15 humidity=50 condition=Cloudy "Authorization: Bearer <TOKEN>"
```
Result: The server strictly enforces roles and rejects the request with a `403 Forbidden` error.
**4.2 Premium User attempting Editor Actions (Expect 403 Forbidden)**
Attempt to insert data into the database using the Premium User token.
```bash
http POST https://ricc120.pythonanywhere.com/api/manage/ location="Paris" date="2026-11-11" time="10:00" temperature=15 humidity=50 condition=Cloudy "Authorization: Bearer <TOKEN>"
```
Result: The server strictly enforces roles and rejects the request with a `403 Forbidden` error.

