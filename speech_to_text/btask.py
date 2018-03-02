# -*- coding: utf-8 -*- #

import time
import random
from multiprocessing import Process
def piao(name):
    print('%s piao' %name)
    time.sleep(random.randrange(1,5))
    print('%s piao end' %name)

p = Process(target=piao,args=('e',)) #必须加,号

p.start()

# print('主线程')