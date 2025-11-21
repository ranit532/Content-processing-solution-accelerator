# Pipeline Architecture

See the README for a high-level diagram.

Components:
- Frontend (React) — upload, validation UI, history
- Backend (FastAPI) — ingestion, retrieval, validation endpoints
- Blob Storage — stores raw documents
- Queue Storage — event bus for processing
- Processor — container that consumes queue messages and runs extraction, mapping
- Cosmos DB — stores final structured results
- Azure AI Services — OCR, GPT Vision, OpenAI for mapping and scoring

Processing flow:
1. User uploads document via frontend
2. Backend stores document to Blob and enqueues a message
3. Processor consumes message, runs OCR and model-driven schema mapping
4. Processor stores results in Cosmos DB and sets confidence scores
5. If confidence below threshold, a human-validation message is enqueued
6. Frontend displays results for validation
