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
process_list = []


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
    global process_list
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            n_of_lines = len(lines)
            
            if n_of_lines == 0:
                find_word_in_text(word, "", mode)
                return
            
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
                
            # passes the exact lines each process is gonna handle, based in lines_per_process
            start_pos = 0
            finish_pos = 0
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
    global process_list
    
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
    counter = 0
    
    if mode == 'c':
        # mutex start
        mutex.acquire()
        shared_counter.value += text.count(word)
        mutex.release()
        # mutex end
        return None
       
    elif mode == 'l':
        lines_found = []
        # mutex start
        mutex.acquire()    
        split_text = text.strip().split("\n")
        for line in split_text:
            if word in line:
                lines_found.append(line)   
        # increments the shared array in my_index position with the amount of lines found so far
        shared_counter[my_index] += len(lines_found)       
        mutex.release()
        # mutex end
        # return set(lines_found) //TODO tem que ver com a prof se precisa ser set ou não
        return lines_found
    
    elif mode == "i":
        mutex.acquire()
        split_text = text.strip().split()
        for w in split_text:
            if word == w:
                counter += 1
        
        # puts the counter in the queue after each file/block was analyzed    
        shared_found.put(counter)
        shared_counter[my_index] += counter
                
        mutex.release()
        return None


def find_word_in_block(word: str, block: str, mode):
    global my_index
    global shared_counter
    
    if mode != "c":
        find_my_index()
        shared_counter[my_index] = 0
        
    result = find_word_in_text(word, block, mode)
    
    if mode == "l":
        list_of_lines = []
        list_of_lines.extend(result)
        shared_found.put(list_of_lines)
    
    
def find_word_in_files(word: str, files: list, mode):
    '''
    Calls find_word_in_text for every file in files.
    '''
    global my_index
    global shared_counter
    
    if mode != "c":
        find_my_index()
        shared_counter[my_index] = 0
    
    list_of_lines = []
    
    for filename in files:
        try:
            with open(filename, 'r', encoding="utf-8") as f:
                text = f.read()
                result = find_word_in_text(word, text, mode)
                if mode == "l":
                    list_of_lines.extend(result)
        except FileNotFoundError:
            print(f"Erro! Ficheiro '{filename}' não encontrado.")
    
    # if mode is "l", put in the queue the counter after all the files were analyzed
    if mode == "l":
        shared_found.put(list_of_lines)

# --------------------------------------------------  

def signal_handler(signum, frame):
    '''
    '''
    global terminate
    terminate = True
    print(f"Sinal {signum} recebido. Encerrando processos filhos...")
    
    for child in process_list:
        if child.is_alive():
            child.terminate()
            child.join()  
            
    os.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def pword(args: list):
    global shared_found
    global shared_counter
    global n_of_processes
    
    mode = args[0]
    n_of_processes = int(args[1])
    interval = int(args[2])               
    partial_results_file = args[3]
    word = args[4]
    files = args[5:]
    
    if len(files) == 1 and n_of_processes > 1: # 1 file and multiple processes
        with open(files[0], "r") as f:
            n_of_lines = len(f.readlines())
            
            if n_of_processes > n_of_lines:
                n_of_processes = n_of_lines
                
        mutex.acquire()
        if mode == "c":
            if shared_counter == None:
                shared_counter = Value("i", 0)
        else:
            if shared_counter == None:
                shared_counter = Array("i", [-1 for i in range(n_of_processes)])
        mutex.release()
        
        divide_content(files[0], n_of_processes, word, mode)
        # TODO do something else
        
    else:
        if n_of_processes > len(files):
            n_of_processes = len(files)
            
        mutex.acquire()
        if mode == "c":
            if shared_counter == None:
                shared_counter = Value("i", 0)
        else:
            if shared_counter == None:
                shared_counter = Array("i", [-1 for i in range(n_of_processes)])
        mutex.release()
        
        assign_files_to_processes(files, n_of_processes, word, mode)    

    if mode == "l":
        all_lines_set = []
        while not shared_found.empty():
            child_line_set = shared_found.get()
            all_lines_set.extend(child_line_set)
            
        print(f"(PAI) Linhas encontradas: {len(all_lines_set)}")
        
    elif mode == "i":
        all_occurrences_counter = 0
        while not shared_found.empty():
            all_occurrences_counter += shared_found.get()
        print(f"(PAI) Todas as ocorrências: {all_occurrences_counter}")
                
                
# --------------------------------------------------   

def main(args):
    pword(args)

if __name__ == "__main__":
    main(sys.argv[1:])
