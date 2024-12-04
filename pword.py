### Grupo: SO-TI-04
# Aluno 1: Libero Suprani (fc62220)
# Aluno 2: Ravi Mughal (fc62504)
# Aluno 3: Ricardo Avelãs (fc62257)

# ex: ./pword -m c -p 1 -w exemplo ficheiro1.txt

import sys
from multiprocessing import Process, Value, Array, Queue, Lock, Semaphore

import signal, time, sys, os

mutex = Lock()
shared_counter = None
shared_found = Queue()
my_index = -1

class FileObj:
    '''
    Representation of a file.
    '''
    def __init__(self, name, size) -> None:
        self.name = name
        self.size = size
        

def divide_content(filename: str, n_of_processes: int, word: str, mode: str):
    '''
    Divides the content of a given file between n-processes.
    
    Requires: 
    - filename, word, mode str
    - n_of_processes int
    
    Ensures:
    - Creation and start of n-processes, where each process deals with a part of the content of the file.
    '''
    
    global shared_counter
    global my_index
    process_list = []
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            n_of_lines = len(lines)
            
            if n_of_lines == 0:
                find_word_in_text(word, "", mode)
                return
            
            if n_of_processes > n_of_lines:
                n_of_processes = n_of_lines
            
            # after knowing exatcly the number of processes that there will be, creates the shared_counter depending on the mode chosen
            mutex.acquire()
            if shared_counter == None:
                if mode == "c":
                    shared_counter = Value("i", 0)
                else:
                    shared_counter = Array("i", [-1 for i in range(n_of_processes)])
                    find_my_index()
                    shared_counter[my_index] = 0
            mutex.release()
            
            division = n_of_lines // n_of_processes
            rest = n_of_lines % n_of_processes

            lines_per_process = [0 for i in range(n_of_processes)]
        
            # this cicle assigns the amount of lines each process is gonna receive,
            # incrementing to each position of the array the result of division 
            # (and +1 while there is rest available)
            pos = 0
            for i in range(0, n_of_lines-rest, division):
                lines_per_process[pos] += division
                if rest > 0:    
                    lines_per_process[pos] += 1
                    rest -= 1
                
                pos += 1
                if pos == n_of_processes:
                    pos = 0
                
            start_pos = 0
            finish_pos = 0
            # passes the exact lines each process is gonna handle, based in lines_per_process
            for i in range(n_of_processes):
                finish_pos = start_pos + lines_per_process[i]
                lines_args = lines[start_pos:finish_pos]
                
                text_block = ""
                for line in lines_args:
                    text_block += line
                
                p = Process(target=find_word_in_block, args=(word, text_block, mode))
                process_list.append(p)
                
                p.start()
                
                start_pos = finish_pos
                
            for p in process_list:
                p.join()
    except FileNotFoundError:
        print(f"Erro! Ficheiro '{filename}' não encontrado.")    
   
                     
def assign_files_to_processes(files: list, n_of_processes: int, word: str, mode: str):
    '''
    Divides the files among n-processes.
    
    Requires:
    - files list
    - n_of_processes int
    - word, mode str
    
    Ensures:
    - Creation and start of n-processes, where each process deals with 1 or more files.
    '''
    
    def sum_files_sizes(files_list: list):
        '''
        Sums the sizes of the files in a group. 
        
        Requires:
        - files_list list
        
        Returns: 
        Total amount of lines in list of files. If files_list is empty, returns 0. 
        '''
        res = 0
        if len(files_list) == 0:
            return 0
        for f in files_list:
            res += f.size
        return res
    
    global shared_counter
    global my_index
    process_list = []

    if n_of_processes > len(files):
        n_of_processes = len(files)
    
    # after knowing exatcly the number of processes that there will be, creates the shared_counter depending on the mode chosen
    mutex.acquire()
    if shared_counter == None:
        if mode == "c":
            shared_counter = Value("i", 0)
        else:
            shared_counter = Array("i", [-1 for i in range(n_of_processes)])
            find_my_index()
            shared_counter[my_index] = 0
    mutex.release()
    
    # creates and runs each process passing exactly 1 file to it
    if n_of_processes == len(files):
        for i in range(n_of_processes):
            p = Process(target=find_word_in_files, args=(word, [files[i]], mode))
            process_list.append(p)
            p.start()
        for p in process_list:
            p.join()
    else:
        # converts each file to a FileObj
        file_obj_list = []  
        for i, filename in enumerate(files):
            try:
                with open(filename, 'r', encoding="utf-8") as f:               
                    lines = f.readlines()
                    file_obj_list.append(FileObj(name=filename, size=len(lines)))
            except FileNotFoundError:
                print(f"Erro! Ficheiro '{filename}' não encontrado.")
        file_group_list = [[] for i in range(n_of_processes)] # [[], []]
        
        # this loop will find the group of files that has the least amount of total lines at the moment
        # and will assign a file to this group
        for file_obj in file_obj_list: 
            lowest_index = 0
            lowest_sum = sum_files_sizes(file_group_list[0])
            
            # finds the group of files that has the least amount of lines combined 
            for i, file_group in enumerate(file_group_list):
                if sum_files_sizes(file_group) < lowest_sum:
                    lowest_sum = sum_files_sizes(file_group)
                    lowest_index = i
            
            # appends the current file to the group with the lowest amount of lines combined
            file_group_list[lowest_index].append(file_obj)
            
        # converts the file_objects in the groups to their respective names
        files_sub_list = [[f.name for f in file_group] for file_group in file_group_list]
        
        for sub_list in files_sub_list:
            p = Process(target=find_word_in_files, args=(word, sub_list, mode))
            process_list.append(p)
            p.start()
        for p in process_list:
            p.join()
  
    
def find_my_index():
    """
    Finds the index of shared_found Array that this current Process must use (which is the first with the value -1), changing the value
    of global variable my_index to this index
    """
    global my_index
    
    found_my_index = False
    my_index = 0
    my_index_iterator = 0
    while not found_my_index:
        found_my_index = True if shared_counter[my_index_iterator] == -1 else False
        my_index = my_index_iterator 
        my_index_iterator += 1
        
            
def find_word_in_text(word: str, text: str, mode): 
    '''
    Finds a given word in a given text.
    
    Requires:
    - word, text, mode str
    
    Ensures:
    - Print of the amount of occurrences of the word in the text, depending of the mode chosen. 
    '''
    global shared_counter
    global shared_found
    global my_index
    
    if mode == 'c':
        # mutex start
        mutex.acquire()
        shared_counter.value += text.count(word)
        mutex.release()
        # mutex end
        print(f"Número de ocorrências: {shared_counter.value}")
        
    elif mode == 'l':
        lines_found = set()
        # mutex start
        mutex.acquire()    
        split_text = text.strip().split("\n")
        for line in split_text:
            if word in line:
                lines_found.add(line)      
        # increments the shared array in my_index position with the amount of lines found so far
        shared_counter[my_index] += len(lines_found)         
        mutex.release()
        # mutex end
        print(f"Número de ocorrências (linhas): {shared_counter[my_index]}")
    
    elif mode == "i":
        mutex.acquire()
        split_text = text.strip().split()
        for w in split_text:
            if word == w:
                shared_counter[my_index] += 1
            mutex.release()
        print(f"Número de ocorrências: {shared_counter[my_index]}")

def find_word_in_block(word: str, block: str, mode):
    global my_index
    
    find_word_in_text(word, block, mode)
    
    # if mode is "l", put in the queue the counter after the block was analyzed
    if mode == "l" or mode == "i":
        shared_found.put(shared_counter[my_index])
        
    
def find_word_in_files(word: str, files: list, mode):
    '''
    Calls find_word_in_text for every file in files.
    '''
    global my_index

    for filename in files:
        try:
            with open(filename, 'r', encoding="utf-8") as f:
                # print(f"\n### Ficheiro '{file}' ###")
                text = f.read()
                find_word_in_text(word, text, mode)
                
                # if mode is "i", put in the queue the counter after each file was analyzed    
                if mode == "i":
                    shared_found.put(shared_counter[my_index])
        except FileNotFoundError:
            print(f"Erro! Ficheiro '{filename}' não encontrado.")
    
    # if mode is "l", put in the queue the counter after all the files were analyzed
    if mode == "l":
        shared_found.put(shared_counter[my_index])
# --------------------------------------------------  
            
def pword(args: list):
    global shared_found
    
    mode = args[0]
    n_of_processes = int(args[1])
    # interval = args[2]                //TODO implementar essas paradas pra poder descomentá-las
    # parcial_results_file = args[3]
    # word = args[4]
    # files = args[5:]
    word = args[2]
    files = args[3:]
    
    if len(files) == 1 and n_of_processes > 1: # 1 file and multiple processes
        divide_content(files[0], n_of_processes, word, mode)
    else:
        assign_files_to_processes(files, n_of_processes, word, mode)    

    while shared_found.full
        print(shared_found.get())
# --------------------------------------------------   

def main(args):
    pword(args)

if __name__ == "__main__":
    main(sys.argv[1:])
