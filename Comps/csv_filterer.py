import csv
import json
import re
from composition import Composition

uids = {}

# Load all the character names
with open('../data/characters.json') as char_file:
    CHARACTERS = json.load(char_file)

def main():
    stats = open("../data/raw_csvs/moc.csv")
    reader = csv.reader(stats)
    col_names = next(reader)
    full_table = []
    for line in reader:
        full_table.append(line)

    all_comps = form_comps(col_names, full_table, phase)
    write_comps(all_comps)

def bool_chars(row, cols, start, end):
    comp = []
    for i in range(start, end):
        if row[i] == '1':
            comp.append(cols[i])
    return comp

def four_chars(row, cols):
    return [row[i] for i in cols]

def form_comps(col_names, table, patch):
    comps = []
    round_num = col_names.index('round_num')
    star_num = col_names.index('star_num')
    room = col_names.index('node')
    floor = col_names.index('floor')
    indexes = [col_names.index("ch1"), col_names.index("ch2"),
               col_names.index("ch3"), col_names.index("ch4")]
    for row in table:
        comp_chars = four_chars(row, indexes)
        for char in comp_chars:
            if char not in CHARACTERS.keys() and char != "":
                print("bad char name: " + char)
        comps.append(Composition(row[0], comp_chars, patch, row[round_num], row[star_num],
                                str(re.findall('[0-9]+', row[floor])[0]) + "-" + str(row[room]), False))
    return comps

def write_comps(comps):
    with open('../data/compositions.csv', 'w') as out_file:
        if out_file.tell() == 0:
            out_file.write("uid,phase,room,round_num,star_num," + ",".join(list(CHARACTERS.keys())) + "\n")
        for comp in comps:
            out_file.write(comp_string(comp))

def comp_string(comp):
    builder = comp.player + "," + comp.phase + "," + comp.room + "," + str(comp.round_num) + "," + str(comp.star_num)
    for char in CHARACTERS:
        if comp.char_presence[char]:
            builder += ",1"
        else:
            builder += ",0"
    return builder + "\n"

if __name__ == '__main__':
    main()
