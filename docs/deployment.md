# Deployment Guide

This guide walks through deploying `my-content-processing-solution-accelerator` using the Azure Developer CLI (`azd`).

## Prerequisites
- Azure subscription
- Azure CLI and azd installed
- GitHub account for CI/CD (optional)

## Quick steps
1. Copy `.env.example` to `.env` and populate secrets.
2. Run `azd up` in the repo root to provision resources (ensure bicep files configured).
3. Build and push container images to ACR and use `azd deploy` to deploy Container Apps.

## For production, configure:
- Managed identities and RBAC
- Secure secrets in KeyVault
- Proper scaling rules for Container Apps

## Notes
- Ensure `OPENAI_API_KEY`, `COSMOS_URL`, and `COSMOS_KEY` are set.
- Container images are pushed to ACR as part of `azd` deployment.
