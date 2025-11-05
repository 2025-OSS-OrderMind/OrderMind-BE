from fastapi import FastAPI 
from pydantic import BaseModel  
from fastapi import File, UploadFile
from fastapi.responses import FileResponse
import os

app = FastAPI()

TEMP_FOLDER = "temp" 
os.makedirs(TEMP_FOLDER, exist_ok=True) #폴더 없을시에 생성

# 첫 화면 동작 확인
@app.get("/")
def read_root():
    return {"Hello": "FastAPI"}

# 파일 업로드 처리 (임시)
@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read() 
    print(f"파일이름: {file.filename}\n파일 사이즈:{len(contents)}bytes")

    save_path = os.path.join(TEMP_FOLDER, file.filename)
    with open(save_path, "wb") as buffer:
        buffer.write(contents)
    #파일이름 및 사이즈 반환
    return {
        "message": f"{file.filename} 파일이 temp 폴더에 저장되었습니다.",
    } 


