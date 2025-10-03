import libs.load_file as lf
import libs.datetime_utils as dt_utils

file_name = "test_data/Talk_2025.8.8 21_50-1.txt"
data = lf.load_chatlog(file_name)
talk_list = []
i = 0
for line in data:
    if dt_utils.check_datetime_format(line):
        talk_list.append(line.strip())
    elif dt_utils.delete_datetime_format(line):
        continue
    else:
        if talk_list:
            talk_list[-1] += " " + line.strip()
    i += 1

with open("temp.txt", "w", encoding="utf-8") as file:
    for line in talk_list:
        file.write(line + "\n")