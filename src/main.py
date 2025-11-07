from libs.preprocess_utils import*
import pandas as pd
from libs.load_file import load_csv
from libs.filtering_utils import*
import sys, io# main.py에 인자를 전달하기 위해 sys 모듈을 import 합니다.
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
#Server.py에서 전달된 인자를 받는 부분입니다.
data_file_path = sys.argv[1]  # 첫 번째 인자는 업로드된 파일 경로입니다.
item_json = sys.argv[2]      # 두 번째 인자는 Item JSON 문자열입니다.
try: #Json 파싱
    item_data = json.loads(item_json)
except Exception as e:
    print(f"[ERROR] JSON 파싱 실패: {e}")
    sys.exit(1)

#-----------------채팅로그 전처리 테스트 코드------------------------
# 제일 먼저 전처리를 하는 단계입니다. csv 파일로 저장됩니다.
# df = processing_chatlog("./test_data/Talk_2025.8.8 21_50-1.txt")
# df.to_csv("./temp.csv", index=False, encoding="utf-8-sig")
#-------------------------------------------------------------------

# CSV에서 읽어온 '날짜시간' 컬럼(문자열)을 
# Pandas 날짜 객체(datetime)로 변환합니다.

df = load_csv(data_file_path) # csv 파일을 불러옵니다.
df['날짜시간'] = pd.to_datetime(df['날짜시간']) # '날짜시간' 컬럼을 datetime 객체로 변환합니다.


# 날짜 문자열을 입력 받아오고 pd.to_datetime 함수로 DataFrame을 마스킹할 Timestamp를 만들어줍니다.
start = pd.to_datetime(item_data["date1"], format="%Y. %m. %d. %H:%M")
end = pd.to_datetime(item_data["date2"], format="%Y. %m. %d. %H:%M")
start
# 라이브러리에다가 만든 필터링 함수를 사용하여 날짜 사이의 채팅 데이터를 필터링해 가져옵니다.
date_filtered = filter_by_date_range(df, start, end)


'''ID란 주문 번호로 쓰는 전화번호 뒤에 4자리 입니다.'''
# 채팅내용에 ID가 등장하는 해당 채팅 데이터들만 필터링하여 가져옵니다.
id_filtered = filter_by_4digit(date_filtered) 

id_list = id_filtered['채팅내용'].str.extractall(r'(\d{4})')[0].to_list() # ID 리스트를 뽑습니다.
id_list = list(set(id_list)) # ID가 채팅내역에서 중복되어 나오기 때문에 set으로 감싸줍니다.


print(str(id_list), \
      '\033[94m' + \
        '%s ~ %s 동안의 고객 수: %d' % (start, end, len(id_list)) + \
            '\033[0m', sep='\n')



nickname_filtered = filter_by_nickname(date_filtered, '초롱초롱 네오')

print(nickname_filtered, '\033[95m' + '초롱초롱 네오가 말한 채팅 데이터들입니다.' + '\033[0m', sep='\n')

nickname_digit_filtered = filter_by_4digit(nickname_filtered)

print(nickname_digit_filtered, '\033[95m' + '초롱초롱 네오가 말한 ID 데이터들입니다.' + '\033[0m', sep='\n')

