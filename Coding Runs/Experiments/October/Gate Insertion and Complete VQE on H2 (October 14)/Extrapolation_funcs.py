import numpy as np


def RichardsonExtrap_Fraction(energies, scales): 
    """
    Source: Temme et Al
    Input: An array of energies scaled with different stretch factors.
    Output: Zero Error extrapolated answer
    """
    n = len(scales) - 1     # because first scale factor is going to 1 which is a trivial scaling factor
    
    #setting up all equations 
    equations = []
    for eq_num in range(n+1): 
        equation = []
        for term_num in scales: 
            term = term_num**(eq_num)
            #print(term)
            equation.append(term)
        equations.append(equation)
    #print(equations)
    
    #Now filling up equals to matrix 
    equals_to = [1]
    for i in range(1, n+1): 
        equals_to.append(0)
    #print(equals_to)
    
    #solving the system
    coeff = np.linalg.solve(equations, equals_to)
    #print(coeff)
    
    #Combine coeff with energies to get zero noise result 
    result = np.dot(coeff, energies)
    return result

def MonteCarloError(means, std_devs, scales, poly_fit = False, deg = None, sampling_size = 1000): 
    """
    Input: arrays means and standard deviations of the various scalings of noise, whether to do richardson i.e. no poly fit 
    If doing polyfit, then specify degree, sampling_size is how many times to sample from the Gaussian 
    
    Assumption: Scaled by integer values ranging from 1 to X where X>1
    
    Output: Error estimate
    """
    n = len(means)
    
    #Sampling from Gaussian for each scaling 
    all_samples = []
    debug_means = []
    for i in range(n): 
        samples = np.random.normal(means[i], std_devs[i], sampling_size)
        all_samples.append(samples)
        #for debugging
        debug_means.append(means[i] - np.mean(samples))
    #print(debug_means)
    
    #Doing Extrapolation for all sampling_size samples (1000 if set to default)
    zero_noise_energies = []
    for j in range(sampling_size): 
        energies = []
        for i in range(n): 
            energies.append(all_samples[i][j])
            
        ##Doing either richardson or funcs 
        ###Polynomial
        if poly_fit: 
            ####need the scale values: 
            ####making the function 
            param = np.polyfit(scales, energies, deg, w = [1/i for i in std_devs])
            f = np.poly1d(param)
            ####extrapolation
            result = f(0)
            zero_noise_energies.append(result)
            
        ###Richardson
        else: 
            result = RichardsonExtrap_Fraction(energies, scales)
            zero_noise_energies.append(result)
    
    #Returning error i.e. std 
    error = np.std(zero_noise_energies)
    return error

def plottingCalc(means, std_devs, scales):
    """
    Gives out data for plotting energies for extrapolation purposes
    """
    
    #highest_degree = len(means) -1
    
    #scales = [1+i*0.5 for i in range(len(means))]
    
    # Uncertainties 
    #R_uncert = MonteCarloError(means, std_devs, scales, poly_fit = False)
    param = np.polyfit(scales,means, 1)
    p = np.poly1d(param)
    poly_zero = p(0)

    
#     poly_uncerts = []
#     for i in range(1, highest_degree+1): 
#         uncert = MonteCarloError(means, std_devs, poly_fit = True, deg = i)
#         poly_uncerts.append(uncert)
    
    #O energy extrap
    #R_zero = RichardsonExtrap_Fraction(means, scales)
    poly_uncert = MonteCarloError(means, std_devs, scales, poly_fit = True, deg = 1)
    
#     poly_zero = []
#     funcs = []
#     for i in range(1,highest_degree+1): 
#         param= np.polyfit(scales, means, i, w=[1/j for j in std_devs])
#         p = np.poly1d(param)
#         funcs.append(p)
#     for f in range(len(funcs)):
#         poly_zero.append(funcs[f](0))
    
    return poly_zero, poly_uncert #, poly_zero,poly_uncerts,