# my-content-processing-solution-accelerator

## Solution Overview

This accelerator enables rapid extraction, transformation, and validation of multi-modal content (PDFs, images, scanned docs, etc.) using Azure AI services, with confidence scoring and human-in-the-loop review. It is designed for scenarios like claims, invoices, contracts, and more, supporting both automated and manual validation workflows.

---

### Key Features
- **Multi-modal content processing**: OCR, GPT Vision, and Content Understanding for text, images, tables, and graphs.
- **Schema-based transformation**: Map extracted data to custom or industry schemas, output as JSON.
- **Confidence scoring**: Automated scoring for extraction and mapping, driving human review when needed.
- **Human-in-the-loop validation**: UI for reviewing, editing, and annotating results.
- **API-driven pipeline**: REST endpoints for ingestion, retrieval, validation, and compute.
- **Azure-native deployment**: Container Apps, Blob Storage, Cosmos DB, Queue Storage, and managed identities.

---

## Architecture Diagram

```mermaid
graph TD
    A[User/Frontend] -->|Upload| B[API Gateway (FastAPI)]
    B -->|Store| C[Azure Blob Storage]
    B -->|Enqueue| D[Azure Queue Storage]
    D -->|Trigger| E[Container App: Processor]
    E -->|OCR, GPT Vision, Content Understanding| F[Azure AI Services]
    E -->|Schema Mapping & Scoring| G[Transformation Service]
    G -->|Store| H[Cosmos DB]
    G -->|Notify| I[Queue: Human Review]
    I -->|Trigger| J[Container App: Validation UI]
    J -->|Review/Edit| H
    H -->|Results| A
```

---

## Services Used
- **Azure AI Foundry**: Generative AI orchestration
- **Azure OpenAI Service**: GPT-5 mini (default), GPT Vision
- **Azure AI Content Understanding**: Multi-modal extraction
- **Azure Blob Storage**: Document storage
- **Azure Cosmos DB**: Structured data storage
- **Azure Queue Storage**: Event-driven pipeline
- **Azure Container Apps**: Scalable compute
- **Azure Container Registry**: Image management

---

## Quick Deploy

1. **Clone the repo**
   ```sh
git clone https://github.com/your-org/my-content-processing-solution-accelerator.git
cd my-content-processing-solution-accelerator
```
2. **Install [Azure Developer CLI](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/overview)**
3. **Provision resources**
   ```sh
azd up
```
4. **Configure environment variables**
   - Copy `.env.example` to `.env` and fill in secrets.
5. **Deploy frontend and backend**
   ```sh
azd deploy
```
6. **Access the app**
   - Frontend: [https://<your-app-url>](https://<your-app-url>)
   - API: [https://<your-api-url>/docs](https://<your-api-url>/docs)

---

## Folder Structure

```
├── src/                # Python backend (FastAPI)
│   ├── api/            # API routes
│   ├── services/       # Content processing, extraction, scoring
│   ├── schemas/        # Data schemas
│   ├── pipelines/      # Processing pipelines
│   └── ...
├── frontend/           # React + Vite + Tailwind frontend
├── infra/              # Bicep templates, azure.yaml
├── docs/               # Documentation
├── .github/workflows/  # CI/CD workflows
├── .devcontainer/      # DevContainer setup
├── .env.example        # Environment variable template
└── README.md           # This file
```

---

## API Endpoints
- `POST /api/ingest` — Upload document
- `GET /api/results/{id}` — Get extraction & mapping results
- `POST /api/validate/{id}` — Submit human validation
- `GET /api/history` — Processing history
- `GET /api/logs` — Pipeline logs

---

## Customization Guide
- **Schemas**: Add or modify JSON schemas in `src/schemas/`
- **Prompts**: Update prompt templates in `src/services/prompts/`
- **Confidence scoring**: Adjust logic in `src/services/scoring.py`

---

## Troubleshooting
- Check logs in Azure Container Apps and Cosmos DB
- Ensure all environment variables are set
- See `docs/troubleshooting.md` for more

---

## Local development - step by step (runnable)

Prerequisites
- Docker & Docker Compose
- Python 3.11
- Node 18+ / npm
- Optional: Azure CLI and azd if you will deploy to Azure

1) Clone and prepare
```bash
git clone https://github.com/your-org/my-content-processing-solution-accelerator.git
cd my-content-processing-solution-accelerator
```

2) Python environment
```bash
python -m venv .venv
source .venv/bin/activate  # zsh / bash on macOS / Linux
pip install --upgrade pip
pip install -r src/requirements.txt
```

3) Frontend dependencies
```bash
npm ci --prefix frontend
```

4) Optional: Playwright test deps
```bash
npm ci --prefix tests/e2e
npx playwright install --with-deps
```

5) Start Azurite (local Storage emulator)
- Using Docker Compose:
```bash
docker-compose up -d azurite
```
- Azurite default dev connection string (use exactly this in `.env` when running locally):

```
BLOB_CONN=DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xnoCQ==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;
QUEUE_CONN=DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xnoCQ==;QueueEndpoint=http://127.0.0.1:10001/devstoreaccount1;
```

6) Create a `.env` from the template and update values
```bash
cp .env.example .env
# Edit .env and set values. For local dev you can set:
# OPENAI_API_KEY= (leave empty to skip external calls)
# API_KEY=dev-key
# KEYVAULT_NAME= (leave empty for local)
# BLOB_CONN and QUEUE_CONN to Azurite strings above
```

7) Run the app + worker locally (two options)

Option A — harness (recommended for quick dev):
```bash
python tests/local/worker_harness.py
```
This starts the FastAPI backend and the worker in-process.

Option B — separate processes / containers:
```bash
# Start API
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
# In another shell (with same .env active)
python -m src.pipelines.worker
```

8) Start the frontend
```bash
npm run dev --prefix frontend
# open http://localhost:5173
```

9) Run tests
- Unit tests
```bash
pytest
```
- E2E (Playwright) tests (requires the backend reachable at http://localhost:8000)
```bash
npx playwright test --project=chromium
```

---

## Azure deployment - step by step

Prerequisites
- An Azure subscription and sufficient quota
- Azure CLI and Azure Developer CLI (azd)
- An Azure AD service principal with contributor role on the target subscription (or use GitHub OIDC) and secrets configured in GitHub

Required GitHub Secrets (used by workflows)
- ACR_LOGIN_SERVER (e.g. myregistry.azurecr.io)
- ACR_USERNAME
- ACR_PASSWORD
- AZURE_CLIENT_ID
- AZURE_TENANT_ID
- AZURE_CLIENT_SECRET
- API_KEY (application API key)

Warning: `azd up` provisions Azure resources and will incur costs. Confirm costing and resource naming before running in production.

Deploy from local machine (interactive):
```bash
azd up
# follow prompts and provide required values; review resources and costs
```

CI/CD (GitHub Actions)
- Push to `main` to trigger `deploy.yml` which builds images, pushes to ACR and runs `azd up` using the service principal credentials stored in GitHub Secrets.

---

## Troubleshooting
- Backend 500 on upload: check container logs (local: the harness prints logs). In Azure: Container Apps logs (Log Analytics).
- Storage errors: ensure `BLOB_CONN` & `QUEUE_CONN` are set correctly (Azurite or real Storage). For Azurite use the dev strings above.
- OpenAI/Model errors: ensure `OPENAI_API_KEY` is set or stub out model calls for local dev.
- Cosmos DB errors: ensure `COSMOS_URL`/`COSMOS_KEY` are set or mock DB calls for unit tests.

Where to find logs
- Local: stdout from `uvicorn` and `worker_harness.py`.
- Azure: Container Apps logs and Log Analytics workspace configured by Bicep. Use `az containerapp logs show` or Azure Portal to inspect logs.

---

## What to customize
- Schemas: `src/schemas/` contains JSON schema examples. Add or modify to match your data model.
- Prompts: `docs/prompts.md` and `src/services/openai_client.py` contain prompt templates used for extraction & mapping.
- Confidence: tune `src/services/scoring.py`.
