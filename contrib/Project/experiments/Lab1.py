"""
Author:         Rajeev B. Botadra
Email:          rajeevbb@uw.edu
Course:         EE595 -- Advanced Topics in Communications Theory
Instructor(s):  Dr. Hao Yin, YongHun Lee
Date:           October, 2024
---------------------------------------Lab#1---------------------------------------
This file contains scripts to run simulation experiments for Parts I, II, and III of Lab#1 and generate
corresponding plots. The results are discussed in the submitted report.
"""

import os
import subprocess
import multiprocessing
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

#Due to large simulation times, we use multiple threads running simulations in parallel
n_threads = 16

#Set simulation seed
seed = 1

# def runThread(cmd, tid):
#     ''' Runs a bash command on a thread with id=tid'''
#     #To give the thread a target function we use lambda functions of the provided cmd
#     proc = lambda cmd: os.system(cmd)
#     t = threading.thread(target=proc)
#     t.start()

#     return

def runNs3Cmd(cmd):
    proc = subprocess.Popen(cmd, shell=True)
    proc.wait()
    print(f'Completed Command: {cmd}')
    return

def P1a(results_dir, run=True):
    '''Two analyses for Part I: 
        P1a -- How does offered load (lambda) change the E2E Delay, Access Delay, and Queuing Delay
        P1b -- For different number of STAs (n) what are the values of lambda at which the network is saturated?
    '''
    os.system("echo 'Testing Offered Load versus Delays'")
    #Experiment constants
    rng_run = seed
    payload_size = 1500     #Bytes
    #Additional constants (defaults)
    simulation_time = 20    #Seconds
    mcs = 6
    channel_width = 20      #MHz
    n_sld = 5               #Number of SLD STAs on Link
    cw_min = 16             #Min time steps in cw

    #Variable
    lambdas = [10 ** n for n in np.arange(-4, 0+0.1, 0.1)]     #Creates range of lambda from 10^-4 to 10^0

    #Run experiment in parallel
    processes = []
    for l in lambdas:
        # command = (f'./ns3 run "single-bss-sld --rngRun={rng_run} '
        # f'--simulationTime={simulation_time} --payloadSize={payload_size} '
        # f'--mcs={mcs} --channelWidth={channel_width} --nSld={n_sld}'
        # f'--perSldLambda={l} --acBECwmin={cw_min}"')
        command = (f'./ns3 run "single-bss-sld --rngRun={rng_run} --payloadSize={payload_size} --perSldLambda={l}"')
        print(f'Executing Command: {command}')

        p = multiprocessing.Process(target=runNs3Cmd, args=(command,))
        p.start()
        processes.append(p)

        #os.system(min_command)
    #Synchronize threads
    for p in processes:
        p.join()
        
    #Move Experiment files to results directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir = os.path.join(results_dir, "P1a", timestamp)
    os.makedirs(dir, exist_ok=True)
    os.system(f'mv wifi-dcf.dat {dir}')

    #Plot results
    data = np.loadtxt(dir+'/wifi-dcf.dat', delimiter=',')
    x = np.log((data[:,-4]))
    e2e = data[:,2]
    access = data[:,3]
    queue = data[:,4]
    #Normalize values
    e2e = e2e/max(e2e)
    access = access/max(access)
    queue = queue/max(queue)    

    plt.figure()
    plt.plot(x, e2e, label='Normalized E2E Delay', color='black')
    plt.plot(x, access, label='Normalized Access Delay', color='orange')
    plt.plot(x, queue, label='Normalized Queue Delay', color='green')

    plt.legend()
    plt.xlabel("Offered Load (Arrival Rate)")
    plt.ylabel("Delay")
    plt.title("Normalized E2E, Access, and Queue Delays vs. Offered Load")
    plt.savefig(dir+'/plot.png', format='png', dpi=300)
    
    return

def P1b(results_dir, run=True):
    '''Two analyses for Part I: 
        P1a -- How does offered load (lambda) change the E2E Delay, Access Delay, and Queuing Delay
        P1b -- For different number of STAs (n) what are the values of lambda at which the network is saturated?

        If run=False, only plots most recent data file without running a new sim
    '''
    os.system("echo 'Testing Network Saturation (lambda) for different STAs (n)'")
    #Experiment constants
    rng_run = seed
    simulation_time = 20    #Seconds
    payload_size = 1500     #Bytes
    mcs = 6
    channel_width = 20      #MHz
    cw_min = 16             #Min time steps in cw

    #Variable
    lambdas = [10 ** n for n in np.arange(-4.0, 0.0, 1.0)]     #Creates range of lambda from 10^-4 to 10^0
    n_slds = [n for n in range(5, 30, 5)]

    #Run experiment in parallel
    processes = []
    #Process names for reference
    names = []
    thread_counter = 0
    for n_sld in n_slds:
        for l in lambdas:
            command = (f'./ns3 run "single-bss-sld --rngRun={rng_run} '
            f'--payloadSize={payload_size} --nSld={n_sld} --perSldLambda={l}"')

            print(f'Executing Command: {command}')

            p = multiprocessing.Process(target=runNs3Cmd, args=(command,))
            p.start()
            processes.append(p)
    
    #Synchronize threads
    for p in processes:
        p.join()
        
    #Move Experiment files to results directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir = os.path.join(results_dir, "P1b", timestamp)
    os.makedirs(dir, exist_ok=True)
    os.system(f'mv wifi-dcf.dat {dir}')

    #Plot results
    data = np.loadtxt(dir+'/wifi-dcf.dat', delimiter=',')
    x = np.log((data[:,-4]))    # Lambda
    y = data[:,1]               # SLD Throughput
    slds = data[:,-5]           # Num. SLDs
    plt.figure()

    colors = plt.cm.plasma(np.linspace(0, 1, len(n_slds)))
    for idx, n in enumerate(n_slds):
        subset = slds == n
        plt.plot(x[subset], y[subset], label=f'nSLD={n}', color=colors[idx])

    plt.legend()
    plt.xlabel("Offered Load (Arrival Rate)")
    plt.ylabel("SLD Throughput")
    plt.title("Througput Saturation vs. Lambda for varying number of SLDs")
    plt.savefig(dir+'/plot.png', format='png', dpi=300)
    
    return

def P2ab(results_dir, run=True):
    '''Two analyses for Part II: 
        P2a -- How does Throughput/Delay vary with number of STAs?
        P2b -- How does the probability of collisions vary with number of STAs?

        If run=False, only plots most recent data file without running a new sim
    '''
    os.system("echo 'Testing Throughput/Delay/Prob. of Collisions vs. Number of STAs'")
    #Experiment constants
    rng_run = seed
    simulation_time = 20    #Seconds
    payload_size = 1500     #Bytes
    mcs = 6
    channel_width = 20      #MHz
    cw_min = 16             #Min time steps in cw
    lamb = 10**-2           #High load to saturate network       
    #Variable
    n_slds = [n for n in range(5, 31, 5)]

    #Run experiment in parallel
    processes = []
    #Process names for reference
    names = []
    thread_counter = 0
    for n_sld in n_slds:
        command = (f'./ns3 run "single-bss-sld --rngRun={rng_run} '
        f'--payloadSize={payload_size} --nSld={n_sld} --perSldLambda={lamb}"')

        print(f'Executing Command: {command}')

        p = multiprocessing.Process(target=runNs3Cmd, args=(command,))
        p.start()
        processes.append(p)

    #Synchronize threads
    for p in processes:
        p.join()
        
    #Move Experiment files to results directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir = os.path.join(results_dir, "P2a", timestamp)
    os.makedirs(dir, exist_ok=True)
    os.system(f'mv wifi-dcf.dat {dir}')

    #Plot results
    data = np.loadtxt(dir+'/wifi-dcf.dat', delimiter=',')
    throughput = data[:,1]      #SLD Throughput
    e2e = data[:,2]             #E2E Delay
    pr_succ = data[:,0]         #Prob. of Success
    pr_coll = np.ones(len(pr_succ)) - pr_succ   #Prob. of Collisions
    x = data[:,-5]              #Num. SLDs

    plt.figure()
    plt.plot(x, throughput)

    plt.legend(title=f'Lambda={lamb}')
    plt.xlabel("Number of Stations")
    plt.ylabel("SLD Throughput")
    plt.title("Througput vs. Number of SLDs")
    plt.savefig(dir+'/plot2A1.png', format='png', dpi=300)

    plt.figure()
    plt.plot(x, e2e)
    
    plt.legend(title=f'Lambda={lamb}')
    plt.xlabel("Number of Stations")
    plt.ylabel("E2E Delay")
    plt.title("E2E Delay vs. Number of SLDs")
    plt.savefig(dir+'/plot2A2.png', format='png', dpi=300)    

    plt.figure()
    plt.plot(x, pr_coll)
    
    plt.legend(title=f'Lambda={lamb}')
    plt.xlabel("Number of Stations")
    plt.ylabel("Probability of Collisions")
    plt.title("Probability of Collisions vs. Number of SLDs")
    plt.savefig(dir+'/plot2B.png', format='png', dpi=300)    
    return

def P3ab(results_dir, run=True):
    '''Two analyses for Part III: 
        P3a -- How does Throughput/Delay vary with Initial Backoff Window Size (CW_min) when (n=10)?
        P3b -- Repeat 3a for (n=20,30)

        If run=False, only plots most recent data file without running a new sim
    '''
    os.system("echo 'Testing Throughput/Delay/ vs. CW_min'")
    #Experiment constants
    rng_run = seed
    simulation_time = 20    #Seconds
    payload_size = 150     #Bytes
    mcs = 6
    channel_width = 20      #MHz
    lamb = 10**-2           #High load to saturate network     
    n_slds = [10, 20, 30]
  
    #Variable
    cw_mins = [3, 7, 15, 31, 63, 127, 255, 511, 1023]

    #Run experiment in parallel
    processes = []
    #Process names for reference
    names = []
    thread_counter = 0
    for n_sld in n_slds:
        for cw_min in cw_mins:
            command = (f'./ns3 run "single-bss-sld --rngRun={rng_run} --acBECwmin={cw_min} '
            f'--payloadSize={payload_size} --nSld={n_sld} --perSldLambda={lamb}"')

            print(f'Executing Command: {command}')

            p = multiprocessing.Process(target=runNs3Cmd, args=(command,))
            p.start()
            processes.append(p)

    #Synchronize threads
    for p in processes:
        p.join()
        
    #Move Experiment files to results directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir = os.path.join(results_dir, "P3a", timestamp)
    os.makedirs(dir, exist_ok=True)
    os.system(f'mv wifi-dcf.dat {dir}')

    #Plot results
    data = np.loadtxt(dir+'/wifi-dcf.dat', delimiter=',')
    throughput = data[:,1]      #SLD Throughput
    e2e = data[:,2]             #E2E Delay
    x = data[:,-1]              #CW_min
    subset = x == 10

    plt.figure()
    plt.plot(x[subset], throughput[subset])

    plt.legend(title=f'Lambda={lamb}')
    plt.xlabel("CW_min")
    plt.ylabel("SLD Throughput")
    plt.title("Througput vs. CW_min")
    plt.savefig(dir+'/plot3A1.png', format='png', dpi=300)

    plt.figure()
    plt.plot(x[subset], e2e[subset])
    
    plt.legend(title=f'n_sld=10')
    plt.xlabel("CW_min")
    plt.ylabel("E2E Delay")
    plt.title("E2E Delay vs. CW_min")
    plt.savefig(dir+'/plot3A2.png', format='png', dpi=300)    

    #Repeat plotting for 3B
    subset = x == 20

    plt.figure()
    plt.plot(x[subset], throughput[subset])

    plt.legend(title=f'n_sld=20')
    plt.xlabel("CW_min")
    plt.ylabel("SLD Throughput")
    plt.title("Througput vs. CW_min")
    plt.savefig(dir+'/plot3B1.png', format='png', dpi=300)

    plt.figure()
    plt.plot(x[subset], e2e[subset])
    
    plt.legend(title=f'Lambda={lamb}')
    plt.xlabel("CW_min")
    plt.ylabel("E2E Delay")
    plt.title("E2E Delay vs. CW_min")
    plt.savefig(dir+'/plot3B2.png', format='png', dpi=300)    

    subset = x == 30

    plt.figure()
    plt.plot(x[subset], throughput[subset])

    plt.legend(title=f'n_sld=30')
    plt.xlabel("CW_min")
    plt.ylabel("SLD Throughput")
    plt.title("Througput vs. CW_min")
    plt.savefig(dir+'/plot3B3.png', format='png', dpi=300)

    plt.figure()
    plt.plot(x[subset], e2e[subset])
    
    plt.legend(title=f'Lambda={lamb}')
    plt.xlabel("CW_min")
    plt.ylabel("E2E Delay")
    plt.title("E2E Delay vs. CW_min")
    plt.savefig(dir+'/plot3B4.png', format='png', dpi=300)    
    return

def main():
    current_dir = os.getcwd()
    #Make results directory
    results_dir = os.path.join(current_dir, 'results', 'Lab1')
    os.makedirs(results_dir, exist_ok=True)

    #Jump to Top Level Directory of ns3-dev
    os.chdir("../../..")
    # Check if the ns3 executable exists
    if not os.path.exists("./ns3"):
        print(f"Cannot find ns3 executable, run program from .../experiments subdirectory")
        return

    #Select Experiment to run
    experiment = input("Select Experiment (P1a\P1b\P2ab\P3ab\ALL)")

    #Confirm that it's okay to delete existing log files
    dat_confirmation = input("Remove wifi-dcf.dat from TLD? (y/n)")
    if(dat_confirmation == "y"):
        os.system("rm wifi-dcf.dat")
        os.system("echo 'wifi-dcf.dat deleted'")
    else:
        os.system("echo 'Program terminated'")
        return

    if(experiment == "P1a"):
        P1a(results_dir)
    elif(experiment == "P1b"):
        P1b(results_dir)
    elif(experiment == "P2ab"):
        P2ab(results_dir)    
    elif(experiment == "P3ab"):
        P3ab(results_dir)
    elif(experiment == "ALL"):
        P3ab(results_dir)
        P1b(results_dir)
    else:
        os.system("echo 'Invalid experiment selection'")
        os.system("echo 'Program terminated'")
        return

    return

def alt_main():
    #Just plotting stuff
    # data = np.loadtxt('/home/aspen/Coursework/EE595/ns-3-dev/contrib/uwee595/experiments/results/Lab1/P1a/20241029_172558/wifi-dcf.dat', delimiter=',')
    # x = np.log(data[:,-4])
    # e2e = data[:,2]
    # access = data[:,3]
    # queue = data[:,4]
    # #Normalize values
    # e2e = e2e/max(e2e)
    # access = access/max(access)
    # queue = queue/max(queue)

    # plt.figure()
    # plt.plot(x, e2e, label='Normalized E2E Delay', color='black')
    # plt.plot(x, access, label='Normalized Access Delay', color='orange')
    # plt.plot(x, queue, label='Normalized Queue Delay', color='green')

    # plt.legend()
    # plt.xlabel("Offered Load (Arrival Rate)")
    # plt.ylabel("Delay")
    # plt.title("Normalized E2E, Access, and Queue Delays vs. Offered Load")
    # plt.savefig('/home/aspen/Coursework/EE595/ns-3-dev/contrib/uwee595/experiments/results/Lab1/P1a/20241029_172558/plot.png', format='png', dpi=300)
    # return

    #Plot results
    n_slds = [n for n in range(1, 30, 1)]
    dir = '/home/aspen/Coursework/EE595/ns-3-dev/contrib/uwee595/experiments/results/Lab1/P1b/20241106_141700'
    data = np.loadtxt(dir + '/wifi-dcf.dat', delimiter=',')
    x = data[:,-4]    # Lambda
    y = data[:,1]               # SLD Throughput
    slds = data[:,-5]           # Num. SLDs
    plt.figure()

    colors = plt.cm.plasma(np.linspace(0, 1, len(n_slds)))
    for idx, n in enumerate(n_slds):
        subset = slds == n
        plt.plot(x[subset], y[subset], label=f'nSLD={n}', color=colors[idx])

    plt.legend()
    plt.xlabel("Offered Load (Arrival Rate)")
    plt.ylabel("SLD Throughput")
    plt.title("Througput Saturation vs. Lambda for varying number of SLDs")
    plt.savefig(dir+'/plot.png', format='png', dpi=300)
    

    return

if __name__ == '__main__':
    main()
    #alt_main()
