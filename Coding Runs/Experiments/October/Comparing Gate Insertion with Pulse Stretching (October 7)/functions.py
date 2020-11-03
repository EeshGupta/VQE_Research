import math

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