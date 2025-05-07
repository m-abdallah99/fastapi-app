# FastAPI Production App

Build and deploy a production-ready containerized Python web application with FastAPI, PostgreSQL database, Redis caching, Nginx reverse proxy, using Docker Compose.


# Features
- FastAPI with async PostgreSQL + Redis
- Multi-stage Docker builds
- Minimal Alpine images
- Nginx as reverse proxy
- Security scanning with Trivy
- Volume-backed PostgreSQL persistence

# Prerequisites
- Docker
- Docker Compose
- Trivy (for security scanning)

# Architecture

        ┌────────────┐
        │   Client   │
        └─────┬──────┘
              │
       ┌──────▼──────┐
       │   Nginx     │
       └──────┬──────┘
              │
    ┌─────────▼──────────┐
    │    FastAPI (web)   │
    └────┬────────┬──────┘
         │        │
 ┌───────▼───┐ ┌──▼────────┐
 │ PostgreSQL│ │   Redis   │
 └───────────┘ └──────────┘


# Deployment And Access

**deploy**
bash: "docker-compose up --build"

**access from localhost**
API: http://localhost:8000/


# Security Scan
- Run Trivy: "trivy image fastapi-app_web"
- open trivy-report.txt file to see the results 

**results**
fastapi-app-web (alpine 3.21.3)
===============================
Total: 1 (UNKNOWN: 0, LOW: 0, MEDIUM: 0, HIGH: 1, CRITICAL: 0)

┌─────────────┬────────────────┬──────────┬────────┬───────────────────┬───────────────┬───────────────────────────────────────────────────────┐
│   Library   │ Vulnerability  │ Severity │ Status │ Installed Version │ Fixed Version │                         Title                         │
├─────────────┼────────────────┼──────────┼────────┼───────────────────┼───────────────┼───────────────────────────────────────────────────────┤
│ sqlite-libs │ CVE-2025-29087 │ HIGH     │ fixed  │ 3.48.0-r0         │ 3.48.0-r1     │ sqlite: Integer Overflow in SQLite concat_ws Function │
│             │                │          │        │                   │               │ https://avd.aquasec.com/nvd/cve-2025-29087            │
└─────────────┴────────────────┴──────────┴────────┴───────────────────┴───────────────┴───────────────────────────────────────────────────────┘

Python (python-pkg)
===================
Total: 2 (UNKNOWN: 0, LOW: 0, MEDIUM: 0, HIGH: 2, CRITICAL: 0)

┌───────────────────────┬────────────────┬──────────┬────────┬───────────────────┬───────────────┬─────────────────────────────────────────────────────┐
│        Library        │ Vulnerability  │ Severity │ Status │ Installed Version │ Fixed Version │                        Title                        │
├───────────────────────┼────────────────┼──────────┼────────┼───────────────────┼───────────────┼─────────────────────────────────────────────────────┤
│ setuptools (METADATA) │ CVE-2024-6345  │ HIGH     │ fixed  │ 65.5.1            │ 70.0.0        │ pypa/setuptools: Remote code execution via download │
│                       │                │          │        │                   │               │ functions in the package_index module in...         │
│                       │                │          │        │                   │               │ https://avd.aquasec.com/nvd/cve-2024-6345           │
├───────────────────────┼────────────────┤          │        ├───────────────────┼───────────────┼─────────────────────────────────────────────────────┤
│ starlette (METADATA)  │ CVE-2024-47874 │          │        │ 0.36.3            │ 0.40.0        │ starlette: Starlette Denial of service (DoS) via    │
│                       │                │          │        │                   │               │ multipart/form-data                                 │
│                       │                │          │        │                   │               │ https://avd.aquasec.com/nvd/cve-2024-47874          │
└───────────────────────┴────────────────┴──────────┴────────┴───────────────────┴───────────────┴─────────────────────────────────────────────────────┘

