import json
import pandas as pd

from libs.filtering_utils import *
from libs.preprocess_utils import processing_chatlog
from .test_json import my_json_2 as my_json

from libs.prompt import build_prompt2, build_prompt3
from libs.api import call_openai_api, call_openai_api_mini, timer
from libs.email import send_email, GMAIL_PASSWORD
import time, math
import sys, io, os

from collections import OrderedDict
import re


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

data_file_path = data_file_path.replace("\\", "/") #경로 구분자 통일
folder_path = os.path.dirname(data_file_path)


def build_nickname_order_map(df: pd.DataFrame) -> OrderedDict:
    """
    닉네임이 말한 4자리 숫자(주문번호)를 모두 수집하여,
    OrderedDict 로 반환.
    """
    nickname_map = OrderedDict()

    # 4자리 주문번호 패턴
    pattern = re.compile(r"(?<!\d)(\d{4})(?!\d)") # 독립된 4자리 숫자

    for idx, row in df.iterrows():
        nickname = row["닉네임"]
        message = row["채팅내용"]

        # 메시지에 있는 모든 4자리 번호 추출
        nums = pattern.findall(message)
        if not nums:
            continue

        # dict에 없으면 생성
        if nickname not in nickname_map:
            nickname_map[nickname] = []

        # 번호들을 append (중복 제거는 선택)
        for num in nums:
            if num not in nickname_map[nickname]:
                nickname_map[nickname].append(num)

    sorted_items = sorted(
        nickname_map.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )

    return OrderedDict(sorted_items)

def df_to_str(df: pd.DataFrame) -> str:
    lines = df.apply(lambda row: f"{row['날짜시간']} {row['닉네임']} : {row['채팅내용']}", axis=1)
    text = "\n".join(lines)
    return text

@timer
def ai_pipeline(_file_path: str | None = ''):
    s_time = time.perf_counter()

    # 위 JSON을 파싱, Dictionary와 배열로 구성되어 있음.
    parsed_json = item_data

    # items를 ["제품명:키워드", "제품명", ...] 으로 파싱.
    items_list = []
    items_column_list = []
    items = parsed_json["items"]
    for item in items:

        item_str = item["name"]

        items_column_list.append(item_str)

        if (len(item["keywords"])):
            item_str += ":" + ', '.join(item["keywords"])
        
        items_list.append(item_str)
    # items 파싱 완료
    print('\n'.join(items_list))

    ignore_items_list = []
    ignore_items = parsed_json["ignore_items"]
    for item in ignore_items:
        item_str = item["name"]
        ignore_items_list.append(item_str)
    
    # ignore_items 파싱 완료
    print('\n'.join(ignore_items_list))
    
    
    print('\033[96m' + 'items_list 테스트 출력' + '\033[0m', items_list, 
          '\033[96m' + '------------------------------------------------' + '\033[0m', sep='\n')


    email_address = parsed_json['email_address']

    print('\033[95m' + f'EMAIL: {email_address}' + '\033[0m')

    # 파싱한 날짜를 pandas용 Timestamp 객체로 만듦
    start = pd.to_datetime(parsed_json['date_range']['start'])
    end = pd.to_datetime(parsed_json['date_range']['end'])

    # 채팅 로그 파일 경로
    file_dir = data_file_path

    # 채팅 로그로 DataFrame 생성
    df = processing_chatlog(file_dir)

    # 날짜 사이로 필터링
    root_df = filter_by_date_range(df, start, end)

    '''ID란 주문 번호로 쓰는 전화번호 뒤에 4자리 입니다.'''
    # 채팅내용에 ID가 등장하는 해당 채팅 데이터들만 필터링하여 가져옵니다.
    id_df = filter_by_4digit(root_df) 

    #ID가 등장한 채팅 데이터들 출력(임시값 이후 제거 예정)
    print('\033[93m' + '선택한 기간 동안 ID가 등장한 채팅 데이터들입니다.' + '\033[0m', id_df.head(5),
          '\033[93m' + '------------------------------------------------' + '\033[0m', sep='\n')
    
    
    id_list = id_df['채팅내용'].str.extractall(r'(\d{4})')[0].to_list() # ID 리스트를 뽑습니다.
    id_list = list(set(id_list)) # ID가 채팅내역에서 중복되어 나오기 때문에 set으로 감싸줍니다.
    
    print("고객 수: ", len(id_list))

    nickname_orders = build_nickname_order_map(root_df)

    nick_count = 0
    big_count = 0
    for i in nickname_orders.keys():
        print(i, nickname_orders[i])
        if (len(nickname_orders[i]) > 1):
            big_count += 1
        nick_count += 1

    print("닉네임 수:", nick_count)
    print("닉네임 1개 이상 수:", big_count)
    print("예상 시간:", (big_count * 30 + nick_count - big_count)/60)

    print(df_to_str(filter_by_nickname(root_df, '피스메이커 프로도')))

    # result 프레임 생성
    columns = ['주문번호'] + items_column_list
    result_df = pd.DataFrame(columns=columns)

    sus_columns = ['날짜', '닉네임', '원본 메시지', '이유']
    sus_df = pd.DataFrame(columns=sus_columns)

    fname_dup_sus = os.path.join(folder_path, '중복_의심_주문.txt')
    with open(fname_dup_sus, "w", encoding="utf-8") as f: # 파일 생성 및 내용 초기화
        f.write(f"")
    
    for customer_id in id_list: # 사용자 주문번호 목록으로 for 문 시작
        customer_chat_df = filter_by_4digit(root_df, customer_id)

        users = list(set(customer_chat_df['닉네임'].unique()))
        if (len(users) > 1):
            print("해당 주문은 중복 번호가 의심되는 주문번호입니다.")
            print(users)
            print(customer_chat_df)

            with open(fname_dup_sus, "a", encoding="utf-8") as f:
                f.write(f"=== 중복 의심 주문번호: {customer_id} ===\n")
                f.write(f"닉네임 목록: {users}\n")
                f.write(customer_chat_df.to_string(index=False))
                f.write("\n\n")

    try:
        customer_count = 0
        i = 1

        print("AI 파이프라인 시작")
        for nick, order_list in nickname_orders.items(): #
            print(f"---------{i} 번째 종합을 시작합니다----------")
            i += 1
            print(f"닉네임: '{nick}' 이 말한 주문 번호: ", order_list)
            filtered_df = filter_by_nickname(root_df, nick)
            chat = df_to_str(filtered_df)
            
            call_api, build_prompt = ((call_openai_api, build_prompt2) if (len(order_list) > 1) \
                                    else (call_openai_api_mini, build_prompt3)) # first function and tuple unpacking

            ai_response = call_api(build_prompt(items_list, ignore_items_list, chat))
            ai_response = ai_response.replace("```json", "").replace("```", "") # ```json {...} ``` 문자열 청소
            ai_json = dict()
            try:
                ai_json = json.loads(ai_response)

            except json.decoder.JSONDecodeError: # JSON 파싱에 실패하면 한 번 더 재시도
                ai_response = call_api(build_prompt(items_list, ignore_items_list, chat))
                ai_response = ai_response.replace("```json", "").replace("```", "") # ```json {...} ``` 문자열 청소

                ai_json = json.loads(ai_response)
        

            orders = ai_json["orders"]
            
            for order in orders:
                number = order["number"]
                items = order["items"]

                if (len(items) < 1):
                    continue
                
                
                items:str = order["items"]

                number = str(abs(int(number))) # 만약에 번호에 -가 들어간 경우, (-) 부호가 붙여져서 엑셀에 저장되는걸 막기 위해 절댓값으로 치환하여 다시 str로 저장.

                row = {col: "" for col in columns}
                row['주문번호'] = number
                
                is_exist_item = False
                for item_name, qty in items.items():
                    item_name = item_name.partition(':')[0] # ChatGPT 문자열에 :가 포함되면 :부터 맨끝까지 삭제하는 코드를 만들고싶어
                    if qty == '0': continue
                    if item_name in row:
                        row[item_name] = qty
                        is_exist_item = True
                
                if not is_exist_item: continue

                result_df.loc[len(result_df)] = row
                print(f'{number} 새로운 행 생성', row)

                customer_count += 1
            
            
            uncertain_orders = ai_json["uncertain"]

            for order in uncertain_orders:
                nickname = order['nickname']
                timestamp = order['timestamp']
                reason = order['reason']
                message = order['message']

                if ('문의' in reason): # reason에 문의에 대한거다라는 말이 포함되어있으면 sus_df에 추가시키지 않고 넘김.
                    continue
                if ('잡담' in reason): # reason에 잡담에 대한거다라는 말이 포함되어있으면 sus_df에 추가시키지 않고 넘김.
                    continue
                if ('제외 제품' in reason): # reason에 제외 제품에 대한거다라는 말이 포함되어있으면 sus_df에 추가시키지 않고 넘김.
                    continue
                if ('제외 목록' in reason): # ..
                    continue
                if ('제외 단어' in reason): # ..
                    continue

                row = {col: "" for col in sus_columns}
                
                # sus_columns = ['날짜', '닉네임', '원본 메시지', '이유']
                row['날짜'] = timestamp
                row['닉네임'] = nickname
                row['원본 메시지'] = message
                row['이유'] = reason
                sus_df.loc[len(sus_df)] = row
    finally:
        start_str = start.strftime("%Y-%m-%d_%H%M")
        end_str = end.strftime("%Y-%m-%d_%H%M")
        fname_output_csv = os.path.join(folder_path, f'종합_{start_str}_to_{end_str}.csv')
        fname_sus_csv = os.path.join(folder_path, '의심_주문_리스트.csv')

        e_time = time.perf_counter()

        result_df.to_csv(fname_output_csv, index=False, encoding='utf-8-sig')
        sus_df.to_csv(fname_sus_csv, index=False, encoding='utf-8-sig')

        send_email('gm.sinmj@gmail.com', 'OrderMind', '20221995@edu.hanbat.ac.kr', '[OrderMind] 띵동~ 주문 종합이 완료됐어요!', \
                   f'종합된 총 고객 수는 {customer_count}명이에요.\n\n종합될 때까지 약 {math.ceil((e_time-s_time)/60)}분 정도 소요됐어요!', \
                    GMAIL_PASSWORD, [fname_output_csv, fname_sus_csv, fname_dup_sus])



        


if __name__ == '__main__':
    ai_pipeline()