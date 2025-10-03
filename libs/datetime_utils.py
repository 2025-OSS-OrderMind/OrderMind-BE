from datetime import datetime
import locale #
locale.setlocale(locale.LC_ALL, 'ko_KR.UTF-8') # 한국어 로케일 설정, 요일 인식 위해 필요

def check_datetime_format(line:str) -> bool:
    """
    20xx. x. x x:x 형식인지 확인하는 함수
    Args:line (str): 확인할 문자열
    """
    line_list = line.split(',')
    if not line_list:
        return False
    candidate = line_list[0].strip()
    try:
        datetime.strptime(candidate, "%Y. %m. %d. %H:%M")
        return True
    
    except ValueError:
        return False

def delete_datetime_format(line:str) -> bool:
    """
    20xx년 x월 x일 x요일 형식인지 확인하는 함수
    Args:line (str): 확인할 문자열
    """
    line_list = line.split(',')
    if not line_list:
        return line
    candidate = line_list[0].strip()
    try:
        datetime.strptime(candidate, "%Y년 %m월 %d일 %A")
        return True
    
    except ValueError:
        return False