import numpy as np
import csv
from comp_rates_config import RECENT_PHASE

char_data = {}
print_data = []

# with open("char_data.csv", 'r') as f:
with open("../mihomo/output1_char.csv", 'r', encoding='UTF8') as f:
    reader = csv.reader(f, delimiter=',')
    print_data += [next(reader)]
    char_data_temp = list(reader)
with open("../data/raw_csvs_real/" + RECENT_PHASE + "_char.csv", 'r') as f:
    reader = csv.reader(f, delimiter=',')
    headers = next(reader)
    char_data_temp += list(reader)
    for line in char_data_temp:
        if line[0] not in char_data:
            char_data[line[0]] = {}
        if line[2] not in char_data[line[0]]:
            char_data[line[0]][line[2]] = [line[3], line[4], line[5], line[6], line[7], line[8]]
for uid in char_data:
    for char in char_data[uid]:
        print_data += [[uid, "2.2b", char] + char_data[uid][char]]

csv_writer = csv.writer(open("../data/raw_csvs_real/" + RECENT_PHASE + "_charnew.csv", 'w', newline=''))
csv_writer.writerows(print_data)
