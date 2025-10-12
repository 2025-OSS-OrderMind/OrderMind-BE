import re
import pandas as pd
import os

from .load_file import load_chatlog

def processing_chatlog(file_path:str) -> pd.DataFrame:
    """
    채팅 파일을 불러오고 전처리하는 함수
    Args:file_path (str): 확인할 파일 경로
    """
    lines, file_name = load_chatlog(file_path)

    data = []

    # 패턴 : "YYYY. M. D. HH:MM, 닉네임 : 내용"
    pattern = re.compile(r"(\d{4}\.\s*\d{1,2}\.\s*\d{1,2}\.\s*\d{1,2}:\d{2}),\s*(.+?)\s*:\s*(.+)")

    # 필터링할 키워드 목록(원하면 추가)
    exclude_message_keywords = [
        "삭제된 메시지입니다",
        "사진",
        "이모티콘",
        "님이 들어왔습니다",
        "님이 나갔습니다",
        "메시지를 가렸습니다"
    ]

    exclude_nickname_keywords = [
        "GS평택국제점",
        "오픈채팅봇"
    ]

    for line in lines:
        match = pattern.match(line.strip())
        if match:
            datetime = match.group(1)
            nickname = match.group(2)
            message = match.group(3).strip()

            # 불필요한 메시지는 건너뛰기
            if any(kw in message for kw in exclude_message_keywords):
                continue
            if any(nick in nickname for nick in exclude_nickname_keywords):
                continue

            data.append([datetime, nickname, message])

    # DataFrame으로 변환
    df = pd.DataFrame(data, columns=["날짜시간", "닉네임", "채팅내용"])
    
    return df