from qiskit import*
import qiskit
from qiskit.compiler import transpile, assemble
from qiskit.scheduler import measure
from qiskit.pulse.instructions import Play, Acquire
from qiskit import pulse
from qiskit.pulse import Drag, Gaussian, GaussianSquare



def instruc_sorter(instrucs):
    '''
    Input: Array of instructions
    Output: Groups all same-time instrucs into smaller arrays and returns a big array containing those 
    smaller sub arrays (lol array lingo)
    
    
    Structure of instruc:
            (duration, pulse_instruction)
    '''
    big_array = []    #where all instruc arrays will be stored
    num_instrucs = len(instrucs)
    i = 0 # indexing instrucs
    while (i < num_instrucs):

        instruc = instrucs[i]
        time = instruc[0]
        array = []
        #adding in the instruction
        array.append(instruc[1])
        #appending index
        i+=1


        while(i<num_instrucs):
            instruc2 = instrucs[i]
            time2 = instruc2[0]
            if (time == time2):
                array.append(instruc2[1])
                i+=1
            else:
                break
        big_array.append(array)
    return big_array

def stretch_sub_sched(sim_pulse_array, factor):
    '''
    Input: A set of pulses happening at the same time (sim = simultaneous) and factor to be stretched by
    Output: A schedule consisting of the stretched pulses
    
    '''
    sub_sched = qiskit.pulse.Schedule()
    for instruc in sim_pulse_array:

        #anything except shift phase
        if (isinstance(instruc, Play)):

            if (isinstance(instruc.pulse, Drag)):
                drag = instruc.pulse
                ## param = {"duration": self.duration, "amp": self.amp, "sigma": self.sigma, "width": self.width}
                param = drag.parameters
                #stretching the drag pulse
                s_pulse = Drag(int(factor*param['duration']), param['amp']/factor, factor*param['sigma'] ,param['beta'] )
                channel = instruc.channels[0]
                sub_sched = sub_sched.append(pulse.Play(s_pulse, channel))

#             elif (isinstance(instruc.pulse, GaussianSquare)):

#                 gauss = instruc.pulse
#                 ## param = {"duration": self.duration, "amp": self.amp, "sigma": self.sigma, "width": self.width}
#                 param = gauss.parameters
#                 #stretching the drag pulse
#                 s_pulse = GaussianSquare(int(factor*param['duration']), param['amp']/factor, factor*param['sigma'],factor*param['width'])
#                 channel = instruc.channels[0]
#                 sub_sched = sub_sched.append(pulse.Play(s_pulse, channel))

            #if not acquire    
            elif ( not isinstance(instruc, Acquire)):
                sub_sched+= instruc
        else:
            sub_sched+= instruc
    return sub_sched

def stretcher(circ, machine, factor):
    '''
    Input: A circ (without measurement) which is to be converted to a schedule, machine to be 
    transpiled upon, and the factor to be stretched by
    Output: The stretched schedule with measurement
    '''
    num_qubits = circ.num_qubits
    circ_device = transpile(circ, machine)
    sched = schedule(circ_device, machine)
    instrucs = sched.instructions
    
    big_array = instruc_sorter(instrucs)
    stretch_sched = None
    j = 0
    
    for element in big_array: 
        sub_sched = stretch_sub_sched(element, factor)
        
        #first element
        if (j == 0):
            stretch_sched = sub_sched
            #print(stretch_sched.instructions)
            j = 1
        else:
            stretch_sched = stretch_sched.insert(stretch_sched.duration, sub_sched)
            
    #adding measurement
    qubits = [i for i in range(num_qubits)]
    stretch_sched +=measure(qubits, machine) <<stretch_sched.duration   #([0], backend)
    
    return stretch_sched

def scheduler(scales, circuits, machine):
    scaled_schedules = []
    
    for scale in scales:
        scale_schedules = []
        for circ in circuits:
            circ_ = circ.copy()
            scaled_schedule= stretcher(circ_, machine, scale)
            scale_schedules.append(scaled_schedule)
        scaled_schedules.append(scale_schedules)
    return scaled_schedules