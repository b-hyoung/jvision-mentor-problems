q = 0

for i in range(len(s)):
    if q < 0: return False
    if s[i] == '(':
        q+=1
    elif s[i] == ')':
        q-=1
if q == 0:
    return True
else:
    return False