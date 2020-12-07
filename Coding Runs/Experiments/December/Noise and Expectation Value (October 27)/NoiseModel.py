from qiskit.providers.aer.noise import NoiseModel
from qiskit.aqua import QuantumInstance
from qiskit.providers.aer.noise import thermal_relaxation_error, ReadoutError, depolarizing_error

def generateDepolarizingError(machine, gate, qubits):
    """
    Return a depolarizing error
    """
    try:
        gate_error = machine.properties().gate_error(gate, qubits)
        error = depolarizing_error(gate_error, len(qubits))
        return error
    
    except: 
        return None
    
def generateRelaxationError(machine, gate, qubits, t1, t2, amp = 1, custom_t = False):
    """
    Return a relaxation error
    """
    if len(qubits) == 1:
        try:
            if(not custom_t):
                t1 = machine.properties().t1(qubits[0])
                t2 = min(machine.properties().t2(qubits[0]), 2*t1)
                t1 = t1/amp
                t2 = t2/amp
            gate_time = machine.properties().gate_length(gate, qubits)
            error = thermal_relaxation_error(t1, t2, gate_time)
            return error
        except:
            return None
    else:
        try:
            #setting times
            
            if(custom_t):
                t1_a = t1
                t2_a = min(t2, 2*t1)
                t1_b = t1_a
                t2_b = t2_a
            else:
                t1_a = machine.properties().t1(qubits[0])
                t2_a = min(machine.properties().t2(qubits[0]), 2*t1_a)
                t1_b = machine.properties().t1(qubits[1])
                t2_b = min(machine.properties().t2(qubits[1]), 2*t1_b)
            
            t1_a = t1_a/amp
            t2_a = t2_a/amp
            t1_b = t1_b/amp
            t2_b = t2_b/amp
            #finding gate time
            time_cx = machine.properties().gate_length(gate, qubits)
            error = thermal_relaxation_error(t1_a, t2_a, time_cx).expand(thermal_relaxation_error(t1_b, t2_b, time_cx))
            return error
        except:
            return None

def generateNoiseModel(machine, coherent = True, incoherent = False, readout = False, custom_t = False, t1 = None, t2 = None, reverse = False):
    """
    Returns a realistic copy of london noise model with custom t1, t2 times
    """
    
    #initializing noise model
    noise_thermal = NoiseModel()
    amp = 1
    
    #for every qubit (5 qubit london machine)
    for q in range(5): 
        #types of erroneous gates
        gates = [ 'u3', 'u2', 'u1', 'id']


        for gate in gates: 
            dep_error = None
            if(coherent):     
                dep_error = generateDepolarizingError(machine, gate, [q])
            rel_error = None
            if(incoherent):
                generateRelaxationError(machine, gate,[q], t1, t2, amp= amp, custom_t = custom_t)

            if(dep_error ==None and rel_error !=None):
                error_obj = rel_error
                noise_thermal.add_quantum_error(error_obj, gate, [q])

            elif(dep_error !=None and rel_error ==None):
                error_obj = dep_error
                noise_thermal.add_quantum_error(error_obj, gate, [q])

            elif(dep_error !=None and rel_error !=None):
                error_obj = dep_error.compose(rel_error)
                noise_thermal.add_quantum_error(error_obj, gate, [q])


        #2 qubit gate errors
        qubits = [i for i in range(5)]
        qubits.remove(q)
        for j in qubits:
            dep_error = None
            if(coherent):
                dep_error = generateDepolarizingError(machine, 'cx', [q,j])
            rel_error = None
            if (incoherent):
                rel_error = generateRelaxationError(machine,'cx' ,[q,j], t1, t2, amp = amp,custom_t = custom_t)

            if(dep_error ==None and rel_error !=None):
                error_obj = rel_error
                noise_thermal.add_quantum_error(error_obj, 'cx', [q,j])

            elif(dep_error !=None and rel_error ==None):
                error_obj = dep_error
                noise_thermal.add_quantum_error(error_obj, 'cx', [q,j])

            elif(dep_error !=None and rel_error !=None):
                error_obj = dep_error.compose(rel_error)
                noise_thermal.add_quantum_error(error_obj, 'cx', [q,j])
        if (readout):
            #adding the readout error 
            p1_0 = machine.properties().qubit_property(q, 'prob_meas1_prep0')[0]
            p0_1 = machine.properties().qubit_property(q, 'prob_meas0_prep1')[0]
            
            print('Original: ' + str(p1_0) + ' ' + str(p0_1))
          
            if(reverse):
                temp = p1_0
                p1_0 = p0_1
                p0_1 = temp
            print('Reverse: ' + str(p1_0) + ' ' + str(p0_1))

            matrix = [[1-p1_0, p1_0 ], [p0_1, 1-p0_1]]
            error  = ReadoutError(matrix)

            noise_thermal.add_readout_error(error, [q])
        
    return noise_thermal
    
