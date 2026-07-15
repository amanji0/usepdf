# Security Policy — UsePDF

UsePDF is designed to process untrusted PDF files safely in a self-hosted environment. This document outlines the security measures in place.

---

## 1. File Validation

- **Magic byte verification**: Every uploaded file is validated against its magic bytes (file signature) before processing, not just the file extension.
- **MIME type allowlist**: Only explicitly allowed MIME types are accepted:
  - `application/pdf`
  - `image/png`, `image/jpeg`, `image/tiff`, `image/webp`
  - `application/vnd.openxmlformats-officedocument.*` (Office formats)
  - `text/html`, `text/markdown`
- **File size limits**: Configurable via `MAX_FILE_SIZE_MB` (default: 100 MB). Enforced at both the Nginx proxy and application layers.

## 2. Filename Sanitization

- **UUID-only internal names**: All uploaded files are renamed to UUIDs internally (e.g., `a3f8b2c1-...-.pdf`). Original filenames are stored only in metadata and never used in filesystem paths.
- **Path traversal prevention**: Any `..`, `/`, or `\` in filenames is rejected outright.
- **No user-controlled paths**: File storage paths are constructed entirely server-side.

## 3. Subprocess Isolation

- **No `shell=True`**: All subprocess calls use `shell=False` with explicit argument lists to prevent command injection.
- **Fixed argument patterns**: CLI tools (Ghostscript, QPDF, LibreOffice) are invoked with pre-defined argument templates; user input is never interpolated into command strings.
- **Timeouts**: Every subprocess call has a hard timeout (default: 120 seconds) to prevent resource exhaustion.
- **Return code validation**: Non-zero exit codes are treated as errors and logged.

## 4. Docker Isolation

- **Separate containers**: The API, default workers, and LibreOffice workers run in separate containers.
- **Resource limits**: The `worker-office` container is limited to 1 GB RAM and 2 CPUs to prevent LibreOffice from consuming host resources.
- **No privileged mode**: No container runs with `--privileged` or elevated capabilities.
- **Read-only filesystems**: Where possible, containers mount volumes as read-only (except the `/data` volume).

## 5. Auto-Cleanup

- **1-hour TTL**: Uploaded and result files are automatically deleted after `FILE_TTL_SECONDS` (default: 3600 seconds / 1 hour).
- **Periodic sweep**: A background Celery Beat task scans the `/data` directories and removes expired files.
- **No persistent storage of user data**: UsePDF is designed as a stateless processing pipeline—files are transient by design.

## 6. Rate Limiting

- **30 requests/minute per IP**: Applied at the API layer using `slowapi` to prevent abuse.
- **Burst tolerance**: A short burst of up to 30 requests is allowed before throttling.
- **429 response**: Clients exceeding the limit receive a `429 Too Many Requests` response with a `Retry-After` header.

## 7. XXE Protection

- **Disabled external entities**: All XML/SVG parsing uses `defusedxml` to prevent XML External Entity (XXE) attacks.
- **No DTD processing**: DTD loading is disabled in all XML parsers.
- **PDF metadata parsing**: PDF metadata is extracted using safe libraries (`pikepdf`, `PyPDF2`) that do not evaluate embedded scripts.

## 8. LibreOffice Macro Disabling

- **Macro execution disabled**: LibreOffice is invoked with `--norestore --nofirststartwizard --nologo --headless` flags, which disable macro execution.
- **No user profile**: A clean, temporary user profile is used for each conversion to prevent state leakage between requests.
- **Sandboxed conversion**: Office document conversions run in the isolated `worker-office` container with resource limits.

## 9. Network Isolation

- **Internal-only communication**: Worker containers do not expose any ports. They communicate only with Redis on the Docker internal network.
- **No outbound internet**: Processing containers have no need for outbound internet access. You can further restrict this with Docker network policies.
- **API gateway pattern**: The frontend Nginx proxy is the only public-facing entry point, forwarding `/api/*` to the backend.

## 10. CORS Configuration

- **Explicit origin allowlist**: CORS is configured via the `CORS_ORIGINS` environment variable. Only listed origins are allowed.
- **No wildcard origins**: `*` is never used in production CORS configuration.
- **Credentials support**: Credentials (cookies, auth headers) are not sent cross-origin by default.

---

## Reporting Vulnerabilities

If you discover a security vulnerability, please report it responsibly by opening a private issue or contacting the maintainers directly. Do **not** open a public issue for security bugs.

## Recommendations for Production

1. Place Nginx behind a reverse proxy (e.g., Cloudflare, Traefik) with TLS termination.
2. Restrict Docker network egress for worker containers.
3. Enable Docker Content Trust for image verification.
4. Run containers as a non-root user where possible.
5. Regularly update base images and dependencies.
6. Set `FILE_TTL_SECONDS` to the shortest acceptable value.
7. Monitor container resource usage and set alerts for anomalies.
