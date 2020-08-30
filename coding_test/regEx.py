import re

p = re.compile('[a-z]')
m = p.match('a\nb')

print(m.match(''))
