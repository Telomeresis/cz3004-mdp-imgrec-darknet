import os
from multiprocessing import Process


def script1():
    os.system("mdp_1.py")

def script2():
    os.system("mdp_2.py")

def script3():
    os.system("mdp_3.py")


if __name__ == '__main__':
    p1 = Process(target=script1)
    p2 = Process(target=script2)
    p3 = Process(target=script3)

    p1.start()
    p2.start()
    p3.start()
    p1.join()
    p2.join()
    p3.join()
