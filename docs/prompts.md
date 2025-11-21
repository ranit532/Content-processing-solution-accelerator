# Prompt Templates

## OCR Extraction
Extract text, tables and key-value pairs from the document. Return a JSON object with keys: text, tables, key_values.

## Schema Mapping (Invoice)
Map the extracted text into the following JSON schema: invoice_number, date, total, vendor, line_items. Return only JSON.

## Confidence Assessment
Given extracted text and mapped JSON, return a brief rationale and a confidence score between 0 and 1. For production, use a scoring function; for POC use heuristics in `src/services/scoring.py`.
