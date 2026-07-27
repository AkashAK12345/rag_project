from fastapi import FastAPI, File, UploadFile
from typing import List, Annotated
from pydantic import WithJsonSchema
import json

app = FastAPI()
@app.post("/test6")
def test6(files: list[Annotated[UploadFile, WithJsonSchema({"type": "string", "format": "binary"})]] = File(...)): pass

if __name__ == "__main__":
    schema = app.openapi()
    print("TEST6:", json.dumps(schema['components']['schemas'].get('Body_test6_test6_post', {}), indent=2))
