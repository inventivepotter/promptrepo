#!/bin/bash

# Script to generate TypeScript types from FastAPI OpenAPI schema

echo "Generating TypeScript types from FastAPI OpenAPI schema..."

# Download OpenAPI schema
curl -s http://localhost:8000/openapi.json > ./openapi-schema.json

# # Kill the server
# kill $SERVER_PID

# Generate TypeScript types using openapi-typescript
npx openapi-typescript openapi-schema.json --output frontend/types/generated/api.ts

echo "TypeScript types generated successfully at frontend/types/generated/api.ts"

# Optional: Clean up schema file
rm openapi-schema.json