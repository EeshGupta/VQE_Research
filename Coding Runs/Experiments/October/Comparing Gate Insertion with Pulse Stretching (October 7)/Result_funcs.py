import numpy as np
from qiskit.tools.monitor import job_monitor
from qiskit import QuantumCircuit, execute, Aer, IBMQ, IBMQ

def countsToProb(counts, sample_size): 
    '''
    Input: counts 
    Output: prob 
    '''
    return (counts['0']/sample_size)

def averagingSeeds(seeds):
    '''
    Input: list of seed probs - buckets are seeds, each with prob for particular gate length
    Output: a single list of probs of gate lengths (averaging across all seeds)
    '''
    gate_lengths = len(seeds[0])
    n_seeds = len(seeds)
    
    
    result =[] # contain averaged out probs of gate lengths
    
    for i in range(gate_lengths):
        summ = 0
        for j in range(n_seeds): 
            summ += seeds[j][i]
        summ/= n_seeds 
        result.append(summ)
        
    return result

def addDicts(listy): 
    '''
    Input: list of dicts of counts 
    Output: combining all dicts into one dict, returning that
    '''
    keys = ['0', '1']
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
    Input: List of circuits organized as follows: scales ---> seeds-----> circuits
    Output: List of counts in that same order after executing all circuits at synchronously
    '''
    n_scales = len(circuits)
    n_seeds = len(circuits[0])
    n_gate_lengths = len(circuits[0][0])
    
    #collecting all circuits
    experiments = []
    
    for i in range(n_scales): 
        for j in range(n_seeds):
            for k in range(n_gate_lengths): 
                experiments.append(circuits[i][j][k])
                
    #Executing all experiments 
    counts = []
    while (sample_size !=0):
        sample_counts = []
        if (sample_size>8192):
            job = execute(experiments, backend, shots=8192)
            job_monitor(job)
            result = job.result()
            sample_counts = result.get_counts()
            sample_size-=8192
        else: 
            job = execute(experiments, backend, shots=sample_size)
            job_monitor(job)
            result = job.result()
            sample_counts = result.get_counts()
            sample_size = 0
        
        if(len(counts)!=0):
            #adding up results of this with all 
            new_counts = []
            for i in range(len(counts)): 
                dicty = addDicts([counts[i], sample_counts[i]])
                new_counts.append(dicty)
            counts = new_counts
        else: 
            counts = sample_counts
    
    new_counts = []
    
    for i in range(n_scales): 
        scale_counts = []
        print('--------------------------------------------------New Scale')
        
        for j in range(n_seeds): 
            seed_counts = []
            print('----------------------New Seed')
            
            for k in range(n_gate_lengths): 
                print('-- Gate Length ')
                count  = counts[i*(n_seeds*n_gate_lengths) + j*(n_gate_lengths) + k]
                seed_counts.append(count)
            scale_counts.append(seed_counts)
        new_counts.append(scale_counts)
    
    return new_counts

def getProb(counts, samples):
    '''
    Input: Counts -- array of scale seeds, which is array of seeds which is array of gate sizes ...and sample count
    Output: Corresponding probs
    '''
    Probs = []
    for scale_seeds in counts:
        scale_probs = [] # initailly buckets are seeds
        for seed in scale_seeds: 
            seed_probs = []
            for gate_count in seed:
                #print(gate_count)
                prob= countsToProb(gate_count, samples)
                seed_probs.append(prob)
            scale_probs.append(seed_probs)
        #averaging probs across all seeds 
        scale_probs = averagingSeeds(scale_probs) #now buckets are gate length prob (bucket are scalar here)
        Probs.append(scale_probs)
    return Probs