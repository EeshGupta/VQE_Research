from qiskit import *

#String symmetry check
def symmetry(string):
    '''
    Given an input string (of 0s and 1s, even length), checks if first half of string
    is equivalent to second half of string
    '''
    n = int(len(string)/2)
    
    for i in range(n):
        f = string[i]
        s = string[n+i]
        
        if (f!=s):
            return False
    return True



def prepare_circuit(circ):
    '''
    Given a circuit, prepare for readout error mitigation by addition of ancilla qubits and measurement gates
    '''
    #adding qubits and c bits
    q = circ.num_qubits
    total_qubits = 2*q
    anc = QuantumRegister(q, 'ancilla')
    anc_meas = ClassicalRegister(total_qubits, 'anc_meas')
    circ.add_register(anc)
    circ.add_register(anc_meas)
    
    #Cnot gates
    for i in range(q):
        circ.cx(i, q+i)
    
    #adding measurement gates
    for i in range(2*q):
        circ.measure(i, i)
    return circ

def modify_counts(counts, shots):
    '''
    Getting rid of non-symmetric counts (1st half doesnt match 2nd half i.e. '0100') and then cutting keys by half
    '''
    keys = counts.keys()
    n_counts = {}
    for key in keys:
        if (symmetry(key)):
            k = int(len(key)/2)
            n_counts[key[:k]] = counts[key]
    
    #resizing shots for each count
    
    ##calcuating total shots
    mod_shots = 0
    n_keys = n_counts.keys()
    for key in n_keys:
        mod_shots+= n_counts[key]
    
    ##resizing now
    for key in n_keys:
        old_shots= n_counts[key]
        n_counts[key] = int((old_shots/mod_shots)*shots)
        
    return n_counts
        