### Grupo: SO-TI-04
# Aluno 1: Libero Suprani (fc62220)
# Aluno 2: Ravi Mughal (fc62504)
# Aluno 3: Ricardo Avelãs (fc62257)

import sys
from multiprocessing import Process

# ex: ./pword -m c -p 1 -w exemplo ficheiro1.txt
def pword(args: list):
    mode = args[0]
    parallelization = int(args[1])
    word = args[2]
    files = args[3:]

    if len(files) < parallelization:
        parallelization = len(files)
        
    #TODO
    if len(files) == parallelization:
        pass
    
    #TODO
    else:
        pass
    


def main(args):
    print('Programa: pword.py')
    print('Argumentos: ',args)
    
    pword(args)


if __name__ == "__main__":
    main(sys.argv[1:])
