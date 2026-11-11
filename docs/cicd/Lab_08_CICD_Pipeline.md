
# Lab 08 — Secure CI/CD with GitHub Actions

## Objective
Build, test, scan and publish a hardened FastAPI
Docker image using GitHub Actions and GHCR.

## Application
- Repository: amitkb-one/devops-home-lab
- Application: FastAPI task API
- Services: FastAPI, PostgreSQL, Redis
- Runtime: Distroless, non-root
- Registry: ghcr.io/amitkb-one/devops-task-api
- Target architecture: linux/amd64

## Pipeline architecture

1. Source changes trigger GitHub Actions.
2. pytest validates application behavior.
3. Docker Buildx builds the image.
4. Trivy generates a vulnerability report.
5. CRITICAL security findings fail the gate.
6. The validated image is saved as an artifact.
7. The publish job loads the validated image.
8. GHCR receives latest and commit-SHA tags.

## Branch strategy
- Feature branches: validation only
- Pull requests: automated tests and scanning
- Main branch: validation and publication

## Security controls
- Distroless runtime
- Non-root execution
- Read-only filesystem in hardened Compose setup
- Dropped Linux capabilities
- Trivy vulnerability scanning
- CRITICAL vulnerability blocking policy
- Scoped GitHub Actions permissions

## Vulnerability baseline
Initial CI scan:
- CRITICAL: 0
- HIGH: 49
- MEDIUM: 113
- LOW: 58

HIGH findings require continued triage.
A passing CRITICAL gate does not imply zero risk.

## Troubleshooting

### Trivy action resolution failure
Cause: Missing v prefix in action version reference.
Resolution: Use a valid published action tag.

### GHCR HTTP 403
Cause: Insufficient workflow permissions.
Resolution: Correct GitHub Actions write permissions
and verify package access.

### Docker image name error
Cause: Incorrect variable or quotation placement.
Resolution: Use "${IMAGE}:latest".

## Validation performed
- Automated tests passed
- Docker build succeeded
- Trivy security gate passed
- Both GHCR tags published
- Image pulled successfully to local Docker
- Image traceability verified
- Deliberately failing pytest test detected

## Future improvements
- Pin third-party actions to reviewed commit SHAs
- Baseline-aware HIGH vulnerability policy
- SBOM and image provenance attestations
- Multi-platform ARM64/AMD64 builds
- Protected release environments
- Automated deployment and rollback
- CI integration for the local RAG application
