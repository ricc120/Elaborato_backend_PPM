# Elaborato Back-end PPM 2026: Weather Forecast API

**Author:** Riccardo Chiti  
**Live Deployment:** https://ricc120.pythonanywhere.com/  
**Repository:** https://github.com/ricc120/Elaborato_backend_PPM/  
**Project Type:** REST API (Track 3: **Weather Forecast API**)  
**Framework:** Django & Django REST Framework


## Project Overview
This project is a fully functional REST API built with Django and Django REST Framework (DRF), designed to provide weather forecasts with a role-based access control system. The architecture includes custom user roles (Basic, Premium, Editor), JWT authentication, rate limiting, and an automated tracking system for user search history. CORS is fully configured to allow external frontend integrations.

## Demo Accounts
The SQLite database (`db.sqlite3`) is pre-populated with weather data and demo users. Please use the following credentials to test the different permission levels:

| Role | Username | Password | Capabilities |
| :--- | :--- | :--- | :--- |
| **Admin** | `userAdmin` | `adm1n0password` | Django Superuser (Access to `/admin/` panel). |
| **Editor** | `userEditor` | `us3r3password` | Full CRUD on weather data (`/api/manage/`). |
| **Premium** | `userPremium` | `us3r2password` | Unlimited weather queries, save favourite cities, access search history and stats. |
| **Basic** | `userBasic` | `us3r1password` | Read-only weather queries (Rate-limited to 5 per day). |

---

## API Endpoints Summary

*Note: As this is a pure REST API, the root URL (`/`) will return a standard `404 Not Found`. All interactions must be routed through the `/api/...` endpoints listed below.*

* `POST /api/token/` - Obtain JWT Access and Refresh tokens.
* `GET /api/weather/` - Retrieve weather forecast (filters: `location`, `date`, `time`).
* `GET/POST/PUT/DELETE /api/history/` - CRUD for personal search history (Premium only).
* `GET/POST/PUT/DELETE /api/favourites/` - Manage favourite cities (Premium only).
* `GET /api/history/stats/` - Aggregated user search statistics (Premium only).
* `GET/POST/PUT/DELETE /api/manage/` - Database management for weather data (Editor only).

### Detailed Endpoints Reference Table

| HTTP Method | URL Path | Auth Required | Allowed Roles | Request Body (JSON) | Response Example (JSON) | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **POST** | `/api/token/` | No | Anonymous / All | `{"username": "...", "password": "..."}` | `{"access": "eyJ...", "refresh": "eyJ..."}` | Obtain JWT Access and Refresh tokens upon login. |
| **POST** | `/api/token/refresh/` | No | Anonymous / All | `{"refresh": "<TOKEN>"}` | `{"access": "eyJ..."}` | Renew an expired Access Token using a valid Refresh Token. |
| **GET** | `/api/weather/` | No (Optional) | Anonymous / All | None (Query params: `location`, `date`, `time`) | `[{"location": "City Name", "temperature": 25.0, ...}]` | Retrieve weather data. Anon/Regular users are rate-limited. Premium benefits from smart fallback if location is omitted. |
| **GET** | `/api/history/` | Yes | Premium | None | `[{"id": ID, "location": "City Name", "timestamp": ...}]` | List the authenticated Premium user's unique search history. |
| **POST** | `/api/history/` | Yes | Premium | `{"location": "City Name"}` | `{"id": ID, "location": "City Name", "timestamp": ...}` | Manually save a location search to the user's history. |
| **PATCH** | `/api/history/<ID>/` | Yes | Premium | `{"location": "New City Name"}` | `{"id": ID, "location": "New City Name", "timestamp": "..."}` | Partially update a specific search history entry. |
| **DELETE** | `/api/history/<ID>/` | Yes | Premium | None | `204 No Content` | Delete a specific search entry from the personal history. |
| **GET** | `/api/favourites/` | Yes | Premium | None | `[{"id": ID, "is_primary": false, "name": "City Name"}]` | Retrieve the list of favorite cities for the authenticated user. |
| **POST** | `/api/favourites/` | Yes | Premium | `{"name": "City Name", "is_primary": true}` | `{"id": ID, "is_primary": true, "name": "City Name"}` | Add a new favorite city and optionally set it as the primary fallback. |
| **PATCH** | `/api/favourites/<ID>/` | Yes | Premium | `{"is_primary": true}` | `{"id": ID, "is_primary": true, "name": "City Name"}` | Update favorite city attributes (e.g., switching the primary fallback status to resolve conflicts). |
| **DELETE** | `/api/favourites/<ID>/` | Yes | Premium | None | `204 No Content` | Remove a city from the personal favorites list. |
| **GET** | `/api/history/stats/` | Yes | Premium | None | `{"last_active": "...", "most_searched_city": "City Name", ...}` | Retrieve aggregated search metrics (total queries, top searched city) via Django ORM. |
| **GET** | `/api/manage/` | Yes | Editor | None | `[{"id": ID, "location": "City Name", ...}]` | Read-only access to inspect the global weather forecasts catalog. |
| **POST** | `/api/manage/` | Yes | Editor | `{"location": "City Name", "date": "date", "time": "time", "temperature": 25.0, ...}` | `{"id": ID, "location": "City Name", "temperature": 25.0, ...}` | Create a new weather forecast record in the database. |
| **PUT** | `/api/manage/<ID>/` | Yes | Editor | `{"location": "New City Name", "date": "New date", "time": "New time", "temperature": 30.0, ...}` | `{"id": ID, "location": "New City Name", ...}` | Completely overwrite an existing weather forecast record. |
| **PATCH** | `/api/manage/<ID>/` | Yes | Editor | `{"temperature": 35.0}` | `{"id": ID, "location": "City Name", "temperature": 35.0, ...}` | Partially update fields (e.g., modify only temperature) of a record. |
| **DELETE** | `/api/manage/<ID>/` | Yes | Editor | None | `204 No Content` | Permanently delete a weather forecast record from the database. |

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

   # Activate on macOS/Linux:
   source venv/bin/activate

   # Activate on Windows:
   venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the server:**
   ```bash
   python manage.py runserver
   ```
   *Note: The db.sqlite3 database is already populated, so no migrations are needed.*


---
## HTTPie Client Setup
To reproduce the tests, you can use the HTTPie command-line client.
* **Installation:** https://httpie.io/docs/cli/installation
* **Base URL:** `https://ricc120.pythonanywhere.com`

## HTTPie Testing Scenarios
*Note: replace `<TOKEN>` with the actual long string received from the login endpoints.*

### Scenario 1: Authentication & Public Access
**1.1 Get Tokens (Login as Basic User)**
```bash
http POST https://ricc120.pythonanywhere.com/api/token/ username=userBasic password=us3r1password
```
**1.2 Public Weather Query (Rate Limited)**

*If you run without a token you will be considered with your IP.*
```bash
http GET https://ricc120.pythonanywhere.com/api/weather/ location==Rome "Authorization: Bearer <TOKEN>"
```
*There are also advanced filter with Date and Time.*
```bash
http GET https://ricc120.pythonanywhere.com/api/weather/ location==Rome date==2026-06-05 time==12:00 "Authorization: Bearer <TOKEN>"
```
*If you run this 6 times without a token (or with a basic user token), you will receive a `429 Too Many Requests` status, returning a custom exception message.*
```
{
    "error": "Request limit reached, upgrade to premium"
}
```
**1.3 Verify Input Validation Handling**

*Pass an invalid date time format to verify the backend input sanitization and customized JSON error structure. Expected `400 Bad Request`.*
```bash
http GET https://ricc120.pythonanywhere.com/api/weather/ location==Rome date==05-06-2026 "Authorization: Bearer <TOKEN>"
```
```
{
    "error": "Invalid data format. Use: YYYY-MM-DD"
}
```
```bash
http GET https://ricc120.pythonanywhere.com/api/weather/ location==Rome time==12PM "Authorization: Bearer <TOKEN>"
```
```
{
    "error": "Invalid time format. Use: HH:MM"
}
```
```bash
http GET https://ricc120.pythonanywhere.com/api/weather/ location==Atlantis date==2026-06-01 "Authorization: Bearer <TOKEN>"
```
```
{
    "error": "No forecast found for this location or date-time"
}
```

### Scenario 2: The Premium Experience (History & Stats)
**2.1 Login as Premium User**
```bash
http POST https://ricc120.pythonanywhere.com/api/token/ username=userPremium password=us3r2password
```
**2.2 Set a Favourite City**
```bash
http POST https://ricc120.pythonanywhere.com/api/favourites/ name="Milan" is_primary=true "Authorization: Bearer <TOKEN>"
```
*Note: If you attempt a POST request for a new favorite city when another destination is already flagged as `is_primary=true`, the unique validation constraint will trigger an error. To safely switch your primary context preference, locate the resource <ID> and perform a partial update instead:*
```bash
http PATCH https://ricc120.pythonanywhere.com/api/favourites/<ID>/ is_primary=true "Authorization: Bearer <TOKEN>"
```
**2.3 Smart Fallback Weather Query**

*Query the weather without providing a location. The API will automatically read the user's primary favourite city (Milan) and return its weather.*
```bash
http GET https://ricc120.pythonanywhere.com/api/weather/ "Authorization: Bearer <TOKEN>"
```
*Note: If you don't set `is_primary` parameter, the system will consider the first favourite city saved as primary.*

**2.4 Fetch Personal Search History Catalog**
```bash
http GET https://ricc120.pythonanywhere.com/api/history/ "Authorization: Bearer <TOKEN>"
```
**2.5 Check Aggregated Statistics**

*Uses Django ORM aggregation to return the most searched city and total queries.*
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

```bash
http GET https://ricc120.pythonanywhere.com/api/manage/ 
```
**3.4 Update the Forecast (PATCH)**

*The ID of the newly created forecast is in the response body of the request above.*
```bash
http PATCH https://ricc120.pythonanywhere.com/api/manage/<ID>/ temperature=35 "Authorization: Bearer <TOKEN>"
```
**3.5 Delete the Forecast (DELETE)**

*Returns `204 No Content` on success.*
```bash
http DELETE https://ricc120.pythonanywhere.com/api/manage/<ID>/ "Authorization: Bearer <TOKEN>"
```

### Scenario 4: Permission Validation (Forbidden Actions)
**4.1 Basic User attempting Editor Actions (Expect 403 Forbidden)**

*Attempt to insert data into the database using the Basic User token.*
```bash
http POST https://ricc120.pythonanywhere.com/api/manage/ location="Paris" date="2026-11-11" time="10:00" temperature=15 humidity=50 condition="Cloudy" "Authorization: Bearer <TOKEN>"
```
*Result: The server strictly enforces roles and rejects the request with a `403 Forbidden` error.*

**4.2 Premium User attempting Editor Actions (Expect 403 Forbidden)**

*Attempt to insert data into the database using the Premium User token.*
```bash
http POST https://ricc120.pythonanywhere.com/api/manage/ location="Paris" date="2026-11-11" time="10:00" temperature=15 humidity=50 condition="Cloudy" "Authorization: Bearer <TOKEN>"
```
*Result: The server strictly enforces roles and rejects the request with a `403 Forbidden` error.*

### Scenario 5: Administrative Django Interface Inspection
**5.1 Admin Console Access Verification**

*To evaluate database internal states, relations, and background trackers via browser interface, access the built-in administration command center:*

**URL:** https://ricc120.pythonanywhere.com/admin/

**Credentials:** Username: `userAdmin` | Password: `adm1n0password`

*Note: In the active production cloud environment (DEBUG=False), static file automated rendering is disabled for security compliance. The administrative interface will correctly process all login permissions and display data models utilizing default structured unstyled semantic HTML.*
