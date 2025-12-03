import requests
import os
from openai import OpenAI
from google import genai
from typing import Optional
from google.genai import errors
from dotenv import load_dotenv

import time, math

# 환경 변수 로드
load_dotenv("key.env")
#---------------------예시값----------------------
# LM Studio가 제공하는 로컬 서버 주소
LM_STUDIO_URL = "http://localhost:1234/v1" #예시: 실제 주소로 변경
# API 키
API_KEY = os.environ.get("GEMINI_API_KEY")
#--------------------------------------------------

# 타이머 데코레이터
def timer(fn):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        end = time.perf_counter()
        print(f"{fn.__name__} 실행 시간: {end - start:.2f}초", end='')
        if (end-start) / 60 >= 5:
            print(f'\b (약 {math.ceil((end - start)/60)}분 소요됨)')
        else:
            print()
        return result
    return wrapper


#---------------클라이언트 초기화--------------------- 

client = OpenAI() # 자동으로 OPENAI_API_KEY가 할당된다

#-------------------------------------------------

#---------------------OpenAI API 호출 함수------------------------
@timer
def call_openai_api(prompt_text: str) -> Optional[str]:
    """
    OpenAI API를 사용합니다.
    """

    response = client.responses.create(
    model='gpt-5-mini-2025-08-07',
    input=[
    {
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": prompt_text
        }
      ]
    }
    ],
    reasoning={
        "summary": "auto",
        "effort": "low"
    },
    text={
        "format": {
        "type": "text"
        }
    }
    )

    return response.output_text

#---------------------OpenAI API 호출 함수------------------------
@timer
def call_openai_api_mini(prompt_text: str) -> Optional[str]:
    """
    OpenAI API를 사용합니다.
    """

    response = client.responses.create(
    model='gpt-5-mini-2025-08-07',
    input=[
    {
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": prompt_text
        }
      ]
    }
    ],
    reasoning={
        "summary": "auto",
        "effort": "low"
    },
    text={
        "format": {
        "type": "text"
        }
    }
    )

    return response.output_text

def call_local_ai_server(LM_STUDIO_URL:str, API_KEY:str, prompt_text:str)-> str | None:
    """
    LM Studio 서버에 OpenAI 규격의 Chat Completion 요청을 보내고
    결과 문자열을 파싱하여 반환합니다.
    """
    # LM Studio 서버 주소 + OpenAI Chat Completion 
    full_url = f"{LM_STUDIO_URL}/chat/completions"
    
    #HTTP 헤더 설정 (인증 및 데이터 형식)
    headers = {
        "Authorization": f"Bearer {API_KEY}", #Bearer로 뒤의 값이 토큰임을 인식
        "Content-Type": "application/json" # JSON 형식 데이터 전송
    }

    data = {
        "model": "google/gemma-3-1b", # LM Studio에 로드된 모델 이름으로 변경 
        "messages": [
            {"role": "user", "content": prompt_text} #생성한 주체, 내용
        ],
        "temperature": 0.7, #창의성 조절(0~1)
        "max_tokens": 2048 #생성할 최대 토큰 수(변경가능)
    }
    print(f"로컬 서버({LM_STUDIO_URL})에 요청 중...")
    
    try:
        # POST 요청 전송
        response = requests.post(full_url, headers=headers, json=data)
        # HTTP 응답 코드가 200 (성공)이 아니면 예외 발생
        response.raise_for_status() 
        # 응답 받은 JSON 데이터를 파이썬 딕셔너리로 변환
        response_json = response.json()
        result = response_json['choices'][0]['message']['content']
        result = result.replace("```","").replace('json',"").strip()

        return result
    # --- 예외 처리 ---
    except requests.exceptions.RequestException as e:  #api 통신 오류 
        print(f"\n--- API 통신 오류 발생 ---")
        return None
    except KeyError:
        print(f"\n--- 응답 파싱 오류 발생 ---")
        return None

# # --- 함수 사용 예시 -----------------
# user_prompt = input("AI에게 보낼 프롬프트를 입력하세요: ")
# result = call_local_ai_server(LM_STUDIO_URL, API_KEY, user_prompt)

# if result: #결과가 None이 아닐 경우
#     print("\n--- 로컬 서버 응답 문자열 ---")
#     print(result)
# #--------------------------------------


#---------------------Google GenAI API 호출 함수------------------------
def call_google_genai_api(api_key: str, prompt_text: str) -> Optional[str]:
    """
    Google GenAI API에 콘텐츠 생성(Generate Content) 요청을 보내고
    결과 문자열을 파싱하여 반환합니다.
    """
    try:
        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_text,
            config={
                "temperature": 0.7, 
                "max_output_tokens": 2048 
            }
        )
        
        ai_response_string = response.text
        return ai_response_string
        
    except errors.APIError as api_e:
        print(f"\n--- Google GenAI API 오류 발생 (APIError): {api_e} ---")
        return None
        
    except Exception as e:
        print(f"\n--- Google GenAI API 통신 오류 발생 (기타): {e} ---")
        return None

# # --- 함수 사용 예시 -----------------
'''
user_prompt = input("AI에게 보낼 프롬프트를 입력하세요: ")
result = call_google_genai_api(API_KEY, user_prompt)
if result: #결과가 None이 아닐 경우
    print("\n--- Google GenAI API 응답 문자열 ---")
    print(type((result)))
    print(result)
else:
    print("Google GenAI API 호출에 실패했습니다.")
'''


if __name__ == '__main__': # OpenAI API 테스트 용
    print(call_openai_api("API 테스트입니다: 안녕 너는 누구야?"))

    # print(call_openai_api(build_prompt(...)))
