from fastapi import FastAPI, File, UploadFile
from typing import List
import json
app = FastAPI()
@app.post("/test5")
def test5(files: list[UploadFile]): pass

if __name__ == "__main__":
    schema = app.openapi()
    print("TEST5:", json.dumps(schema['components']['schemas'].get('Body_test5_test5_post', {}), indent=2))
