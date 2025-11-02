from fastapi import FastAPI
from pydantic import BaseModel  
from fastapi import File, UploadFile

class Item(BaseModel):
    name: str
    value: float
    description: str | None = None 

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "FastAPI"}

@app.post("/create-item/")
def create_item(item: Item):
    print(f"Postman으로부터 받은 데이터: {item.name}")
    return {"message": f"'{item.name}' 생성 성공!", "item_data": item}


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    print(file.filename, len(contents))
    return {"filename": file.filename, "size": len(contents)}