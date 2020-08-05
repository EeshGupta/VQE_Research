# Error Mitigation using Neural Networks

## Introduction 

### Why did I do this work? 
- Recently, a hybrid quantum-classical algorithm – Variational Quantum Eigensolver (VQE) – has been devised which optimizes electrons in molecular
orbitals to minimize the energy of molecular systems.

- However quantum computers are highly susceptible to errors due to imperfect qubits and gates.

- Errors also stem from decomposing the Hamiltonian into pauli terms in VQE 

- If there was a way to directly measure the Hamiltonian without Pauli decomposition, then variance in results might be 
reduced.


### What is my hypothesis?

Verifying whether using a neural network  as opposed to Hamiltonian Averaging on optimized circuit in VQE will improve precision and accuracy of energy estimates

## Results

### What was measured? 

### What did I find?

## Conclusion

### Was the hypothesis proved or disproved? 

### Why does it make a difference

### What did I learn?

## Updates 
August 5, 2020: Familiar with dataset, information stored in visible layer, cost function. Emailed questions to Roger and Torlai on 
how multiple local hamiltonians can be measured, how to get P(x). BTW, events whose probabilities NN will calculate on 2 qubit device 
are 00,01,11,10 in th ZZ basis.

## References
Torlai, Giacomo et al. “Precise Measurement of Quantum Observables with Neural-Network Estimators.” Physical Review Research 2.2 (2020): n. pag. Crossref. Web.
