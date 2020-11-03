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


def plotter(file1, file2, color1, color2, color3, color4, name):
    '''
    Returns a plot with histograms and fitted normal curves
    '''
    arry1 = readinput(file1)
    arry2 = readinput(file2)
    
    a = plt.figure()
    
    mu1, sigma1, rms1 = stats(arry1)
    mu2, sigma2, rms2 = stats(arry2)
    
    #Histograms
    n, bins, patches = plt.hist(arry1, bins=int(len(arry1)/10), density = True, color = color1, label = r'Noisy: $\mu=%.3f, \sigma=%.3f, r = %.3f$' %(mu1, sigma1, rms1))
    y = norm.pdf( bins, mu1, sigma1)
    l1 = plt.plot(bins, y, color = color3, linestyle = '--', linewidth=2)
    #plt.plot(arry1,[gaussian(x, mu1, sigma1) for x in arry1], 'r--')
    
    n, bins, patches = plt.hist(arry2, int(len(arry2)/10), color = color2, density = True, label = r'Mitigated: $\mu=%.3f, \sigma=%.3f, r = %.3f$' %(mu2, sigma2, rms2))
    y = norm.pdf( bins, mu2, sigma2)
    l2 = plt.plot(bins, y, color = color4, linestyle = '--', linewidth=2)
    

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