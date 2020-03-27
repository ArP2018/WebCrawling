import time

from manager import ProxyManager

s = time.time()
ProxyManager.validate()
e = time.time()

print(str(e-s))
