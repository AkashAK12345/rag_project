import json
from api_main import app

def resolve_ref(schema, ref):
    parts = ref.split('/')[1:]
    curr = schema
    for p in parts:
        curr = curr[p]
    return curr

schema = app.openapi()

upload_req = schema['paths']['/api/v1/upload']['post']['requestBody']
if '$ref' in upload_req['content']['multipart/form-data']['schema']:
    upload_schema = resolve_ref(schema, upload_req['content']['multipart/form-data']['schema']['$ref'])
else:
    upload_schema = upload_req['content']['multipart/form-data']['schema']

ingestion_req = schema['paths']['/api/v1/ingestion']['post']['requestBody']
if '$ref' in ingestion_req['content']['multipart/form-data']['schema']:
    ingestion_schema = resolve_ref(schema, ingestion_req['content']['multipart/form-data']['schema']['$ref'])
else:
    ingestion_schema = ingestion_req['content']['multipart/form-data']['schema']

output = {
    'upload_schema': upload_schema,
    'ingestion_schema': ingestion_schema
}

with open('debug_actual_schemas.json', 'w') as f:
    json.dump(output, f, indent=2)
print("Schemas dumped to debug_actual_schemas.json")
