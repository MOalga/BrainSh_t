import sys
import re

bf_chars = r'+-<>,.[]'
alphanum = r'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_0123456789'

def delete_blanks(s):
    """空白・タブ・改行を消す"""
    for ch in (' ','\n','\t'):
        s = s.replace(ch,'')
    return s

def make_func_list(code):
    funcs0 = code.split('$')[1:]
    funcs1 = []
    for i in range(len(funcs0)):
        funcs1.append(funcs0[i].split(':')) 
    funcs2 = []
    for i in range(len(funcs1)):
        funcs2.append(funcs1[i][0].split('\''))
    func_list = []
    for i in range(len(funcs1)):
        func_list.append([funcs2[i][0],funcs2[i][1:],funcs1[i][1]])
    return func_list

def translate(func_list):
    i = 0
    for fc in range(len(func_list))[::-1]:
        func = func_list[fc]
        code = func[2]
        while i < len(code):
            print(code)
            if code[i] in bf_chars:
                i += 1
            elif code[i] == '{':
                blanket_count = 1
                for j in range(i+1,len(code)):
                    if code[j] == '{':
                        blanket_count += 1
                    elif code[j] == '}':
                        blanket_count -= 1
                        if blanket_count == 0:
                            break
                rep = code[i+1:j]
                for k in range(j+1,len(code)):
                    if code[k] not in '0123456789':
                        break
                num = int(code[j+1:k])
                newcode = rep * num
                code = str(code[:i] + newcode + code[k:])
                func_list[fc][2] = code
            elif code[i] == '/':
                for j in range(i+1,len(code)):
                    if code[j] not in alphanum:
                        break
                for k in range(j,len(code)):
                    if code[k] not in '\'0123456789':
                        break
                args = code[j:k].split("\'")
                args = list(filter(lambda x: x!='',args))
                func_name = code[i+1:j]
                for fnum in range(len(func_list)):
                    if func_list[fnum][0] == func_name:
                        break
                newcode = func_list[fnum][2]
                for a in range(len(func_list[fnum][1])):
                    newcode = newcode.replace('}'+func_list[fnum][1][a],'}'+args[a])
                    newcode = newcode.replace('\''+func_list[fnum][1][a],'\''+args[a])
                code = str(code[:i] + newcode + code[k:])
                func_list[fc][2] = code
    for main_id in range(len(func_list)):
        if func_list[main_id][0] == '':
            break
    return func_list[main_id][2]


def run(code):
    stack = []
    jump = [-1]*len(bf_code)
    for i in range(len(bf_code)):
        if bf_code[i] == '[':
            stack.append(i)
        if bf_code[i] == ']':
            j = stack.pop()
            jump[i] = j
            jump[j] = i
    memory = [0]*10000
    input_buff = []
    pc = pp = 0
    while pc < len(code):
        if code[pc] == '+':
            memory[pp] = (memory[pp]+1)&255
        if code[pc] == '-':
            memory[pp] = (memory[pp]-1)&255
        if code[pc] == '>':
            pp+=1
        if code[pc] == '<':
            pp-=1
        if code[pc] == '[':
            if memory[pp] == 0:
                pc = jump[pc]
        if code[pc] == ']':
            if memory[pp] != 0:
                pc = jump[pc]
        if code[pc] == '.':
            print(chr(memory[pp]), end='')
            sys.stdout.flush()
        if code[pc] == ',':
            if len(input_buff) == 0:
                input_buff += str(input())
            memory[pp] = ord(input_buff.pop(0))
        pc+=1
    print()


# ファイルを開く
filename = sys.argv[1]
f = open(filename, 'r')

code = f.read()        # ファイルを文字列として読み込む
code = delete_blanks(code)
func_list = make_func_list(code)        # 関数のリストを作る
#check_list(func_list)       # リストの整合性を確認
bf_code = translate(func_list)   # brainf*ckのコードに翻訳する

run(bf_code)