# Deploy backend from a prebuilt image (bypass on-platform builds)

Instead of building the image on Railway (which can fail on base image layer pulls), deploy the backend using a prebuilt container image hosted on GHCR.

## 1) Build & push with GitHub Action	s

- A workflow `.github/workflows/backend-image.yml` is added. On push to `main` (changes in `backend/**`), it builds from `backend/Dockerfile.railway` and pushes to:
  - `ghcr.io/<owner>/generative-ai-budget-tracker-backend:latest`
  - `ghcr.io/<owner>/generative-ai-budget-tracker-backend:sha-<commit>`

Ensure GitHub Packages visibility is allowed for your Railway project to pull (public repo is easiest).

## 2) Configure Railway backend service to use the image

- In Railway → backend service → Settings → Deploy from Image
  - Image: `ghcr.io/<owner>/generative-ai-budget-tracker-backend:latest`
  - Registry auth: not required for public images; for private, provide GHCR token
- Remove Dockerfile build configuration for this service.
- Keep your environment variables (SECRET_KEY, DATABASE_URL, etc.).

## 3) Deploy

- Click Deploy (or enable auto-deploy on new image updates).
- Verify `/ready` and `/health`.

## Notes

- This avoids Docker Hub flaky layer pulls on the builder.
- You can pin to `:sha-<commit>` for reproducibility.
- If you need multi-arch, adjust `platforms` in the workflow.
