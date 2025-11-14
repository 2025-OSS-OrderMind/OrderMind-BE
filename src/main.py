from libs.preprocess_utils import*
import pandas as pd
from libs.load_file import load_csv
from libs.filtering_utils import*
#from libs.api import call_google_genai_api, API_KEY # 테스트를 위해 import
from libs.api import call_local_ai_server, LM_STUDIO_URL, API_KEY
import sys, io# main.py에 인자를 전달하기 위해 sys 모듈을 import 합니다.
import json
import re
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8') #출력 인코딩 설정
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8') #에러 출력 인코딩 설정

#Server.py에서 전달된 인자를 받는 부분입니다.
data_file_path = sys.argv[1]  # 첫 번째 인자는 업로드된 파일 경로입니다.
item_json = sys.argv[2]      # 두 번째 인자는 Item JSON 문자열입니다.
try: #Json 파싱
    item_data = json.loads(item_json)
except Exception as e:
    print(f"[ERROR] JSON 파싱 실패: {e}")
    sys.exit(1)

folder_path = os.path.dirname(data_file_path)
output_csv = os.path.join(folder_path, "temp.csv")
print(f"--- [Debug] 데이터 파일 경로: {data_file_path} ---")
#-----------------채팅로그 전처리 테스트 코드------------------------
data_file_path = data_file_path.replace("\\", "/") #경로 구분자 통일
print(f"--- [Debug] 수정된 데이터 파일 경로: {data_file_path} ---")
#제일 먼저 전처리를 하는 단계입니다. csv 파일로 저장됩니다.
df = processing_chatlog(data_file_path)
df.to_csv(output_csv, index=False, encoding="utf-8-sig")


# CSV에서 읽어온 '날짜시간' 컬럼(문자열)을 
# Pandas 날짜 객체(datetime)로 변환합니다.

df = load_csv(output_csv) # csv 파일을 불러옵니다.
df['날짜시간'] = pd.to_datetime(df['날짜시간']) # '날짜시간' 컬럼을 datetime 객체로 변환합니다.

start_data = item_data["date_range"]["start"]
end_data = item_data["date_range"]["end"]


# 날짜 문자열을 입력 받아오고 pd.to_datetime 함수로 DataFrame을 마스킹할 Timestamp를 만들어줍니다.
start = pd.to_datetime(start_data, format="%Y. %m. %d. %H:%M")
end = pd.to_datetime(end_data, format="%Y. %m. %d. %H:%M")
start
# 라이브러리에다가 만든 필터링 함수를 사용하여 날짜 사이의 채팅 데이터를 필터링해 가져옵니다.
date_filtered = filter_by_date_range(df, start, end)


'''ID란 주문 번호로 쓰는 전화번호 뒤에 4자리 입니다.'''
# 채팅내용에 ID가 등장하는 해당 채팅 데이터들만 필터링하여 가져옵니다.
id_filtered = filter_by_4digit(date_filtered) 


#ID가 등장한 채팅 데이터들 출력(임시값 이후 제거 예정)
print(id_filtered, '\033[93m' + '선택한 기간 동안 ID가 등장한 채팅 데이터들입니다.' + '\033[0m', sep='\n')

id_list = id_filtered['채팅내용'].str.extractall(r'(\d{4})')[0].to_list() # ID 리스트를 뽑습니다.
id_list = list(set(id_list)) # ID가 채팅내역에서 중복되어 나오기 때문에 set으로 감싸줍니다.


print(str(id_list), \
      '\033[94m' + \
        '%s ~ %s 동안의 고객 수: %d' % (start, end, len(id_list)) + \
            '\033[0m', sep='\n')


# 특정 ID를 지정해 해당 ID가 포함된 채팅만 추출 (예: 3556)
target_id = None
try:
    target_id = str(item_data.get("target_id")) if "target_id" in item_data else None
except Exception:
    target_id = None

# target_id가 있으면 그 ID가 채팅내용에 포함된 행만 필터링
target_id_in_id_filtered = id_filtered.iloc[0:0]
if target_id:
    if target_id in id_list:
        target_pattern = rf'\b{re.escape(target_id)}\b'
        target_id_in_id_filtered = id_filtered[id_filtered['채팅내용'].str.contains(target_pattern, na=False)]
        print(target_id_in_id_filtered, '\033[96m' + f'지정한 ID({target_id})가 포함된 채팅 데이터들입니다.' + '\033[0m', sep='\n')
    else:
        print(f"지정한 ID({target_id})는 기간 내 채팅 ID 목록에 없습니다.")

nickname_filtered = filter_by_nickname(date_filtered, '초롱초롱 네오')

print(nickname_filtered, '\033[95m' + '초롱초롱 네오가 말한 채팅 데이터들입니다.' + '\033[0m', sep='\n')

nickname_digit_filtered = filter_by_4digit(nickname_filtered)

print(nickname_digit_filtered, '\033[95m' + '초롱초롱 네오가 말한 ID 데이터들입니다.' + '\033[0m', sep='\n')


# 닉네임에서 등장한 4자리 숫자만 추출
nickname_ids = nickname_digit_filtered['채팅내용'].str.extractall(r'(\d{4})')[0].unique().tolist() if not nickname_digit_filtered.empty else []

# 위 숫자들만 사용하여 id_filtered에서 해당 숫자가 들어있는 행만 추출
if nickname_ids:
    pattern = '|'.join(map(re.escape, nickname_ids))
    nickname_ids_in_id_filtered = id_filtered[id_filtered['채팅내용'].str.contains(pattern, na=False)]
else:
    nickname_ids_in_id_filtered = id_filtered.iloc[0:0]  # 빈 DataFrame

print(nickname_ids_in_id_filtered, '\033[96m' + '닉네임에서 등장한 ID가 포함된 채팅 데이터들입니다.' + '\033[0m', sep='\n')




#---------------------Google GenAI API 테스트 코드------------------------

# id_list에 있는 ID(숫자)가 id_filtered의 '채팅내용' 안에 존재하는 메시지만 리스트로 수집
matched_messages = []
if id_list:
    for _, row in id_filtered.iterrows():
        text = str(row.get('채팅내용', ''))
        for idv in id_list:
            if idv in text:
                matched_messages.append(text)
                break  # 동일 행은 한 번만 추가

print(matched_messages, '\033[96m' + 'id_list에 있는 ID가 채팅내용에 포함된 메시지 리스트입니다.' + '\033[0m', sep='\n', flush=True)


while True:
    try:
        for i in range(2):  # 테스트로 처음 5개 메시지만 AI 서버에 전송
            messages = matched_messages[i]  
            json_data = call_local_ai_server(LM_STUDIO_URL, API_KEY, messages)
            data = json.loads(json_data)
            print(json_data, '\033[92m' + 'AI 서버 응답 데이터입니다.' + '\033[0m', sep='\n', flush=True)
        break
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다.")
        break

# while True:
#     try:
        
#         user_prompt = input("\nAI에게 물어볼 질문을 입력하세요 (종료하려면 'exit' 입력): ")
#         if user_prompt.lower() == 'exit':
#             print("프로그램을 종료합니다.")
#             break
#         ai_response = call_google_genai_api(API_KEY, user_prompt)

#         #keyword = call_openai_api(LMSTUDIO_URL, API_KEY, user_prompt)
#         if ai_response:
#             print("\n--- Google GenAI API 응답 문자열 ---")
#             print(ai_response)
#         else:
#             print("Google GenAI API 호출에 실패했습니다.")

#     except KeyboardInterrupt:
#         print("\n프로그램을 종료합니다.")
#         break



