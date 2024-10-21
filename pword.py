### Grupo: SO-TI-04
# Aluno 1: Libero Suprani (fc62220)
# Aluno 2: Ravi Mughal (fc62504)
# Aluno 3: Ricardo Avelãs (fc62257)

import sys
from multiprocessing import Process


DEFAULT_MODE = "c"
DEFAULT_PARALLELIZATION = 1
VALID_MODES = ["c", "l", "i"]


# ex: ./pword -m c -p 1 -w exemplo ficheiro1.txt
def pword(args: list):
    mode = DEFAULT_MODE
    parallelization = DEFAULT_PARALLELIZATION
    word = ""
    
    if "-m" in args:
        mode = args[args.index("-m")+1]
        if mode not in VALID_MODES:
            raise Exception("Invalid mode given. Valid arguments are: c|l|i")
        
    if "-p" in args:
        parallelization = args[args.index("-p")+1]
        
    if "-w" not in args:
        raise Exception("Argument -w must be provided")
    
    word = args[args.index("-w")+1]
    
    file_list = args[
        args.index(word)+1 :       
    ]

    if len(file_list) < parallelization:
        parallelization = len(file_list)
        
    #TODO
    if len(file_list) == parallelization:
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
