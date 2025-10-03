def load_chatlog(filename: str)->list:
    """
    채팅 로그 파일을 불러오는 함수
    Args:filename (str): 불러올 파일 경로
    """
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return lines

