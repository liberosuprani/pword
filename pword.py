### Grupo: SO-TI-04
# Aluno 1: Libero Suprani (fc62220)
# Aluno 2: Ravi Mughal (fc62504)
# Aluno 3: Ricardo Avelãs (fc62257)

import sys, signal, re, time
from multiprocessing import Process, Value, Array, Queue, Lock

mutex_logs = Lock()
mutex_shared_counter = Lock()

shared_counter = None
shared_found = Queue()

my_index = -1

# will store the child processes needed
process_list = []

# starts as 0, will be changed to 1 in case SIGINT is triggered
is_terminated = Value("i", 0)

is_plummer_needed = False

# data retrieved from shared_found queue
unclogged_data = []

mode = "c"
partial_results_file = ""

already_processed = Value("i", 0)
still_to_process = Value("i", 0)

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
    
    global shared_counter, my_index, process_list, is_plummer_needed, unclogged_data
    
    mutex_logs.acquire()
    still_to_process.value = n_of_processes
    mutex_logs.release()
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            n_of_lines = len(lines)
            
            if n_of_lines == 0:
                find_word(word, "", mode)
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
                
                p = Process(target=find_in_block, args=(word, text_block, mode))
                process_list.append(p)
                
                p.start()
                start_pos = finish_pos
                
            join_unclogging()
                         
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
    
    global shared_counter,my_index, process_list, is_plummer_needed, unclogged_data, already_processed, still_to_process
    
    mutex_logs.acquire()
    still_to_process.value = len(files)
    mutex_logs.release()
    
    # creates and runs each process passing exactly 1 file to it
    if n_of_processes == len(files):
        for i in range(n_of_processes):
            p = Process(target=find_in_files, args=(word, [files[i]], mode))
            process_list.append(p)
            p.start()
            
        join_unclogging()
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
            p = Process(target=find_in_files, args=(word, sub_list, mode))
            process_list.append(p)
            p.start()
            
        join_unclogging()
    
    
def join_unclogging():
    """
    Iterates over the list of processes and joins them to the parent only after the queue is free
    """
    global process_list, is_plummer_needed, unclogged_data, is_terminated
    
    for p in process_list:
        # plummer is needed when modes are either l or i
        if is_plummer_needed:
            unclogged_data.extend(call_plummer())
        p.join()
    
                     
def find_my_index():
    """
    Finds the index of shared_found Array that this current Process must use (which is the first with the value -1), changing the value
    of global variable my_index to this index and changing from -1 to 0
    """
    global my_index, shared_counter
    
    found_my_index = False
    my_index = 0
    my_index_iterator = 0
    while not found_my_index and my_index_iterator < len(shared_counter):
        found_my_index = True if shared_counter[my_index_iterator] == -1 else False
        my_index = my_index_iterator 
        my_index_iterator += 1
        
    if found_my_index:
        shared_counter[my_index] = 0
   
   
def find_lines(word: str, text: str):
    '''
    Finds a given word in a given text.
    
    Requires:
    - word, text, str
    
    Ensures:
    - a list of lines that contain the given word
    '''
    global shared_counter, shared_found, my_index

    split_text = text.strip().split("\n")
    
    # remove leading and trailing and spaces from all the lines
    split_text = [line.strip() for line in split_text]
    
    lines_containing_word = [i for i in split_text if re.search(rf"{word}", i)]

    return lines_containing_word
       
            
def find_word(word: str, text: str, mode): 
    '''
    Finds a given word in a given text.
    
    Requires:
    - word, text, mode str
    
    Ensures:
    - 
    '''
    global shared_counter, shared_found, my_index
    counter = 0
    
    if mode == 'c':
        counter = text.count(word)
        return counter
    
    elif mode == "i":
        # regex for isolated word
        counter = len(re.findall(rf"\b{word}\b", text))
        return counter

# TODO
def find_in_block(word: str, block: str, mode): 
    """
    Calls find_word for a block of text
    
    Requires: 
    - word str
    """
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    
    global my_index, shared_counter, is_terminated, shared_found, already_processed, still_to_process
    
    if is_terminated.value == 0:
        if mode != "c":
            find_my_index()
        
        list_of_results = [] 
        
        if mode == "l":
            result = find_lines(word, block)
            list_of_results.extend(result)
            mutex_shared_counter.acquire()
            shared_counter[my_index] = len(list_of_results)
            mutex_shared_counter.release()
                    
        else:
            # amount of occurrences of that word
            result = find_word(word, block, mode)
        
            if mode == "c":
                mutex_shared_counter.acquire()
                shared_counter.value += result
                mutex_shared_counter.release()
            if mode == "i":
                list_of_results.append(result)
                
                mutex_shared_counter.acquire()
                shared_counter[my_index] = sum(list_of_results)
                mutex_shared_counter.release()
                
        mutex_logs.acquire()
        already_processed.value += 1
        still_to_process.value -= 1
        mutex_logs.release()
        
    if mode != "c":
        shared_found.put(list_of_results)
 
    
def find_in_files(word: str, files: list, mode):
    '''
    Calls find_word (if mode == c or mode == l), or find_lines (if mode == l) for every file in files.
    '''
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    
    global my_index, shared_counter, is_terminated, already_processed
    
    if mode != "c":
        find_my_index()
    
    if is_terminated.value == 0:
        list_of_results = [] 
        
        for filename in files:
            if is_terminated.value == 1:
                break
            
            try:
                with open(filename, 'r', encoding="utf-8") as f:
                    text = f.read()
                    if mode == "l":
                        result = find_lines(word, text)
                        list_of_results.extend(result)
                        mutex_shared_counter.acquire()
                        shared_counter[my_index] = len(list_of_results)
                        mutex_shared_counter.release()
                    
                    else:
                        result = find_word(word, text, mode)
                    
                        if mode == "c":
                            mutex_shared_counter.acquire()
                            shared_counter.value += result
                            mutex_shared_counter.release()
                        if mode == "i":
                            list_of_results.append(result)
                            
                            mutex_shared_counter.acquire()
                            shared_counter[my_index] = sum(list_of_results)
                            mutex_shared_counter.release()           
            except FileNotFoundError:
                print(f"Erro! Ficheiro '{filename}' não encontrado.")
                
            mutex_logs.acquire()
            already_processed.value += 1
            still_to_process.value -= 1
            mutex_logs.release()

        if mode != "c":
            shared_found.put(list_of_results)
    
# --------------------------------------------------  

def terminate_early(sig, frame):
    '''
    Handles the SIGINT signal.
    '''
    global shared_found, shared_counter, is_terminated, unclogged_data
        
    is_terminated.value = 1
    
    print("Encerrando os processos filhos...")
    
    # consumes the queue
    join_unclogging()
    
    if mode != "c":
        for i in range(len(shared_counter)):
            if shared_counter[i] == -1:
                shared_counter[i] = 0
        
    if mode == "c":
        print(f"(TERMINADO) Ocorrências: {shared_counter.value}")
    
    if mode == "l":
        all_lines_set = unclogged_data  
        print(f"(TERMINADO) Linhas encontradas: {len(all_lines_set)}")
        
    elif mode == "i":
        all_occurrences = unclogged_data
        print(f"(TERMINADO) Todas as ocorrências: {sum(all_occurrences)}")
    
    sys.exit(0)
    

def call_plummer():
    """
    Runs until the shared_found queue has data, and frees it.
    
    Ensures: content in shared_found
    """
    unclogged_data_local = None
    while unclogged_data_local is None:
        if shared_found.qsize() > 0:
            unclogged_data_local = shared_found.get()
            return unclogged_data_local
       

def write_logs(file, finished=False):
    """
    Writes logs to a given file.
    """
    global time_of_start
    
    t = time.gmtime()
    current_time = time.time()*1000000 - time_of_start
    
    mutex_shared_counter.acquire()
    log_text = f"{t.tm_mday}/{t.tm_mon}/{t.tm_year}-{t.tm_hour}:{t.tm_min}:{t.tm_sec} " 
    log_text += f"{int(current_time)} " 
    log_text += f"{0 if shared_counter is None else (shared_counter.value if mode == 'c' else (sum(shared_counter[:]) if sum(shared_counter[:]) > 0 else 0))} "
    mutex_shared_counter.release()
    
    log_text += f"{already_processed.value} " 
    log_text += f"{still_to_process.value}"
    
    if finished:
        log_text += " (finished) "
   
    log_text += "\n"
   
    if file == "stdout":
        print(log_text)
    else:
        with open(file, "a") as f:
            f.write(log_text)


time_of_start = 0


def pword(args: list):
    
    global shared_found, shared_counter, n_of_processes, is_plummer_needed, unclogged_data, mode, time_of_start, partial_results_file
    
    time_of_start = time.time()*1000000
    
    mode = args[0]
    n_of_processes = int(args[1])
    interval = int(args[2])               
    partial_results_file = args[3]
    word = args[4]
    files = args[5:]
    
    # terminate_early will be called when there is a SIGINT
    signal.signal(signal.SIGINT, terminate_early)
    
    if partial_results_file != "stdout":
        f = open(partial_results_file, "w")
        f.close()
    # sets a timer that runs the function write_logs, passing partial_results_file to it, every interval
    signal.signal(signal.SIGALRM, lambda sig, frame: write_logs(partial_results_file))
    signal.setitimer(signal.ITIMER_REAL, interval, interval)
    
    # 1 file and multiple processes, has to call divide_content
    if len(files) == 1 and n_of_processes > 1: 
        with open(files[0], "r") as f:
            lines = f.readlines()
            n_of_lines = len(lines)
            
            if n_of_processes > n_of_lines:
                n_of_processes = n_of_lines
                
        mutex_shared_counter.acquire()
        if mode == "c":
            if shared_counter == None:
                shared_counter = Value("i", 0)
        else:
            if shared_counter == None:
                is_plummer_needed = True
                shared_counter = Array("i", [-1 for i in range(n_of_processes)])
        mutex_shared_counter.release()

        divide_content(files[0], n_of_processes, word, mode)
    
    # no content will be divided, assign_files_to_precesses will be called
    else:
        if n_of_processes > len(files):
            n_of_processes = len(files)
            
        mutex_shared_counter.acquire()
        if mode == "c":
            if shared_counter == None:
                shared_counter = Value("i", 0)
        else:
            if shared_counter == None:
                is_plummer_needed = True
                shared_counter = Array("i", [-1 for i in range(n_of_processes)])
        mutex_shared_counter.release()
        
        assign_files_to_processes(files, n_of_processes, word, mode)    


    if mode == "c":
        print(f"Ocorrências: {shared_counter.value}")
    
    if mode == "l":
        all_lines_set = unclogged_data  
        print(f"Linhas encontradas: {len(all_lines_set)}")
        
    elif mode == "i":
        all_occurrences = unclogged_data
        print(f"Ocorrências: {sum(all_occurrences)}")
                
    write_logs(partial_results_file, True)
# --------------------------------------------------   

if __name__ == "__main__":
    pword(sys.argv[1:])
