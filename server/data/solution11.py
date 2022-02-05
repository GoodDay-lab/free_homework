import sys
import os.path


def human_read_format(size: int):
    format_l = ['Б', 'КБ', 'МБ', 'ГБ']
    indicator = len(format_l)
    while indicator >= 0:
        if bool(indicator) * 1024 ** indicator <= size:
            break
        indicator -= 1
    return str(round(size / 1024 ** indicator)) + format_l[indicator]


def get_files_sizes():
    for path, _, files in os.walk():
        print(path, '----------------------')
        for file in files:
            print(file, end=' ')
            print(human_read_format(os.path.getsize(os.path.join(path, file))))
    
    
get_files_sizes()