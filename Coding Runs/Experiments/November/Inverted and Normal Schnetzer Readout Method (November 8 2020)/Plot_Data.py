import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt

def stats(data):
    '''
    Finds mean, std dev, and rms of data 
    '''
    data = np.array(data)
    rms = np.sqrt(np.mean(data**2))
    (mu, sigma) = norm.fit(data)
    return mu, sigma, rms

def readinput(file):
    '''
    reads data from text file into an array
    '''
    arry = []
    file_p = open(file, 'r') 
    #print(file_p)
    line = file_p.readline()
    #print(line)
    
    #iterating through the lines
    while line:
        #print(line)
        line = line.split(',')
        d = float(line[0])
        arry.append(d)
        line = file_p.readline()
    file_p.close()
    return arry


import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt

def plotter(arry1, arry2, arry3, colors, name):
    '''
    Returns a plot with histograms and fitted normal curves
    '''
    
    a = plt.figure()
    
    mu1, sigma1, rms1 = stats(arry1)
    mu2, sigma2, rms2 = stats(arry2)
    mu3, sigma3, rms3 = stats(arry3)
    
    #Histograms
    n, bins, patches = plt.hist(arry1, bins=int(len(arry1)/10), density = True, color = colors[0], label = r'Noisy: $\mu=%.3f, \sigma=%.3f, r = %.3f$' %(mu1, sigma1, rms1))
    y = norm.pdf( bins, mu1, sigma1)
    l1 = plt.plot(bins, y, color = colors[1], linestyle = '--', linewidth=2)
    #plt.plot(arry1,[gaussian(x, mu1, sigma1) for x in arry1], 'r--')
    
    n, bins, patches = plt.hist(arry2, int(len(arry2)/10), color = colors[2], density = True, label = r'Mitigated: $\mu=%.3f, \sigma=%.3f, r = %.3f$' %(mu2, sigma2, rms2))
    y = norm.pdf( bins, mu2, sigma2)
    l2 = plt.plot(bins, y, color = colors[3], linestyle = '--', linewidth=2)
    
    n, bins, patches = plt.hist(arry3, int(len(arry3)/10), color = colors[4], density = True, label = r'Inverted and Mitigated: $\mu=%.3f, \sigma=%.3f, r = %.3f$' %(mu3, sigma3, rms3))
    y = norm.pdf( bins, mu3, sigma3)
    l2 = plt.plot(bins, y, color = colors[5], linestyle = '--', linewidth=2)
    

    #a = plt.figure()
    #plt.hist(diff_r, bins=100, color = "orang", label = 'Noisy')
    #plt.hist(diff_nr, bins=100, color = "paleturquoise", label = 'Mitigated')
    plt.title("Difference between noisy and ideal energies")
    plt.xlabel("Energy Difference (Hartree)")
    plt.ylabel("Frequency (Normalized)")
    plt.legend()
    #plt.show()
    a.savefig(name, dpi = 1000)
    return None