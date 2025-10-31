import pandas as pd
import os

def load_chatlog(file_path: str)->list:
    """
    채팅 로그 파일을 불러오는 함수
    Args:file_path (str): 불러올 파일 경로
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    file_name = os.path.splitext(os.path.basename(file_path))[0]  # 파일 이름만 추출 (확장자 제외)

    return lines, file_name

def load_csv(file_path: str) -> pd.DataFrame:
    """
    csv파일을 불러오는 함수
    Args:file_path (str): 불러올 파일 경로
    """
    df = pd.read_csv(file_path)
    df["날짜시간"] = pd.to_datetime(df["날짜시간"], format="%Y. %m. %d. %H:%M", errors="coerce")
    return df