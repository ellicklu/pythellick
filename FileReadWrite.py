import re
def readABlock():
    rstr = r"[\s\/\\\:\*\?\"\<\>\|]"
    idx = 0
    title = 'FirstSample'
    cached_non_empty_line = ''
    filetoappend = open('D:\\projects\\leetcodetmp.txt', 'w', encoding='UTF-8')
    current_file_suffix = 'txt'
    with open('D:\\projects\\leetcode100.txt', 'r', encoding='UTF-8') as f:
        for line in f.readlines():
            str_line = str(line.strip())
            if len(str_line) == 0:
                continue
            if str(str_line).startswith('Description:'):
                idx = idx+1
                title = re.sub(rstr, '_', cached_non_empty_line)
                print('#'+title)
                filetoappend.write('\r\n}\r\n');
                filetoappend.close()
                filetoappend = open('D:\\projects\\'+title+'.txt', 'w', encoding='UTF-8')
                current_file_suffix = 'txt'
                filetoappend.write(cached_non_empty_line)
                yield 0
            elif str(str_line).startswith('/**') and current_file_suffix == 'txt':
                filetoappend.close()
                class_name = re.sub('\\S\\d', '', title)
                filetoappend = open("D:\\projects\\"+class_name+'.java', 'w', encoding='UTF-8')
                current_file_suffix = 'java'
                filetoappend.write('public class ' + class_name + '{\r\n')
            filetoappend.write('\r\n' + str_line + '\r\n')
            cached_non_empty_line = line
    return 'done'

block = readABlock()
for i in range(1,15):
    next(block)