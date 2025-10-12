from libs.preprocess_utils import *

df = processing_chatlog("./test_data/Talk_2025.8.8 21_50-1.txt")

# 결과 확인
print(df.head())

# 예시 출력
df.to_csv("./temp.csv", index=False, encoding="utf-8-sig")