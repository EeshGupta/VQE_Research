import qiskit
from qiskit.scheduler import measure
from qiskit.pulse.instructions import Play, Acquire
from qiskit import pulse
from qiskit.pulse import Drag


def stretchSchedule_singleQ(sched, factor, machine):
    # args:circuit in pulse form WITHOUT measurement, stretch factor
    #output: pulses stretched by thefactor
    
    instrucs = sched.instructions
    new_sched = qiskit.pulse.Schedule(name = "Schedule stretched by factor " + str(factor))
    
    #Only stretching the sample pulse, doing nothing to shiftphase, measurement,etc.
    
    for instruc_paren in instrucs:
        instruc = instruc_paren[1]
        #if drag/gaussian square ....ignore gaussian, only add drag
        if (isinstance(instruc, Play)):
            
            #print(instruc)
            
            if (isinstance(instruc.pulse, Drag)):
                drag = instruc.pulse
                ## param = {"duration": self.duration, "amp": self.amp, "sigma": self.sigma, "width": self.width}
                param = drag.parameters
                #print("Initial Param")
                #print(param)
                #print("final Param")
                #print('Duration' + str(factor*param['duration']))

                #stretching the drag pulse
                s_pulse = Drag(int(factor*param['duration']), param['amp']/factor, factor*param['sigma'], param['beta'])
                channel = instruc.channels[0]
                new_sched+= pulse.Play(s_pulse, channel)
        
        #if not acquire    
        elif ( not isinstance(instruc, Acquire)):
            new_sched+= instruc
    
    #adding measurement
    new_sched +=measure([0], machine) <<new_sched.duration   #([0], backend)
    return new_sched
#circuits ----> scaled schedules

from qiskit.compiler import schedule 
from qiskit.compiler import transpile

def Scheduler(scales, circuits, machine): 
    '''
    Input: scales and circuits to be converted to schedules and stretched
    Output: Scaled schedules corr. to circuits
    '''
    scaled_schedules = []
    for c in scales:
        scale_seeds = []
        for seed in circuits: 
            new_seed =[]
            for circ in seed: 
                circ_device = transpile(circ, machine)
                sched_circ = schedule(circ_device, machine)
                scaled_sched =  stretchSchedule_singleQ(sched_circ, c, machine)
                new_seed.append(scaled_sched)
            scale_seeds.append(new_seed)
        scaled_schedules.append(scale_seeds)
    return scaled_schedules