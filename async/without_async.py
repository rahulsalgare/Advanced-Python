import time

def fun():
    print('one')
    time.sleep(1)
    print('two')


if __name__ == '__main__':
    
    s = time.perf_counter()
    for _ in range(3):
        fun()
    
    e = time.perf_counter() - s

    print('executed in :', e)