#!/bin/bash

# Script to generate TypeScript types from FastAPI OpenAPI schema

echo "Generating TypeScript types from FastAPI OpenAPI schema..."

# Start the FastAPI server temporarily to get the schema
cd backend
uvicorn main:app --host localhost --port 8001 &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Download OpenAPI schema
curl -s http://localhost:8001/openapi.json > ../openapi-schema.json

# Kill the server
kill $SERVER_PID

cd ..

# Generate TypeScript types using openapi-typescript
npx openapi-typescript openapi-schema.json --output frontend/types/generated/api.ts

echo "TypeScript types generated successfully at frontend/types/generated/api.ts"

# Optional: Clean up schema file
rm openapi-schema.json