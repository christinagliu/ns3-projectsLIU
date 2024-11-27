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
    lambdas = [10 ** n for n in np.arange(-5, -1-0.1, 0.1)]     #Creates range of lambda from 10^-5 to 10^-1

    #Run experiment in parallel
    processes = []
    for l in lambdas:
        # command = (f'./ns3 run "single-bss-sld --rngRun={rng_run} '
        # f'--simulationTime={simulation_time} --payloadSize={payload_size} '
        # f'--mcs={mcs} --channelWidth={channel_width} --nSld={n_sld}'
        # f'--perSldLambda={l} --acBECwmin={cw_min}"')
        command = (f'./ns3 run "single-bss-mld --rngRun={rng_run} --payloadSize={payload_size} --mldPerNodeLambda={l}"')
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
    os.system(f'mv wifi-mld.dat {dir}')

    #Load data
    data = np.loadtxt(dir+'/wifi-mld.dat', delimiter=',')
    x = np.sort(data[:,29])
    queueL1 = np.sort(data[:,6])
    queueL2 = np.sort(data[:,7])
    queueAgg = np.sort(data[:,8])

    accL1 = np.sort(data[:,9])
    accL2 = np.sort(data[:,10])
    accAgg = np.sort(data[:,11])

    e2eL1 = np.sort(data[:,12])
    e2eL2 = np.sort(data[:,13])
    e2eAgg = np.sort(data[:,14])

    #Plot results
    plt.figure()
    plt.plot(x, queueL1, label='Link I Queue Delay', color='black')
    plt.plot(x, queueL2, label='Link II Queue Delay', color='orange')
    plt.plot(x, queueAgg, label='Aggregate Queue Delay', color='blue')
    plt.xscale('log')
    plt.grid()
    plt.legend()
    plt.xlabel("Offered Load (Arrival Rate)")
    plt.ylabel("Delay (us)")
    plt.title("Link I/II/Agggregate Queue Delays vs. Offered Load")
    plt.savefig(dir+'/queueDelay_plot.png', format='png', dpi=300)

    plt.figure()
    plt.plot(x, accL1, label='Link I Access Delay', color='black')
    plt.plot(x, accL2, label='Link II Access Delay', color='orange')
    plt.plot(x, accAgg, label='Aggregate Access Delay', color='blue')
    plt.xscale('log')
    plt.grid()
    plt.legend()
    plt.xlabel("Offered Load (Arrival Rate)")
    plt.ylabel("Delay (us)")
    plt.title("Link I/II/Agggregate Access Delays vs. Offered Load")
    plt.savefig(dir+'/accessDelay_plot.png', format='png', dpi=300) 

    plt.figure()
    plt.plot(x, e2eL1, label='Link I E2E Delay', color='black')
    plt.plot(x, e2eL2, label='Link II E2E Delay', color='orange')
    plt.plot(x, e2eAgg, label='Aggregate E2E Delay', color='blue')
    plt.xscale('log')
    plt.grid()
    plt.legend()
    plt.xlabel("Offered Load (Arrival Rate)")
    plt.ylabel("Delay (us)")
    plt.title("Link I/II/Agggregate E2E Delays vs. Offered Load")
    plt.savefig(dir+'/e2eDelay_plot.png', format='png', dpi=300) 
    
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
    lambdas = [10 ** n for n in np.arange(-4.0, 0, 0.5)]     #Creates range of lambda from 10^-4 to 10^-1
    n_stas = [n for n in range(5, 31, 5)]

    #Run experiment in parallel
    processes = []
    #Process names for reference
    names = []
    thread_counter = 0
    for n_sta in n_stas:
        for l in lambdas:
            command = (f'./ns3 run "single-bss-mld --rngRun={rng_run} '
            f'--payloadSize={payload_size} --nMldSta={n_sta} --mldPerNodeLambda={l}"')

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
    os.system(f'mv wifi-mld.dat {dir}')

    #Plot results
    data = np.loadtxt(dir+'/wifi-mld.dat', delimiter=',')
    x = np.sort(data[:,29])             # Lambda
    mean_throughputL1 = data[:,3]       # MLD Throughput Link 1
    mean_throughputL2 = data[:,4]       # MLD Throughput Link 2
    mean_throughputAgg = data[:,5]       # MLD Throughput Aggregated
    n_slds = data[:,28]                  # Num. SLDs
    
    plt.figure()

    colors = plt.cm.plasma(np.linspace(0, 1, len(n_slds)))
    for idx, n in enumerate(n_slds):
        subset = n_slds == n
        plt.plot(x[subset], mean_throughputL1[subset], label=f'Link I -- nSLD={n}', color=colors[idx])
        plt.plot(x[subset], mean_throughputL2[subset], label=f'Link II -- nSLD={n}', color=colors[idx])
        plt.plot(x[subset], mean_throughputAgg[subset], label=f'Aggregate -- nSLD={n}', color=colors[idx])

    plt.legend()
    plt.xlabel("Offered Load (Arrival Rate)")
    plt.ylabel("Mean MLD Throughput (Mbps)")
    plt.title("Througput Saturation vs. Lambda for varying number of SLDs")
    plt.savefig(dir+'/plot.png', format='png', dpi=300)
    
    return

def P2a(results_dir, run=True):
    '''Two analyses for Part II: 
        P2a -- Studying Delay with Assymetric Link conditions (MCS)
        P2b -- Studying Delay with Assymetric Link conditions (Bandwidth)

        If run=False, only plots most recent data file without running a new sim
    '''
    os.system("echo 'Testing Link Assymetry with different MCS'")
    #Experiment constants
    rng_run = seed
    simulation_time = 20    #Seconds
    payload_size = 1500     #Bytes
    mcs = 6
    channel_width = 20      #MHz
    cw_min = 16             #Min time steps in cw
    n_sta = 5

    #Variable
    lambdas = [10 ** n for n in np.arange(-4.0, 0, 0.5)]     #Creates range of lambda from 10^-4 to 10^-1
    mcs2s = [2, 4, 8]

    #Run experiment in parallel
    processes = []
    #Process names for reference
    names = []
    thread_counter = 0
    for mcs2 in mcs2s:
        for l in lambdas:
            command = (f'./ns3 run "single-bss-mld --rngRun={rng_run} '
            f'--payloadSize={payload_size} --nMldSta={n_sta} --mldPerNodeLambda={l} '
            f'--mcs={mcs} --mcs2={mcs2}"')
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
    os.system(f'mv wifi-mld.dat {dir}')

    #Plot results
    # data = np.loadtxt(dir+'/wifi-mld.dat', delimiter=',')
    # x = np.sort(data[:,29])             # Lambda
    # mean_throughputL1 = data[:,3]       # MLD Throughput Link 1
    # mean_throughputL2 = data[:,4]       # MLD Throughput Link 2
    # mean_throughputAgg = data[:,5]       # MLD Throughput Aggregated
    # n_slds = data[:,28]                  # Num. SLDs
    
    # plt.figure()

    # colors = plt.cm.plasma(np.linspace(0, 1, len(n_slds)))
    # for idx, n in enumerate(n_slds):
    #     subset = n_slds == n
    #     plt.plot(x[subset], mean_throughputL1[subset], label=f'Link I -- nSLD={n}', color=colors[idx])
    #     plt.plot(x[subset], mean_throughputL2[subset], label=f'Link II -- nSLD={n}', color=colors[idx])
    #     plt.plot(x[subset], mean_throughputAgg[subset], label=f'Aggregate -- nSLD={n}', color=colors[idx])

    # plt.legend()
    # plt.xlabel("Offered Load (Arrival Rate)")
    # plt.ylabel("Mean MLD Throughput (Mbps)")
    # plt.title("Througput Saturation vs. Lambda for varying number of SLDs")
    # plt.savefig(dir+'/plot.png', format='png', dpi=300)
    
    return

def P2b(results_dir, run=True):
    '''Two analyses for Part II: 
        P2a -- Studying Delay with Assymetric Link conditions (MCS)
        P2b -- Studying Delay with Assymetric Link conditions (Bandwidth)

        If run=False, only plots most recent data file without running a new sim
    '''
    os.system("echo 'Testing Link Assymetry with different Bandwidths'")
    #Experiment constants
    rng_run = seed
    simulation_time = 20    #Seconds
    payload_size = 1500     #Bytes
    channel_width = 20      #MHz
    cw_min = 16             #Min time steps in cw
    n_sta = 5

    #Variable
    lambdas = [10 ** n for n in np.arange(-4.0, 0, 0.5)]    #Creates range of lambda from 10^-4 to 10^-1
    channel_width2s = [40, 80]                             #MHz

    #Run experiment in parallel
    processes = []
    #Process names for reference
    names = []
    thread_counter = 0
    for channel_width2 in channel_width2s:
        for l in lambdas:
            command = (f'./ns3 run "single-bss-mld --rngRun={rng_run} '
            f'--payloadSize={payload_size} --nMldSta={n_sta} --mldPerNodeLambda={l} '
            f'--channelWidth={channel_width} --channelWidth2={channel_width2}"')
            print(f'Executing Command: {command}')

            p = multiprocessing.Process(target=runNs3Cmd, args=(command,))
            p.start()
            processes.append(p)
    
    #Synchronize threads
    for p in processes:
        p.join()
        
    #Move Experiment files to results directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir = os.path.join(results_dir, "P2b", timestamp)
    os.makedirs(dir, exist_ok=True)
    os.system(f'mv wifi-mld.dat {dir}')

    #Plot results
    # data = np.loadtxt(dir+'/wifi-mld.dat', delimiter=',')
    # x = np.sort(data[:,29])             # Lambda
    # mean_throughputL1 = data[:,3]       # MLD Throughput Link 1
    # mean_throughputL2 = data[:,4]       # MLD Throughput Link 2
    # mean_throughputAgg = data[:,5]       # MLD Throughput Aggregated
    # n_slds = data[:,28]                  # Num. SLDs
    
    # plt.figure()

    # colors = plt.cm.plasma(np.linspace(0, 1, len(n_slds)))
    # for idx, n in enumerate(n_slds):
    #     subset = n_slds == n
    #     plt.plot(x[subset], mean_throughputL1[subset], label=f'Link I -- nSLD={n}', color=colors[idx])
    #     plt.plot(x[subset], mean_throughputL2[subset], label=f'Link II -- nSLD={n}', color=colors[idx])
    #     plt.plot(x[subset], mean_throughputAgg[subset], label=f'Aggregate -- nSLD={n}', color=colors[idx])

    # plt.legend()
    # plt.xlabel("Offered Load (Arrival Rate)")
    # plt.ylabel("Mean MLD Throughput (Mbps)")
    # plt.title("Througput Saturation vs. Lambda for varying number of SLDs")
    # plt.savefig(dir+'/plot.png', format='png', dpi=300)
    
    return

def P3a(results_dir, run=True):
    '''Two analyses for Part III: 
        P3a -- Maximizing throughput with varied link probability, MCS 
        P3b -- Minimize E2E delay with varied link probability, Bandwidth

        If run=False, only plots most recent data file without running a new sim
    '''
    os.system("echo 'Testing Throughput against Link Probability and MCS'")
    #Experiment constants
    rng_run = seed
    simulation_time = 20    #Seconds
    payload_size = 1500     #Bytes
    channel_width = 20      #MHz
    cw_min = 16             #Min time steps in cw
    n_sta = 5
    l = 10**-1         #Saturates network
    mcs = 6

    #Variable
    mcs2s = [2, 4, 8]
    mld_probL1s = [n for n in np.arange(0,1,0.1)]

    #Run experiment in parallel
    processes = []
    #Process names for reference
    names = []
    thread_counter = 0
    for mcs2 in mcs2s:
        for mld_probL1 in mld_probL1s:
            command = (f'./ns3 run "single-bss-mld --rngRun={rng_run} '
            f'--payloadSize={payload_size} --nMldSta={n_sta} --mldPerNodeLambda={l} '
            f'--mcs={mcs} --mcs2={mcs2} --mldProbLink1={mld_probL1}"')
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
    os.system(f'mv wifi-mld.dat {dir}')

    #Plot results
    # data = np.loadtxt(dir+'/wifi-mld.dat', delimiter=',')
    # x = np.sort(data[:,29])             # Lambda
    # mean_throughputL1 = data[:,3]       # MLD Throughput Link 1
    # mean_throughputL2 = data[:,4]       # MLD Throughput Link 2
    # mean_throughputAgg = data[:,5]       # MLD Throughput Aggregated
    # n_slds = data[:,28]                  # Num. SLDs
    
    # plt.figure()

    # colors = plt.cm.plasma(np.linspace(0, 1, len(n_slds)))
    # for idx, n in enumerate(n_slds):
    #     subset = n_slds == n
    #     plt.plot(x[subset], mean_throughputL1[subset], label=f'Link I -- nSLD={n}', color=colors[idx])
    #     plt.plot(x[subset], mean_throughputL2[subset], label=f'Link II -- nSLD={n}', color=colors[idx])
    #     plt.plot(x[subset], mean_throughputAgg[subset], label=f'Aggregate -- nSLD={n}', color=colors[idx])

    # plt.legend()
    # plt.xlabel("Offered Load (Arrival Rate)")
    # plt.ylabel("Mean MLD Throughput (Mbps)")
    # plt.title("Througput Saturation vs. Lambda for varying number of SLDs")
    # plt.savefig(dir+'/plot.png', format='png', dpi=300)
    
    return

def P3b(results_dir, run=True):
    '''Two analyses for Part III: 
        P3a -- Maximizing throughput with varied link probability, MCS 
        P3b -- Minimize E2E delay with varied link probability, Bandwidth

        If run=False, only plots most recent data file without running a new sim
    '''
    os.system("echo 'Testing E2E Latency against Link Probability and Bandwidth'")
    #Experiment constants
    rng_run = seed
    simulation_time = 20    #Seconds
    payload_size = 1500     #Bytes
    channel_width = 20      #MHz
    cw_min = 16             #Min time steps in cw
    n_sta = 5
    l = 10**-2    

    #Variable
    channel_width2s = [40, 80]       #MHz
    mld_probL1s = [n for n in np.arange(0,1,0.1)]

    #Run experiment in parallel
    processes = []
    #Process names for reference
    names = []
    thread_counter = 0
    for channel_width2 in channel_width2s:
        for mld_probL1 in mld_probL1s:
            command = (f'./ns3 run "single-bss-mld --rngRun={rng_run} '
            f'--payloadSize={payload_size} --nMldSta={n_sta} --mldPerNodeLambda={l} '
            f'--channelWidth={channel_width} --channelWidth2={channel_width2} --mldProbLink1={mld_probL1}"')
            print(f'Executing Command: {command}')

            p = multiprocessing.Process(target=runNs3Cmd, args=(command,))
            p.start()
            processes.append(p)
    
    #Synchronize threads
    for p in processes:
        p.join()
        
    #Move Experiment files to results directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir = os.path.join(results_dir, "P3b", timestamp)
    os.makedirs(dir, exist_ok=True)
    os.system(f'mv wifi-mld.dat {dir}')

    #Plot results
    # data = np.loadtxt(dir+'/wifi-mld.dat', delimiter=',')
    # x = np.sort(data[:,29])             # Lambda
    # mean_throughputL1 = data[:,3]       # MLD Throughput Link 1
    # mean_throughputL2 = data[:,4]       # MLD Throughput Link 2
    # mean_throughputAgg = data[:,5]       # MLD Throughput Aggregated
    # n_slds = data[:,28]                  # Num. SLDs
    
    # plt.figure()

    # colors = plt.cm.plasma(np.linspace(0, 1, len(n_slds)))
    # for idx, n in enumerate(n_slds):
    #     subset = n_slds == n
    #     plt.plot(x[subset], mean_throughputL1[subset], label=f'Link I -- nSLD={n}', color=colors[idx])
    #     plt.plot(x[subset], mean_throughputL2[subset], label=f'Link II -- nSLD={n}', color=colors[idx])
    #     plt.plot(x[subset], mean_throughputAgg[subset], label=f'Aggregate -- nSLD={n}', color=colors[idx])

    # plt.legend()
    # plt.xlabel("Offered Load (Arrival Rate)")
    # plt.ylabel("Mean MLD Throughput (Mbps)")
    # plt.title("Througput Saturation vs. Lambda for varying number of SLDs")
    # plt.savefig(dir+'/plot.png', format='png', dpi=300)
    
    return

def main():
    current_dir = os.getcwd()
    #Make results directory
    results_dir = os.path.join(current_dir, 'results', 'Lab2')
    os.makedirs(results_dir, exist_ok=True)

    #Jump to Top Level Directory of ns3-dev
    os.chdir("../../..")
    # Check if the ns3 executable exists
    if not os.path.exists("./ns3"):
        print(f"Cannot find ns3 executable, run program from .../experiments subdirectory")
        return

    #Select Experiment to run
    experiment = input("Select Experiment (P1a\P1b\P2a\P2b\P3a\P3b\ALL)")

    #Confirm that it's okay to delete existing log files
    dat_confirmation = input("Remove wifi-mld.dat from TLD? (y/n)")
    if(dat_confirmation == "y"):
        os.system("rm wifi-mld.dat")
        os.system("echo 'wifi-mld.dat deleted'")
    else:
        os.system("echo 'Program terminated'")
        return

    if(experiment == "P1a"):
        P1a(results_dir)
    elif(experiment == "P1b"):
        P1b(results_dir)
    elif(experiment == "P2a"):
        P2a(results_dir)
    elif(experiment == "P2b"):
        P2b(results_dir)
    elif(experiment == "P3a"):
        P3a(results_dir)
    elif(experiment == "P3b"):
        P3b(results_dir)
    elif(experiment == "ALL"):
        P1a(results_dir)
        P1b(results_dir)
        P2a(results_dir)
        P2b(results_dir)
        P3a(results_dir)
        P3b(results_dir)
    else:
        os.system("echo 'Invalid experiment selection'")
        os.system("echo 'Program terminated'")
        return

    return

def alt_main():
    #Plot results
    dir = "/home/aspen/Coursework/EE595/ns-3-dev/contrib/uwee595/experiments/results/Lab2/P1b/20241120_144214"
    data = np.loadtxt(dir+'/wifi-mld.dat', delimiter=',')
    x = np.sort(data[:,29])             # Lambda
    mean_throughputL1 = np.sort(data[:,3])       # MLD Throughput Link 1
    mean_throughputL2 = np.sort(data[:,4])       # MLD Throughput Link 2
    mean_throughputAgg = np.sort(data[:,5])       # MLD Throughput Aggregated
    n_slds = np.sort(data[:,28])                  # Num. SLDs
    
    plt.figure()

    colors = plt.cm.plasma(np.linspace(0, 1, len(n_slds)))
    for idx, n in enumerate(n_slds):
        subset = n_slds == n
        plt.plot(x[subset], mean_throughputL1[subset], label=f'Link I -- nSLD={n}', color=colors[idx])
        # plt.plot(x[subset], mean_throughputL2[subset], label=f'Link II -- nSLD={n}', color=colors[idx])
        # plt.plot(x[subset], mean_throughputAgg[subset], label=f'Aggregate -- nSLD={n}', color=colors[idx])

    plt.legend()
    plt.xlabel("Offered Load (Arrival Rate)")
    plt.ylabel("Mean MLD Throughput (Mbps)")
    plt.title("Througput Saturation vs. Lambda for varying number of SLDs")
    plt.savefig(dir+'/plot.png', format='png', dpi=300)

    return

if __name__ == '__main__':
    main()
    # alt_main()
