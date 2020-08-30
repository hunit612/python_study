text = ['   + -- + - + -   ',
        '   + --- + - +   ',
        '   + -- + - + -   ',
        '   + - + - + - +   ']
#ord() : 문자 -> 숫자
#chr() : 숫자 -> 문자
s = [i.strip().replace(' ','').replace('+','1').replace('-','0') for i in text]

#list(map(lambda x: chr(int(x,2)), s))

def f(x):
    return chr(int(x,2))

print(''.join(list(map(f,s))))