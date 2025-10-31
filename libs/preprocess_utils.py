import re
import pandas as pd

from .load_file import load_chatlog

def processing_chatlog(file_path:str) -> pd.DataFrame:
    """
    채팅 파일을 불러오고 전처리하는 함수
    Args:file_path (str): 확인할 파일 경로
    """
    # --------------------------
    import libs.datetime_utils as dt_utils

    chat_data, file_name = load_chatlog(file_path)
    talk_list = []
    for line in chat_data:
        if dt_utils.check_datetime_format(line):
            talk_list.append(line.strip())
        elif dt_utils.delete_datetime_format(line):
            continue
        else:
            if talk_list:
                talk_list[-1] += " " + line.strip()
    # -------------------------

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
        "메시지를 가렸습니다",
        "0원"   # 대화 내용에 예시:8900원 5000원 이런 식으로 가격이 언급되어 있는 경우가 있어서 필터링 해야 함.
    ]

    exclude_nickname_keywords = [
        "GS평택국제점",
        "오픈채팅봇"
    ]

    for line in talk_list:
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
    df["날짜시간"] = pd.to_datetime(df["날짜시간"], format="%Y. %m. %d. %H:%M")
    
    return df