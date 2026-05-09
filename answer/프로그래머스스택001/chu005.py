s = ("((((((((((()))))))))))")
answer = []

a = s.count('(')
b = s.count(')')
c = -1
d = -1
if a == b:
    for i in range(b):
        c = s.find('(', c+1)
        d = s.find(')', d+1)  
        if c < d:
            answer = True
        else: 
            answer = False
            break
else: answer = False
return answer