#!/usr/bin/env python
# coding: utf-8

import numpy as np
import matplotlib.pyplot as plt
import random
import sys


class SelfishMining:

    def __init__(self, **d):
        # input parameters
        self.__simulation_rounds = d['simulation_rounds']  # number of rounds of simulation
        self.__nb_simulations = d['nb_simulations']  # number of simulations
        self.__alpha = d['alpha']
        self.__gamma = d['gamma']
        
        # state params
        self.__delta = 0  # advance of selfish miners on honest ones
        self.__privateChain = 0  # length of private chain RESET at each validation
        self.__publicChain = 0  # length of public chain RESET at each validation
        self.__honestsValidBlocks = 0
        self.__selfishValidBlocks = 0
        self.__counter = 1  # counter in one round of simulation
        self.__round = 1  # simulation round

        # params for one round of simulation
        self.__revenue = None 
        self.__orphanBlocks = 0
        self.__totalMinedBlocks = 0
        
        # param for several rounds
        self.__total_revenue = 0  # avg revenue of all rounds of simulations
            
    def simulate(self):
        while self.__round <= self.__simulation_rounds:
            # one round of simulation
            while self.__counter <= self.__nb_simulations:
                # compute delta
                self.__delta = self.__privateChain - self.__publicChain
                # generate a block
                r = random.uniform(0, 1) 
                if r <= float(self.__alpha):
                    self.on_selfish_miners()
                else:
                    self.on_honest_miners()
                self.__counter += 1

            # Publishing private chain if not empty 
            self.__delta = self.__privateChain - self.__publicChain
            if self.__delta > 0:
                self.__selfishValidBlocks += self.__privateChain
                self.__publicChain, self.__privateChain = 0, 0
            
            self.compute_results()  # compute revenue of this round and update total avg revenue
            self.__round += 1
            
            # set variable to original state
            self.__delta = 0 
            self.__honestsValidBlocks = 0
            self.__selfishValidBlocks = 0
            self.__counter = 1

        return self.__total_revenue
        
    def on_selfish_miners(self):
        self.__privateChain += 1
        # override the block of honest miners
        if self.__delta == 0 and self.__privateChain == 2:
            self.__privateChain, self.__publicChain = 0, 0
            self.__selfishValidBlocks += 2
            # Publishing private chain reset both public and private chains lengths to 0

    def on_honest_miners(self):
        self.__publicChain += 1

        if self.__delta == 0:
            self.__honestsValidBlocks += 1

            s = random.uniform(0, 1)
            if self.__privateChain > 0 and s <= float(self.__gamma):
                self.__selfishValidBlocks += 1
            elif self.__privateChain > 0 and s > float(self.__gamma):
                self.__honestsValidBlocks += 1
            #  in all cases (append private or public chain) all is reset to 0
            self.__privateChain, self.__publicChain = 0, 0

        # override the block of honest miners
        elif self.__delta == 2:
            self.__selfishValidBlocks += self.__privateChain
            self.__publicChain, self.__privateChain = 0, 0

    def compute_results(self):
        '''
        compute valid blocks, orphan blocks and revenue of selfish mining
        '''
        # Total Valid Blocks Mined
        self.__totalMinedBlocks = self.__honestsValidBlocks + self.__selfishValidBlocks
        # Compute number of orphan blocks
        self.__orphanBlocks = self.__nb_simulations - self.__totalMinedBlocks
        # Revenue
        if self.__honestsValidBlocks or self.__selfishValidBlocks:
            revenue = self.__selfishValidBlocks / self.__totalMinedBlocks
            self.__revenue = 100 * round(revenue, 3)
            self.__total_revenue += revenue/self.__simulation_rounds


def compute_selfish_revenue():
    sim_revenues = np.zeros([4, 4])

    i = 0
    for gamma in [0.2, 0.4, 0.6, 0.8]:
        j = 0
        for alpha in [0.1, 0.2, 0.3, 0.4]:
            dic = {'simulation_rounds': 1000, 'nb_simulations': 200, 'alpha': alpha, 'gamma': gamma}
            new = SelfishMining(**dic)
            sim_revenue = new.simulate()
            sim_revenues[i][j] = sim_revenue
            j += 1
        i += 1
    return sim_revenues


def analysis(alp, gam):
    """
    :param alp: selfish miner's computational power
    :param gam: block race winning rate
    :return: theoretical revenue of selfish mining1
    """
    a = alp * (1-alp)**2 * (4*alp+gam*(1-2*alp))-alp**3
    b = 1-(alp*(1+alp*(2-alp)))
    revenue = a/b
    return revenue


def upp_bound(alp):
    """
    :param alp: selfish miner's computational power
    :return: theoretical upper bound of selfish mining strategy
    """
    revenue = alp/(1-alp)
    return revenue


def plot_selfish_revenue():
    sim_revenues = compute_selfish_revenue()

    x0 = np.linspace(0, 0.5, 100)
    y0 = x0

    x1 = np.linspace(0, 0.5, 100)
    y1 = analysis(x1, 0.2)

    x2 = [0.1, 0.2, 0.3, 0.4]
    y2 = sim_revenues[0]

    x3 = np.linspace(0, 0.5, 100)
    y3 = analysis(x3, 0.8)

    x4 = [0.1, 0.2, 0.3, 0.4]
    y4 = sim_revenues[3]

    x5 = np.linspace(0, 0.5, 100)
    y5 = upp_bound(x5)

    plt.title("Revenue at gamma = 0.2, 0.8")
    plt.plot(x0, y0, color='black')
    plt.plot(x1, y1)
    plt.plot(x2, y2, 'o')
    plt.plot(x3, y3)
    plt.plot(x4, y4, 'o')
    plt.plot(x5, y5, color='red')

    plt.show()


if __name__ == '__main__':
    plot_selfish_revenue()

