### Grupo: SO-TI-04
# Aluno 1: Libero Suprani (fc62220)
# Aluno 2: Ravi Mughal (fc62504)
# Aluno 3: Ricardo Avelãs (fc62257)

# ex: ./pword -m c -p 1 -w exemplo ficheiro1.txt

import sys
from multiprocessing import Process

def divide_content(files: list, n_of_processes: int):
    ...


def assign_files_to_processes(files: list, n_of_processes: int):
    if n_of_processes > len(files):
        n_of_processes = len(files)
        
        
def pword(args: list):
    mode = args[0]
    n_of_processes = int(args[1])
    word = args[2]
    files = args[3:]

    if len(files) == 1 and n_of_processes > 1:
        divide_content(files, n_of_processes)
    else:
        assign_files_to_processes(files, n_of_processes)
            

def main(args):
    print('Programa: pword.py')
    print('Argumentos: ',args)
    
    pword(args)


if __name__ == "__main__":
    main(sys.argv[1:])
