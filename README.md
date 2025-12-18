# GFormFiller API

**GFormFiller** is an intelligent automation solution for Google Forms. Built with **FastAPI** and **Selenium**, it enables the management of persistent browsing profiles, automates the completion of complex forms via JSON configurations or AI, and tracks execution in real-time through a REST API.


## WORK IN PROGESS

This repository contains work-in-progress code and is not production-ready.
Use at your own risk, and expect frequent change.

---

## Key Features

- **Profile Management**: Creation and persistence of Google sessions (eliminates the need to log in every time).

- **Background Mode**: Asynchronous execution of form submissions to prevent timeouts.

- **Path Resolution**: Intelligent file upload management (automatic absolute path generation).

- **Locking System**: Profile protection using .lock files to prevent Selenium instance conflicts.

- **Advanced Logging**: Dual-layer log storage (Rotating files + SQLite database).

- **Interactive Documentation**: Integrated Swagger UI for real-time API testing and exploration.

---

## Installation

### Prerequisites

- Python **3.12+**
- [Poetry](https://python-poetry.org/)

```bash
git clone https://github.com/EnamSon/gformfiller.git
cd gformfiller
poetry install
```

---

## Run the server

The server runs at http://127.0.0.1:8000 by default

```bash
poetry run gformfiller
```

You can specify another host IP or another port with optional arguments `--host` or `--port`.

---

## Directory Structure

The application self-organizes within the $HOME/.gformfiller directory:

    - /chrome-testing: Contains the Chrome for Testing binary.

    - /chromedriver: Contains the Chromedriver binary.

    - /profiles: Chrome user data (one folder per profile).

    - /fillers:

        - /{name}/formdata.json: Data to be injected.

        - /{name}/config.json: Specific settings (AI, delays).

        - /{name}/metadata.json: Form URL and execution status.

        - /{name}/files/: Storage for files to be uploaded.

        - /{name}/record/:

            - /pdfs: Form printed as PDF (before and after submission).

            - /screenshots: Screenshots for debugging purposes.

    - log.db: SQLite database for system logs.

---

## QUICK START

### Step 1: Create profile

Call the API to create a profile. A Chrome window will open, allowing you to log in to your Google account.

```bash
curl -X POST "http://localhost:8000/gformfiller/profiles/?profile_name=MyProfile/"
```
### Step 2: Initialize a Filler

```bash
curl -X POST "http://localhost:8000/gformfiller/fillers/MyForm/"
```
### Step 3: Update filler configuration

```bash
curl -X PUT "http://localhost:8000/gformfiller/fillers/MyForm/config/" \
    -H "Content-Type: application/json" \
    -d '{
        "profile": "MyProfile",
        "headless": false,
        "remote": false,
        "wait_time": 5.0,
        "submit": true
    }'
```

### Step 4: Dans un contexte de développement (interface utilisateur ou documentation), voici les traductions les plus adaptées :
1. La version standard (Interface/Web)

    Save files to upload (Optional)

```bash
curl -X POST "http://localhost:8000/gformfiller/fillers/MyForm/files/" \
    -F "files=@/path/to/your/photo.jpeg" \
    -F "files=@/path/to/your/document.pdf"
```

### Step 5: Update the information to be filled in the form

```bash
curl -X PUT "http://localhost:8000/gformfiller/fillers/MyForm/formdata/" \
    -H "Content-Type: application/json" \
    -d  '{
        "TextResponse": {
            "nom": "your name",
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
            "document": "photo.jpeg",
            "photo": "cni.pdf"
        }
}'
```

### Step 6: Update URL in metadata.json

```bash
curl -X PUT "http://localhost:8000/gformfiller/fillers/MyForm/metadata/" \
    -H "Content-Type: application/json" \
    -d '{
        "url": "https://docs.google.com/forms/d/e/1FAIpQLSeE1LZOwq15GKZTyR99zt8lydqtnaDIMFYwNHcmPFCgtUbMNQ/viewform"
    }'
```

### Step 7: Run

```bash
curl -X POST "http://localhost:8000/gformfiller/fillers/MyForm/run/"
```

### Step 8: Check status (Optional)

```bash
curl -X POST "http://localhost:8000/gformfiller/fillers/MyForm/status"
```
ou

```bash
curl -X POST "http://localhost:8000/gformfiller/fillers/MyForm/metadata/"
```
