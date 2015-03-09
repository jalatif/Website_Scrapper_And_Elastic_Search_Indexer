__author__ = 'manshu'

import sys
import glob
import re
from os import walk

def get_json_strings(file, lines, file_prefix):

    url = lines[0]
    title = lines[1]

    body = ""
    for bline in lines[2:]:
        body += bline + "\n"

    title = title.replace('"', '\\"')

    body = body.replace('\n', '\\n')
    body = body.replace('"', '\\"')

    first_str = "{ \"create\": { \"_index\": \"" + file_prefix + "_index\", \"_type\": \"doc\"}}"

    second_str = "{\"doc_id\": \"" + file + "\", \"url\" : \"" + url + "\", \"title\" : \"" + title + "\", \"body\" : \"" + body + "\"}"

    final_str = first_str + "\n" + second_str + "\n"
    return final_str

numbers = re.compile(r'(\d+)')
def numerical_sort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts

def list_files(file_path, file_prefix):
    # for (dirpath, dirnames, filenames) in walk(file_path):
    #     print dirpath, dirnames, filenames
    files = glob.glob1(file_path, file_prefix + "_*")
    files = sorted(files, key=numerical_sort)

    print len(files)

    new_json = open(file_prefix + ".json", "w")

    for file in files:
        lines = []
        temp_f = open(file_path + "/" + file, "r")
        for line in temp_f:
            line = line.strip()
            lines.append(line)
        temp_f.close()

        new_json.write(get_json_strings(file, lines, file_prefix))

    new_json.close()

if __name__ == "__main__":
    file_prefix = "sharma55"
    file_path = "sharma55_txt" #sys.argv[1]
    list_files(file_path, file_prefix)