# 🚀 CloudOps Backend Integration Guide

Welcome to the CloudOps senior DevOps/SRE control backend. This pipeline programmatically scans multi-cloud assets, audits DevSecOps firewall vulnerabilities and storage compliance risks, and executes autonomic therapeutic healing.

This backend is built on **Python FastAPI** and **PostgreSQL** to serve the Jetpack Compose Android application in real-time.

---

## 🛠️ Prerequisites

To run this backend locally, ensure you have:
1. **Python 3.8+** installed.
2. **PostgreSQL** database active and listening (e.g., via Local Service, PostgresApp, or Docker).
3. **AWS Account credentials** with read permissions (VPC, Security Groups, S3, RDS, Lambda) if executing live audits.

---

## 💾 1. Database Setup

Ensure PostgreSQL is running on your system. You can spin up a quick, clean PostgreSQL container in Docker using:

```bash
docker run --name cloudops-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=your_secure_password \
  -e POSTGRES_DB=cloudops_db \
  -p 5432:5432 -d postgres
```

If you are using PostgreSQL installed natively via Homebrew or Windows installers, simply create a database named `cloudops_db`:

```sql
CREATE DATABASE cloudops_db;
```

---

## 🔑 2. Environment Configuration

Create a file named `.env` inside the `backend/` directory of your workspace. Populate it with your local database connection URLs and your AWS target programmatic keys:

```ini
# --- PostgreSQL Credentials Configuration ---
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=cloudops_db

# --- AWS SDK (Boto3) Security Credentials ---
# (Securely configure programmatic Access Keys with Read Permissions)
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_DEFAULT_REGION=us-east-1
```

*Note: If AWS keys are omitted or invalid, the backend gracefully falls back to generating rich simulation datasets so the UI remains completely responsive and interactive.*

---

## ⚡ 3. Starting the FastAPI Server

Navigate to your `backend/` directory from your terminal and execute:

### Step A: Initialize Virtual Environment
```bash
cd backend
python3 -m venv venv
```

### Step B: Activate the Virtual Environment
* **On macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```
* **On Windows (CMD)**:
  ```cmd
  venv\Scripts\activate.bat
  ```
* **On Windows (PowerShell)**:
  ```powershell
  venv\Scripts\Activate.ps1
  ```

### Step C: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step D: Launch server with Uvicorn
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Your server is now live at `http://localhost:8000`. You can explore the interactive API Explorer (Swagger UI) by loading `http://localhost:8000/docs` inside your web browser!

---

## 📱 4. Launching & Testing the Android App

The Android emulator routes network requests destined to `10.0.2.2` directly back to the developer machine's `127.0.0.1` (localhost).

1. Build and boot the Android Application in your Emulator.
2. Navigate to the **Cloud Connectors** screen (Vault tab).
3. At the top of the viewport, inspect the **INTEGRATION SWITCHBOARD**.
4. Flip the **FastAPI SRE Engine** switch to **Active (ONLINE)**.
5. The system will ping your Uvicorn instance. If reachable, the status card turns **Vibrant Green** signaling a live integration!
6. Head to the **SRE Dashboard Screen**, hit **START NETWORK DISCOVERY**. Watch the terminal console as FastAPI dispatches Celery-style background thread sweep workers, queries Boto3 APIs, updates PostgreSQL schemas, and polls progress metrics from 0% to 100%!
7. Spot security threats in the **AI Doctor Incident Vault** and trigger programmatic self-healing:
   - For Security Group Wildcard Ingress issues, FastAPI will invoke AWS SDK to revoke unrestricted internet access on port 22 and bind a secure subnetwork tunnel instead.
   - For Unencrypted S3 Storage Buckets, FastAPI will programmatically apply an active server-side AES256 compliance envelope policy.
