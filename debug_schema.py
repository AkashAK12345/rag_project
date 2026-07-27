from fastapi.testclient import TestClient
from api_main import app
import json

schema = app.openapi()
print('UPLOAD:', json.dumps(schema['paths']['/api/v1/upload']['post']['requestBody'], indent=2))
print('INGESTION:', json.dumps(schema['paths']['/api/v1/ingestion']['post']['requestBody'], indent=2))
