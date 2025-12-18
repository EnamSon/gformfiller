# GFormFiller API Documentation

**Version:** 1.0.0  
**Base URL:** `http://localhost:8000/gformfiller`  
**Interactive UI (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Overview
GFormFiller is a REST API designed to automate Google Forms filling using Selenium and AI. It manages browser profiles (with Google Authentication), handles form data configurations, and executes background automation tasks.

---

## Browser Profiles Management
These endpoints handle Chrome user data directories to maintain persistent login sessions.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/profiles/` | List all available browser profiles. |
| **POST** | `/profiles/` | Create a new profile & trigger `AuthWorker` (Opens Chrome for login). |
| **DELETE** | `/profiles/{name}/` | Permanently delete a profile and its session data. |

**Query Parameters for POST:**
- `profile_name` (string): Unique name for the new profile.

---

## Fillers Management
Manage the logic, data, and files for specific automation targets.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/fillers/` | List all available fillers. |
| **POST** | `/fillers/{name}/` | Initialize a new filler with default structure. |
| **GET** | `/fillers/{name}/{file_key}/` | Get content of `config`, `formdata`, or `metadata`. |
| **PUT** | `/fillers/{name}/{file_key}/` | Update content of `config`, `formdata`, or `metadata`. |
| **POST** | `/fillers/{name}/files/` | Upload binary files (PDF, Images) to the filler's storage. |
| **DELETE** | `/fillers/{name}/` | Delete a filler and all associated records. |

---

## ⚡ Execution Engine (The Runner)
Trigger the automated form-filling process.

### `POST /fillers/{name}/run/`
Starts the automation as a **Background Task**.

**Request Body (Optional):**

```json
{
    "TextResponse": {
        "name": "your name",
        "surname": "your surname"
    },

    "DateResponse": {
        "birthdate": "1995-10-01"
    },

    "TimeResponse": {
        "time": "10:00"
    },

    "CheckboxResponse": {
        "exams": "exam1 | exam2 | exame3 | exam3"
    },

    "RadioResponse": {
        "gender": "female"
    },

    "ListboxResponse": {
        "country": "cameroun"
    },

    "FileUploadResponse": {
        "document": "filename"
    }
}
```

If provided, this JSON overrides the local formdata.json for this specific execution.

Response: *202 Accepted*

GET /fillers/{name}/status

Check the progress of the automation.

   - Possible values: idle, running, completed, failed, error.

---

## System & Monitoring

Global configuration and audit logs.

**GET | PUT** */gformfiller/default/*

Access or update the global configuration template (default.json). Settings here (like use_ai, model_name, headless) serve as defaults for all new fillers.

**GET** */gformfiller/log/*

Fetch the audit trail from the SQLite database.

   - Query Parameter: limit (default: 100).

   - Output: Array of logs containing timestamp, level, message, and category.

---

## Error Handling & Locks

    - Profile Locking: A .lock file is created in the profile directory during execution. Any attempt to use a locked profile will return a 409 Conflict.

    - Background Cleanup: If an execution fails, the worker attempts to release the profile lock and update the status to error.

    - Validation: Missing URLs in metadata or invalid JSON structures will return 400 Bad Request.