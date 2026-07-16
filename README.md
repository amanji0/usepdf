# UsePDF

A free, self-hosted, open-source PDF toolkit built as a premium alternative to services like iLovePDF.

UsePDF allows you to organize, optimize, convert, and secure your PDF documents locally without exposing your sensitive files to third-party APIs. It runs entirely on your own hardware via Docker.

## Features

- **Organize**: Merge multiple PDFs, split pages, and rotate documents.
- **Optimize**: Compress heavy PDFs into smaller, web-friendly sizes without losing quality.
- **Convert**: 
  - Convert PDF to JPG / JPG to PDF
  - Convert PDF to editable Word (.docx), PowerPoint (.pptx), and Excel (.xlsx) files
  - Convert PDF to Apple Pages (natively supported via DOCX)
- **Security**: Password protect PDFs or unlock encrypted documents.

## Tech Stack

- **Backend**: Python 3.11, FastAPI, Celery, Redis
- **Frontend**: React 18, Vite, TypeScript, Lucide Icons
- **PDF Engines**: PyMuPDF, pdf2docx, python-pptx, pdfplumber, PyPDF2
- **Infrastructure**: Docker & Docker Compose

## Quick Start

1. Ensure you have **Docker** and **Docker Compose** installed on your system.
2. Clone this repository.
3. Boot the application stack:

```bash
docker compose up --build
```

4. Once the containers are running, open your web browser and navigate to:
```
http://localhost:5173
```

## Production Deployment (VPS)

UsePDF is designed to be easily deployed to a Virtual Private Server (VPS) using Docker Compose and Caddy for automatic HTTPS.

1. SSH into your VPS and install Docker & Docker Compose.
2. Clone the repository to the server.
3. Copy the production environment example and configure it:
   ```bash
   cp .env.prod.example .env
   # Edit .env to set your DOMAIN and strong passwords
   nano .env
   ```
4. Run the deployment script:
   ```bash
   ./scripts/deploy.sh
   ```
The application will automatically provision an SSL certificate for your domain and start securely handling traffic.

## Aesthetic Design

UsePDF features a premium, responsive Light Mode UI inspired by Apple's design language, utilizing frosted glassmorphism, subtle drop shadows, and clean SVG iconography for a stunning user experience.
