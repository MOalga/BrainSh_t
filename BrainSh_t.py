import sys
import re

bf_chars = r'+-<>,.[] '
bs_chars = r'{}_0123456789'

def change_into_blanks(s):
    """空白・タブ・改行を空白にする"""
    s = re.sub(r'\t+',' ',s)
    s = re.sub(r'\n+',' ',s)
    s = re.sub(r'\s+',' ',s)
    return s

def delete_blanks(s):
    """空白・タブ・改行を消す"""
    for ch in (' ','\n','\t'):
        s = s.replace(ch,'')
    return s

def m1_to_inf(n):
    return sys.maxsize if n == -1 else n

def make_func_list(code):
    """(関数名,引数名,実装) を要素とするリストを作る"""
    i = 0
    j = 0
    func_list = []
    i = code.find('$')        # 最初の'$'の位置
    while i < len(code):
        # 関数名の取得
        j = min(m1_to_inf(code.find('_',i+1)),m1_to_inf(code.find(':',i+1)))
        func_name = code[i+1:j]
        i = j
        # 引数名リストの取得
        arg_names = []
        while code[i]=='_':
            j = min(m1_to_inf(code.find('_',i+1)),m1_to_inf(code.find(':',i+1)))
            arg_names.append(code[i+1:j])
            i = j
        # 実装の取得
        l = code.find('$',i+1)
        j = l if l!=-1 else len(code)
        func_code = code[i+1:j]
        i = j
        # リストへの追加
        func_list.append([func_name,arg_names,func_code])
    return func_list

def check_list(func_list):
    """リストの整合性を確認する"""
    for func in func_list:
        s = func[2]
        for ch in bf_chars:
            s = s.replace(ch,' ')
        for ch in bs_chars:
            s = s.replace(ch,' ')
        for func2 in sorted(func_list[:func_list.index(func)+1],key = lambda f : len(f[0]), reverse=True):
            s = s.replace(func2[0],' ')
        for arg in func[1]:
            s = s.replace(arg,' ')
        s = re.sub(r'\s+',' ',s)        # 連続した空白文字をまとめる
        if s != ' ':
            ls = list(filter(lambda a: a != '', s.split()))
            raise Exception('undefined: {0}'.format(ls))
        if not func[0].isupper() and func[0]!='$':
            raise Exception('characters used in function.name must be UPPER CASE. {0}'.format(func[0]))
        for a in func[1]:
            if not a.islower():
                raise Exception('characters used in argment.name must be lower case. {0}'.format(a))
    
def translate(func_list):
    i = 0
    for fc in range(len(func_list))[::-1]:
        func = func_list[fc]
        code = func[2]
        while i < len(code):
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
                num = int(code[j+1:k])      # '[0-9]+[a-z,A-Z]+{' エラー未考慮
                code = str(code[:i] + (rep*num) + code[k:])
                func_list[fc][2] = code
            elif code[i].isalpha():
                head = i        # 位置を記録
                for j in range(i+1,len(code)):
                    if (j >= len(code)) or (code[j] in bf_chars) or (code[j] in bs_chars):
                        break
                func_name = code[i:j]
                i = j
                arg_val = []
                while code[i]=='_':
                    for j in range(i+1,len(code)):
                        if (j >= len(code)) or (code[j] not in '0123456789'):
                            break
                    arg_val.append(code[i+1:j])
                    i = j
                for func_id in range(len(func_list)):
                    if func_list[func_id][0] == func_name:
                        break
                # 関数に代入
                newcode = func_list[func_id][2]
                for arg_c in range(len(func_list[func_id][1])):
                    newcode = newcode.replace(func_list[func_id][1][arg_c],arg_val[arg_c])
                code = str(code[:head] + newcode + code[i:])
                func_list[fc][2] = code
                i = head

    for main_id in range(len(func_list)):
        if func_list[main_id][0] == '$':
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
code = change_into_blanks(code)        # 空白・タブ・改行を消す
func_list = make_func_list(code)        # 関数のリストを作る
check_list(func_list)       # リストの整合性を確認
bf_code = delete_blanks(translate(func_list))   # brainf*ckのコードに翻訳する

run(bf_code)