"""
Author:         Rajeev B. Botadra
Email:          rajeevbb@uw.edu
Course:         EE595 -- Advanced Topics in Communications Theory
Instructor(s):  Dr. Hao Yin, YongHun Lee
Date:           October, 2024
---------------------------------------Lab#0---------------------------------------
This file contains scripts to run experiments for Q1, Q2, and Q3 of Lab#0. The results
are discussed in the submitted report.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

def Q1a(results_dir):
    '''Test Link Performance and Packet Size'''
    os.system("echo 'Q1a -- Testing Link Performance versus Packet Size'")
    #Experiment constants
    distance = 50
    max_packets = 1000
    transmit_power = 0
    noise_power = -90
    frequency = 5e+09
    loss_model_type = 'Friis'
    
    #Variable
    packet_sizes = [2 ** n for n in range(1, 16, 1)] #Creates range of packet sizes from 2^1=2 to 2^15=32768

    #Run experiment
    for size in packet_sizes:
        print(f'Packet Size: {size}')
        command = (f'./ns3 run "link-performance --distance={distance} '
        f'--maxPackets={max_packets} --transmitPower={transmit_power} '
        f'--noisePower={noise_power} --frequency={frequency} '
        f'--packetSize={size} --lossModelType={loss_model_type} --metadata={size}"')
        os.system(command)
        
    #Move Experiment files to results directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir = os.path.join(results_dir, "Q1a", timestamp)
    os.makedirs(dir, exist_ok=True)
    os.system(f'mv link-performance-* {dir}')

    #Plot results
    data = np.loadtxt(dir+'/link-performance-summary.dat', delimiter=' ')
    x = data[:,5]
    y = data[:,3]
    y_err = data[:,4]
    plt.figure()
    plt.errorbar(x, y, yerr=y_err, color='black', ecolor='red')
    plt.xlabel("Packet Size (bytes)")
    plt.ylabel("Packet Error Rate")
    plt.title("Packet Error Rate vs. Packet Size")
    plt.savefig(dir+'/plot.png', format='png', dpi=300)
    
    return

def Q1b(results_dir):
    '''Address Pt2 of Q1 -- For a given PER how much more distance is afforded by packet size of 100 vs 1000 bytes'''
    os.system("echo 'Q1b -- Testing 100 bytes vs 1000 bytes'")
    
    #Fix Packet Size to 100, vary distance
    #Experiment constants
    packet_size = 100
    max_packets = 1000
    transmit_power = 0
    noise_power = -90
    frequency = 5e+09
    loss_model_type = 'Friis'
    
    #Variable
    distances = list(range(25, 80, 1)) #Creates range of distances from 25-80

    for d in distances:
        print(f'Distance: {d}')
        command = (f'./ns3 run "link-performance --distance={d} '
        f'--maxPackets={max_packets} --transmitPower={transmit_power} '
        f'--noisePower={noise_power} --frequency={frequency} '
        f'--packetSize={packet_size} --lossModelType={loss_model_type} --metadata={d}"')
        os.system(command)

    #Move Experiment files to results directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir = os.path.join(results_dir, "Q1b", timestamp)
    os.makedirs(dir, exist_ok=True)
    #Rename file to include packet size
    os.system(f'mv ./link-performance-summary.dat {dir}/link-performance-summary-100B.dat')

    #Now repeat with packet size of 1000B
    packet_size = 1000

    for d in distances:
        print(f'Distance: {d}')
        command = (f'./ns3 run "link-performance --distance={d} '
        f'--maxPackets={max_packets} --transmitPower={transmit_power} '
        f'--noisePower={noise_power} --frequency={frequency} '
        f'--packetSize={packet_size} --lossModelType={loss_model_type} --metadata={d}"')
        os.system(command)

    #Rename file to include packet size
    os.system(f'mv ./link-performance-summary.dat {dir}/link-performance-summary-1000B.dat')

    #Plot results
    dataA = np.loadtxt(dir+'/link-performance-summary-100B.dat', delimiter=' ')
    dataB = np.loadtxt(dir+'/link-performance-summary-1000B.dat', delimiter=' ')

    x = dataA[:,5]
    yA = dataA[:,3]
    yA_err = dataA[:,4]
    yB = dataB[:,3]
    yB_err = dataB[:,4]

    plt.figure()
    plt.errorbar(x, yA, yerr=yA_err, color='black', ecolor='red', label='Packet Size: 100B')
    plt.errorbar(x, yB, yerr=yB_err, color='blue', ecolor='red', label='Packet Size: 1000B')
    plt.legend()
    plt.xlabel("Distance")
    plt.ylabel("Packet Error Rate")
    plt.title("Packet Error Rate vs. Distance for Packet Size of 100B and 1000B")
    plt.savefig(dir+'/plot.png', format='png', dpi=300)

    return

def Q2a(results_dir):
    '''Test Link Performance and Frequency'''
    os.system("echo 'Q2a -- Testing effects of Transmission Frequency'")
    
    #Experiment constants
    distance = 50
    packet_size = 1000
    max_packets = 1000
    transmit_power = 0
    noise_power = -90
    loss_model_type = 'Friis'
    
    #Variable
    frequencies = list(range(int(5e+07), int(7.5e+09), int(1e+08))) #Creates range of frequencies from 50MHz to 7.5GHz

    for freq in frequencies:
        print(f'Frequency: {freq}')
        command = (f'./ns3 run "link-performance --distance={distance} '
        f'--maxPackets={max_packets} --transmitPower={transmit_power} '
        f'--noisePower={noise_power} --frequency={freq} '
        f'--packetSize={packet_size} --lossModelType={loss_model_type} --metadata={freq}"')
        os.system(command)

    #Move Experiment files to results directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir = os.path.join(results_dir, "Q2", timestamp)
    os.makedirs(dir, exist_ok=True)
    os.system(f'mv link-performance-* {dir}')

    #Plot results
    data = np.loadtxt(dir+'/link-performance-summary.dat', delimiter=' ')
    x = data[:,5]
    y = data[:,3]
    y_err = data[:,4]
    plt.figure()
    plt.errorbar(x, y, yerr=y_err, color='black', ecolor='green')
    plt.xlabel("Frequency (GHz)")
    plt.ylabel("Packet Error Rate")
    plt.title("Packet Error Rate vs. Frequency")
    plt.savefig(dir+'/plot.png', format='png', dpi=300)

    return

def Q2b(results_dir):
    '''Test Link Performance and Frequency'''
    os.system("echo 'Q2b -- Testing 2.4GHz vs. 5GHz'")
    
    #Fix frequency to 2.4GHz, vary distance
    #Experiment constants
    packet_size = 1000
    max_packets = 1000
    transmit_power = 0
    noise_power = -90
    frequency = 2.4e+09
    loss_model_type = 'Friis'
    
    #Variable
    distances = list(range(30, 150, 1)) #Creates range of distances from 30-150

    for d in distances:
        print(f'Distance: {d}')
        command = (f'./ns3 run "link-performance --distance={d} '
        f'--maxPackets={max_packets} --transmitPower={transmit_power} '
        f'--noisePower={noise_power} --frequency={frequency} '
        f'--packetSize={packet_size} --lossModelType={loss_model_type} --metadata={d}"')
        os.system(command)

    #Move Experiment files to results directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir = os.path.join(results_dir, "Q2b", timestamp)
    os.makedirs(dir, exist_ok=True)
    #Rename file to include freq
    os.system(f'mv ./link-performance-summary.dat {dir}/link-performance-summary-2_4GHz.dat')

    #Now repeat with frequency of 5GHz
    frequency = 5e+09

    for d in distances:
        print(f'Distance: {d}')
        command = (f'./ns3 run "link-performance --distance={d} '
        f'--maxPackets={max_packets} --transmitPower={transmit_power} '
        f'--noisePower={noise_power} --frequency={frequency} '
        f'--packetSize={packet_size} --lossModelType={loss_model_type} --metadata={d}"')
        os.system(command)

    #Rename file to include packet size
    os.system(f'mv ./link-performance-summary.dat {dir}/link-performance-summary-5GHz.dat')

    #Plot results
    dataA = np.loadtxt(dir+'/link-performance-summary-2_4GHz.dat', delimiter=' ')
    dataB = np.loadtxt(dir+'/link-performance-summary-5GHz.dat', delimiter=' ')

    x = dataA[:,5]
    yA = dataA[:,3]
    yA_err = dataA[:,4]
    yB = dataB[:,3]
    yB_err = dataB[:,4]

    plt.figure()
    plt.errorbar(x, yA, yerr=yA_err, color='black', ecolor='red', label='Frequency: 2.4GHz')
    plt.errorbar(x, yB, yerr=yB_err, color='blue', ecolor='red', label='Frequency: 5GHz')
    plt.legend()
    plt.xlabel("Distance")
    plt.ylabel("Packet Error Rate")
    plt.title("Packet Error Rate vs. Distance for Frequency of 2.4GHz and 5GHz")
    plt.savefig(dir+'/plot.png', format='png', dpi=300)

    return

def Q3(results_dir):
    '''Test Link Performance and Transmission Power'''
    os.system("echo 'Q3 -- Testing Link Performance versus Transmission Power'")
    #Experiment constants
    distance = 100
    packet_size = 1000
    max_packets = 1000
    noise_power = -90
    frequency = 2.4e+09
    loss_model_type = 'Friis'
    
    #Variable
    transmit_powers = np.arange(-3, 2.5, 0.1) #Creates range of tranmission power from -3dBm to 2.5dBm

    #Run experiment
    for power in transmit_powers:
        print(f'Transmission Power: {power}')
        command = (f'./ns3 run "link-performance --distance={distance} '
        f'--maxPackets={max_packets} --transmitPower={power} '
        f'--noisePower={noise_power} --frequency={frequency} '
        f'--packetSize={packet_size} --lossModelType={loss_model_type} --metadata={power}"')
        os.system(command)
        
    #Move Experiment files to results directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir = os.path.join(results_dir, "Q3", timestamp)
    os.makedirs(dir, exist_ok=True)
    os.system(f'mv link-performance-* {dir}')

    #Plot results
    data = np.loadtxt(dir+'/link-performance-summary.dat', delimiter=' ')
    x = data[:,5]
    y = data[:,3]
    y_err = data[:,4]
    plt.figure()
    plt.errorbar(x, y, yerr=y_err, color='black', ecolor='red')
    plt.xlabel("Transmission Power (dBm)")
    plt.ylabel("Packet Error Rate")
    plt.title("Packet Error Rate vs. Transmission Power")
    plt.savefig(dir+'/plot.png', format='png', dpi=300)
    
    return

def main():
    current_dir = os.getcwd()
    #Make results directory
    results_dir = os.path.join(current_dir, 'results', 'Lab0')
    os.makedirs(results_dir, exist_ok=True)
    #Jump to Top Level Directory of ns3-dev
    os.chdir("../../..")

    #Select Experiment to run
    experiment = input("Select Experiment (1a/1b/2a/2b/3)")

    #Confirm that it's okay to delete existing log files
    rssi_confirmation = input("Remove link-performance-rssi.dat from TLD? (y/n)")
    if(rssi_confirmation == "y"):
        os.system("rm link-performance-rssi.dat")
        os.system("echo 'link-performance-rssi.dat deleted'")
    else:
        os.system("echo 'Program terminated'")
        return
    
    summary_confirmation = input("Remove link-performance-summary.dat from TLD? (y/n)")
    if(summary_confirmation == "y"):
        os.system("rm link-performance-summary.dat")
        os.system("echo 'link-performance-summary.dat deleted'")
    else:
        os.system("echo 'Program terminated'")
        return

    if(experiment == "1a"):
        Q1a(results_dir)
    elif(experiment == "1b"):
        Q1b(results_dir)
    elif(experiment == "2a"):
        Q2a(results_dir)
    elif(experiment == "2b"):
        Q2b(results_dir)
    elif(experiment == "3"):
        Q3(results_dir)
    else:
        os.system("echo 'Invalid experiment selection'")
        os.system("echo 'Program terminated'")
        return

    return

if __name__ == '__main__':
    main()
