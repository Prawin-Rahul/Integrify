# Integrify Application

This project is a multi-service application that integrates with Airtable, HubSpot, and Redis to perform various tasks. It is containerized using Docker and includes separate services for the backend, frontend, and Redis database.

---

## Features

1. **Backend Service**:

   - REST API built using FastAPI.
   - Integrations with Airtable and HubSpot.

2. **Frontend Service**:

   - React-based user interface.

3. **Redis**:
   - Caching layer to store temporary data.

---

## Prerequisites

Before running the application, ensure you have the following installed:

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

---

## Getting Started

### 1. Clone the Repository

```bash
git clone <git@github.com:Prawin-Rahul/Integrify.git>
cd Integrify
```

### 2. Set Up the Backend .env File

**AIRTABLE API KEYS**

```
AIRTABLE_API_KEY= *****
AIRTABLE_CLIENT_SECRET= *****
AIRTABLE_CLIENT_ID= *****
```

**HUBSPOT API KEYS**

```
HUBSPOT_CLIENT_ID= *****
HUBSPOT_CLIENT_SECRET= *****
```

**REDIS KEYS**

```
REDIS_HOST=redis
```

### 3. Build and Run the Containers

```bash
docker-compose up --build
```

### 4. If You Encounter react-scripts: not found Issue

while running the frontend container , If you Encounter

```
sh: react-scripts: not found
```

Navigate to the frontend directory:

```bash
npm install react-scripts
```

Again bring up the container

### 5. Access the Application

- [Frontend]: Access the API at (http://localhost:3000 ) .
- [Backend]: Access the API at (http://localhost:8000).

### 6. Stopping the Application

```bash
docker-compose down
```

### NOTES

- Feel free to reachout to prawinrahul1411@gmail.com
- Also modify the .env file to use your actual Airtable and HubSpot API credentials.
