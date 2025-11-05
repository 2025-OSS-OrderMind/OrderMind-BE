from libs.preprocess_utils import *
import pandas as pd
from libs.load_file import load_csv
from libs.filtering_utils import *



# 제일 먼저 전처리를 하는 단계입니다. csv 파일로 저장됩니다.

df = processing_chatlog("./test_data/Talk_2025.8.8 21_50-1.txt")

df.to_csv("./temp.csv", index=False, encoding="utf-8-sig")


df = load_csv("temp.csv") # csv 파일을 불러옵니다.

# 날짜 문자열을 입력 받아오고 pd.to_datetime 함수로 DataFrame을 마스킹할 Timestamp를 만들어줍니다.
start = pd.to_datetime('2025. 7. 4. 09:45', format="%Y. %m. %d. %H:%M")
end = pd.to_datetime('2025. 7. 6. 13:35', format="%Y. %m. %d. %H:%M")
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

