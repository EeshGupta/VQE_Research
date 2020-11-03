import math
from qiskit import QuantumCircuit
import numpy as np

def splitter(word): 
    return [char for char in word] 


def PiReader(string):
    import math
    '''
    Converts symbol experession to numerical answer
    
    Assumption: should not contain decimal
    '''
    
    #null case 
    if string == "0" or string == "0.0": 
        return 0
    
    temp = []
    expression = 1
    
    arry = splitter(string)
    i = 0
    
    while (i<len(arry)): 
        element = arry[i]

        #number
        if element.isdigit():
            
            number = int(element)
            i+=1

            expression*=number
            
        #negative sign 
        elif element == '-':
            expression *= -1
            i+=1
            
        #pi 
        elif element == 'p':
            expression *= math.pi
            i+=2   #skip the 'i'
            
        #division sign
        elif element == "/": 
            expression/= int(arry[i+1])
            i+=2
            
        #do nothing if mult sign
        elif element == "*":
            expression = expression
            i+=1
        else:
            print('Erront in parsing angle.... char is ' + element)
            expression*=1
            i+=1

    return expression

def u3PairAdder(orig_gate_str, barrier): 
    """
    Input: a qasm string corresponding to a gate
    Output: a pair of gates in qasm string representation to amplify error in the given gate by factor of 3
    """
    # Converting the gate string to array 
#     print('original string is ' + orig_gate_str)
    ##break up the string 
    strings = orig_gate_str.split("(")
    temp =[]
    for string in strings: 
        temp = temp + string.split(")")
    strings = temp 
    temp =[]
    for string in strings: 
        temp = temp + string.split(",")
    strings = temp 
#     temp = []
#     for string in strings: 
#         temp = temp + string.split("*")
    strings = temp
    
    #Obtaining all useful information 
    gate = strings[0]
    qubit = strings[4]
#     print( '---------------------------------------')
#     print ('Strings is ')
#     print(strings)
#     print('---------------------------------------')
    orig_angles = strings[1:4]
    
    #new angles 
    new_angles = orig_angles 
    
    ## U3 ^-1(  theta,  phi, lambda) = U3( theta , -pi - lambda, - pi - phi)
    
    ###Part 1: adding - pi to  - of 2nd and 3rd angle
    for i in range(1,3): 
        
        if 'pi' in new_angles[i]: 
            angle = PiReader(new_angles[i])
        else: 
            angle = float(new_angles[i])
            
            
        new_angles[i] = str(-math.pi - angle)
        
#         if new_angles[i][0] == '-': 
            
#             if new_angles[i] == '-pi': 
#                 new_angles[i] = str(-math.pi +math.pi)
#             elif new_angles[i] == '-pi/2': 
#                 new_angles[i] = str(-math.pi +(math.pi/2))
#             else:
#                 new_angles[i] = str(-math.pi +float(new_angles[i][1:]))
#         else: 
#             if new_angles[i] == 'pi': 
#                 new_angles[i] = str(-math.pi -math.pi)
#             elif new_angles[i] == 'pi/2': 
#                 new_angles[i] = str(-math.pi -(math.pi/2))
#             else:
#                 new_angles[i] = str(-math.pi+ (-1)*float(new_angles[i]))

    ###Part 2: Switching the 2nd and 3rd angles
    new_angles = [new_angles[0], new_angles[2], new_angles[1]]
            

    #creating inverted gate
    new_gate_str = gate + '(' + new_angles[0] + ',' + new_angles[1] + ',' + new_angles[2] + ')' + qubit
    
    #barrier 
    #barrier ="""barrier q[0],q[1];"""
    
    return barrier + '\n' + new_gate_str + '\n'+ barrier + '\n' + orig_gate_str + '\n' + barrier + '\n' + new_gate_str + '\n'+ barrier + '\n' + orig_gate_str + '\n' + barrier + '\n'

def cXPairAdder(orig_gate_str, barrier): 
    """
    Input: a qasm string corresponding to a gate
    Output: a pair of gates in qasm string representation to amplify error in the given gate by factor of 3
    """
    #barrier for 2 qubit circuit only
    #barrier ="""barrier q[0],q[1];"""
    
    return barrier + '\n' + orig_gate_str +'\n' +barrier + '\n'+orig_gate_str + '\n' + barrier + '\n' + orig_gate_str +'\n' +barrier + '\n'+orig_gate_str + '\n' + barrier + '\n'

def GateInsertion(circ, c): 
    """
    Input: a circuit (with u3 and cnot gates only), and scaling factor
    Output: circuit with amplified error using gate insertion
    """
    import numpy as np
    import random
    #for creating barriers!
    n_qubits = circ.num_qubits
    qubit_str = ""
    if (n_qubits == 1): qubit_str= "qr[0]"
    elif (n_qubits == 2): qubit_str= "q[0],q[1]"
    
    barrier = "barrier " + qubit_str + ";"
    
    #iterating over the circuit in string representation
    
    
    newqasm_str=""
    circ_str=circ.qasm()
#     print("Converting circ to string using Qasmstring function in Quantum Ciruit")
#     print(circ_str)
    
    qregname=circ.qregs[0].name
    global debug 
    debug = []
    
    for line in iter(circ_str.splitlines()):
        
        if line.startswith('cx') or line.startswith('u3'):
            
            #adding the original first
            newqasm_str+= barrier + '\n' + line + '\n'+ barrier + '\n'
            
            #doing a toss to see number of identities:
            n_ident_mean= (c-1)/2
            n_ident = np.random.poisson(n_ident_mean, 1)[0]
            debug.append(n_ident)
            
            #adding those identities
            for i in range(n_ident):  
                
                if line.startswith('cx'):
                    newqasm_str += cXPairAdder(line, barrier)
                else:
                    newqasm_str += u3PairAdder(line, barrier)
        else:
            newqasm_str+=line+"\n"
#     print("------------------------------------")
#     print("passing a modified qasm string to from_qasm_str method of quantum circuit")
#     print(newqasm_str)https://notebooks.quantum-computing.ibm.com/user/5d10d2fd29bc3e00182cd85c/notebooks/Gate%20Insertion%20with%20Poisson%20.ipynb#

    circo=QuantumCircuit().from_qasm_str(newqasm_str)
    
    return circo 

def GateInserter(scales, circuits):
    scaled_circuits = []   # buckets are scales, each contains seeds which contain circs
    for c in scales:
        scale_seeds = []
        for seed in circuits: 
            new_seed =[]
            for circ in seed: 
                scaled_circ =  GateInsertion(circ,c)
                new_seed.append(scaled_circ)
            scale_seeds.append(new_seed)
        scaled_circuits.append(scale_seeds)
    return scaled_circuits