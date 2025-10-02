from datetime import datetime
import locale
locale.setlocale(locale.LC_ALL, 'ko_KR.UTF-8')

def check_datetime_format(line:str) -> bool:
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
    line_list = line.split(',')
    if not line_list:
        return line
    candidate = line_list[0].strip()
    try:
        datetime.strptime(candidate, "%Y년 %m월 %d일 %A")
        return True
    
    except ValueError:
        return False