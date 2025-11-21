from fastapi import FastAPI 
from pydantic import BaseModel,Field  #구조체 정의를 위해 import
from fastapi import File, UploadFile, Form 
from libs.schemas import Item
import os #파일 및 디렉토리 작업을 위한 os 모듈
import subprocess 
import sys
import uuid #고유 파일 이름 생성을 위한 uuid 모듈
import threading

app = FastAPI()

RESULTS_FOLDER = "results" 
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# 첫 화면 동작 확인
@app.get("/")
def read_root():
    return {"Hello": "FastAPI"}

# 파일 업로드 처리 (임시)
@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...), 
    item_data: str = Form(...)  # Pydantic 모델을 문자열로 받습니다. (이름을 item -> item_data로 변경)
):
    
    try:
        item = Item.model_validate_json(item_data) #json 문자열을 Pydantic 모델로 파싱
    except Exception as e:
        # JSON 파싱 실패 시 오류 반환
        print(f"--- [Debug] JSON Parsing FAILED: {e}")
        return {"error": "Invalid Item JSON data", "details": str(e)}

    #파일 내용을 읽어와 contents 변수에 저장합니다.
    contents = await file.read()

    #--------------디버그 용--------------------------
    print(f"파일이름: {file.filename})")
    print(f"파일 사이즈:{len(contents)} bytes")
    print(f"Date1: {item.date_range['start']}")
    print(f"Date2: {item.date_range['end']}")
    print(f"Item List: {item.items}")


    process_id = str(uuid.uuid4()) #고유 프로세스 ID 생성   
    process_folder_path = os.path.join(RESULTS_FOLDER, process_id) #프로세스별 결과 폴더 경로
    os.makedirs(process_folder_path, exist_ok=True) #프로세스별 결과 폴더 생성
    save_path = os.path.join(process_folder_path, file.filename) #저장할 파일 경로

    try: #cp949형식일 경우'utf-8' 형식으로 파일에 저장
        decoded_contents = contents.decode('cp949')
        with open(save_path, "w", encoding="utf-8") as buffer: #버퍼로 저장
            buffer.write(decoded_contents)
    except UnicodeDecodeError: #디코딩 오류시 바이너리 형식으로 저장
        with open(save_path, "wb") as buffer:
            buffer.write(contents)


    # main.py에 파일경로와 item json문자열을 인자로 전달
    command = [sys.executable,"-m", "src.main", save_path, item_data] 
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) #프로젝트 루트 디렉토리 경로
    print(f"--- 실행 명령어: {' '.join(command)} ---")
    print(f"--- 작업 디렉토리: {project_root} ---")

    
    try:
        # 비동기 실행 (백그라운드에서 실행하고 즉시 반환)
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=project_root,
            text=True,
            encoding='utf-8', # 출력 인코딩 설정
            errors='replace', # 인코딩 오류 발생 시 대체 문자로 처리
        )   

        print("STDOUT PIPE:", process.stdout)
        print("STDERR PIPE:", process.stderr)
        print("Process running?", process.poll())
        def stream_reader(stream, name):
            for line in iter(stream.readline, ''):
                print(f"[{name}] {line}", flush=True)

        threading.Thread(target=stream_reader, args=(process.stdout, "STDOUT"), daemon=True).start()
        threading.Thread(target=stream_reader, args=(process.stderr, "STDERR"), daemon=True).start()

        #sys.stdout.flush()
        # 즉시 응답 반환 (프로세스는 백그라운드에서 계속 실행)
        return {
            "message": f"{file.filename} 파일 업로드 완료. 백그라운드에서 처리 중입니다.",
            "received_item_data": item.model_dump(),
            "process_id": process_id,
            "status": "processing"
        }
        
    except Exception as e:
        print(f"--- main.py 실행 중 오류: {e} ---")
        return {"error": f"main.py 실행 오류: {str(e)}"}

