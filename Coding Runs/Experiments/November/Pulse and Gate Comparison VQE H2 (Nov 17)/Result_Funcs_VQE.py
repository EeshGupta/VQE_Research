import numpy as np
from qiskit.tools.monitor import job_monitor
from qiskit import QuantumCircuit, execute, Aer, IBMQ, result

def fullCountSetGenerator(qubits):
    '''
    Given the number of qubits, generates a list of all possible counts. So for eg. if qubits = 2, 
    returns the list = ['00', '11', '01', '10']
    '''
    keys = ['']
    for i in range(qubits):
        new_keys = []
        for key in keys:
            new_keys.append(key + '0')
            new_keys.append(key + '1')
        keys = new_keys
    return keys

def marginalizeCounts(counts, qubits):
    '''
    Input: List of buckets each of which holds multiple dicts denoting the counts 
    Output: All those dicts marginalized...i.e. holding 2 qubit keys instead of 7 qubit ones
    '''
    qubits = [i for i in range(qubits)]
    for i in range(len(counts)):
        for j in range(len(counts[i])):
            counts[i][j] = result.marginal_counts(counts[i][j], qubits)
    return counts 

def addDicts(listy): 
    '''
    Input: list of dicts of counts 
    Output: combining all dicts into one dict, returning that
    '''
    #Determining the number of qubits
    dict_keys = (listy[0]).keys()
    for key in dict_keys:
        num_qubits = len(key)
        break;
        
    #generating the full set of keys for that many qubits    
    keys = fullCountSetGenerator(num_qubits)
    master = {}
    
    for key in keys: 
        #initializing master at that key
        master[key] = 0
        
        #now adding up all dictys[key]
        for dicty in listy: 
            try:
                master[key] += dicty[key]
            except KeyError: 
                continue
    return master

def runExperiments(circuits, backend, sample_size):
    '''
    Input: List of circuits organized as follows: scales -----> circuits of different length vectors
    Output: List of counts in that same order after executing all circuits at synchronously
    '''
    n_scales = len(circuits)
    n_gate_lengths = len(circuits[0])
    n_circuits = n_scales*n_gate_lengths
    
    #collecting all circuits into a single list
    experiments = []
    
    for i in range(n_scales):
        for j in range(n_gate_lengths): 
            experiments.append(circuits[i][j])
                
    #Executing all experiments ...if sample size>8192, this part can accomodate that case too
    total_counts = []
    while (sample_size !=0):
        this_sample_counts = []
        if (sample_size>8192):
            job = execute(experiments, backend, shots=8192)
            job_monitor(job)
            result = job.result()
            this_sample_counts = result.get_counts()
            sample_size-=8192
        else: 
            job = execute(experiments, backend, shots=sample_size)
            job_monitor(job)
            result = job.result()
            this_sample_counts = result.get_counts()
            sample_size = 0
        
        if(len(total_counts)!=0):
            #adding up results of this with all 
            new_total_counts = []
            for i in range(n_circuits): 
                dicty = addDicts([total_counts[i], this_sample_counts[i]])
                new_total_counts.append(dicty)
            total_counts = new_total_counts
        else: 
            total_counts = this_sample_counts
    
    #reorganizing counts according to how scale and gate lengths are organized
    re_org_counts = []
    
    #i denotes the scale number and j denotes the gate length index
    for i in range(n_scales): 
        scale_counts = [] 
        
        for j in range(n_gate_lengths): 
            count  = total_counts[i*(n_gate_lengths) + j]
            scale_counts.append(count)
            
        re_org_counts.append(scale_counts)
        
    re_org_counts = marginalizeCounts(re_org_counts, 2)    
    
    return re_org_counts

