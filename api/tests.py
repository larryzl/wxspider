from django.test import TestCase

# Create your tests here.


import collections

dd = {'banana': 3, 'apple': 4, 'pear': 1, 'orange': 2}
# 按key排序
kd = collections.OrderedDict(sorted(dd.items(), key=lambda t: t[0]))
print(kd)
vd = kd

print(vd)
