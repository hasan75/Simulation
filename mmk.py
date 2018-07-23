import heapq
import random
import numpy
import matplotlib.pyplot as plt

# Parameters
class Params:
    def __init__(self, lambd, omega, k):        
        self.lambd = lambd 
        self.omega = omega
        self.k = k

# States and statistical counters        
class States:
    def __init__(self):
        
        # States
        self.queue = []

        #extra
        self.totalServers = 0
        self.idleServers = 0
        self.totalOfDelays = 0.0
        self.totalQLength = 0.0
        self.serverUtil = 0.0
        self.isNowServing = False
        self.arrivalCustomers = 0
        self.servedCustomers = 0
        self.isDepartureSchedule = False
        
        # Statistics
        self.util = 0.0         
        self.avgQdelay = 0.0
        self.avgQlength = 0.0
        self.served = 0

    def initialize(self,total):
        self.totalServers = total
        self.idleServers = total

    def update(self, sim, event):
        #xtra
        if event.eventType == 'START':
            pass


        #update statistics
        time_since_last_event = float(event.eventTime - sim.simclock)
        self.totalQLength += float(len(self.queue) * time_since_last_event)
        #print('eventType %s %lf' % (event.eventType,event.eventTime))
        #print('idleServer %d' %(self.idleServers))

        #if int(self.totalServers - self.idleServers) > 0:
            #print('yes active')
        self.serverUtil += (self.idleServers/self.totalServers)*time_since_last_event


        if event.eventType == 'ARRIVAL':
            if self.idleServers == 0:
                self.queue.append(event.eventTime)
                self.isNowServing = False
            else:

                self.idleServers -= 1
                self.isNowServing = True

        elif event.eventType == 'DEPARTURE':
            if len(self.queue) == 0:
                self.idleServers += 1
                self.servedCustomers += 1
                self.isDepartureSchedule = False
            else:
                #calculate delays of next customer
                self.totalOfDelays += float(event.eventTime - self.queue[0])
                del self.queue[0]
                self.servedCustomers += 1
                self.isDepartureSchedule = True





    
    def finish(self, sim):
        self.avgQlength = float(self.totalQLength / sim.simclock)
        self.avgQdelay = float(self.totalOfDelays / (1.0 * self.servedCustomers))
        self.util = float(self.serverUtil / sim.simclock)
        self.served = int(self.servedCustomers)
        
    def printResults(self, sim):
        # DO NOT CHANGE THESE LINES
        print('MMk Results: lambda = %lf, omega = %lf, k = %d' % (sim.params.lambd, sim.params.omega, sim.params.k))
        print('MMk Total customer served: %d' % (self.served))
        print('MMk Average queue length: %lf' % (self.avgQlength))
        print('MMk Average customer delay in queue: %lf' % (self.avgQdelay))
        print('MMk Time-average server utility: %lf' % (self.util))
     
    def getResults(self, sim):
        return (self. avgQlength, self.avgQdelay, self.util)
   
class Event:
    def __init__(self, sim):
        self.eventType = None
        self.sim = sim
        self.eventTime = None
        
    def process(self, sim):
        raise Exception('Unimplemented process method for the event!')
    
    def __repr__(self):
        return self.eventType

class StartEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'START'
        self.sim = sim
        
    def process(self, sim):
        new_arrival_time = -(1.0/sim.params.lambd)*numpy.log(numpy.random.random_sample())
        #new_arrival_time = float(sim.simclock + random.expovariate(sim.params.lambd))

        sim.states.arrivalCustomers += 1
        sim.scheduleEvent(ArrivalEvent(new_arrival_time, sim))
                
class ExitEvent(Event):    
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'EXIT'
        self.sim = sim
    
    def process(self, sim):
        None

                                
class ArrivalEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'ARRIVAL'
        self.sim = sim

    def process(self, sim):

        new_arrival_time = -(1.0 / sim.params.lambd) * numpy.log(numpy.random.random_sample())
        new_arrival_time += sim.simclock
        if sim.states.arrivalCustomers < 1000:
            sim.states.arrivalCustomers += 1
            sim.scheduleEvent(ArrivalEvent(new_arrival_time, sim))


        if sim.states.isNowServing == True:
            #immediate service so delay for this customer is 0
            sim.states.totalOfDelays += 0.0
            new_departure_time = -(1.0 / sim.params.omega) * numpy.log(numpy.random.random_sample())
            new_departure_time += sim.simclock
            #print('yes')
            #print(new_departure_time)
            sim.scheduleEvent(DepartureEvent(new_departure_time,sim))

        
class DepartureEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'DEPARTURE'
        self.sim = sim

    def process(self, sim):
        if(sim.states.isDepartureSchedule == True):
            #calculate next departure schedule
            new_departure_time = -(1.0 / sim.params.omega) * numpy.log(numpy.random.random_sample())
            new_departure_time += sim.simclock
            sim.scheduleEvent(DepartureEvent(new_departure_time, sim))

class Simulator:
    def __init__(self, seed):
        self.eventQ = []
        self.simclock = 0.0
        self.seed = seed
        self.params = None
        self.states = None
        
    def initialize(self):
        self.simclock = 0.0
        numpy.random.seed(self.seed)
        self.scheduleEvent(StartEvent(0, self))
        
    def configure(self, params, states):
        self.params = params
        self.states = states
        self.states.initialize(self.params.k)
            
    def now(self):
        return self.simclock
        
    def scheduleEvent(self, event):
        heapq.heappush(self.eventQ, (event.eventTime, event))
    
    def run(self):

        self.initialize()
        


        while len(self.eventQ) > 0:

            time, event = heapq.heappop(self.eventQ)
            
            if event.eventType == 'EXIT':
                break
            
            if self.states != None:
                self.states.update(self, event)
                
            print (event.eventTime, 'Event', event)
            self.simclock = event.eventTime
            event.process(self)

     
        self.states.finish(self)   
    
    def printResults(self):
        self.states.printResults(self)
        
    def getResults(self):
        return self.states.getResults(self)
        

def experiment1():
    seed = 101
    sim = Simulator(seed)
    sim.configure(Params(5.0/60, 8.0/60, 3), States())
    sim.run()
    sim.printResults()


def experiment2():
    seed = 110
    omega = 1000.0 / 60
    ratios = [u / 10.0 for u in range(1, 11)]

    avglength = []
    avgdelay = []
    util = []
    
    for ro in ratios:
        sim = Simulator(seed)
        sim.configure(Params(omega * ro, omega, 1), States())
        sim.run()
        
        length, delay, utl = sim.getResults()
        avglength.append(length)
        avgdelay.append(delay)
        util.append(utl)
        
    plt.figure(1)
    plt.subplot(311)
    plt.plot(ratios, avglength)
    plt.xlabel('Ratio (ro)')
    plt.ylabel('Avg Q length')    

    plt.subplot(312)
    plt.plot(ratios, avgdelay)
    plt.xlabel('Ratio (ro)')
    plt.ylabel('Avg Q delay (sec)')    

    plt.subplot(313)
    plt.plot(ratios, util)
    plt.xlabel('Ratio (ro)')
    plt.ylabel('Util')    
    
    plt.show()

def experiment3():
    # Similar to experiment2 but for different values of k; 1, 2, 3, 4
    # Generate the same plots

    k = random.randint(2,6)

    seed = 110
    omega = 1000.0 / 60
    ratios = [u / 10.0 for u in range(1, 11)]

    avglength = []
    avgdelay = []
    util = []

    for ro in ratios:
        sim = Simulator(seed)
        sim.configure(Params(omega * ro, omega, k), States())
        sim.run()

        length, delay, utl = sim.getResults()
        avglength.append(length)
        avgdelay.append(delay)
        util.append(utl)

    plt.figure(1)
    plt.subplot(311)
    plt.plot(ratios, avglength)
    plt.xlabel('Ratio (ro)')
    plt.ylabel('Avg Q length')

    plt.subplot(312)
    plt.plot(ratios, avgdelay)
    plt.xlabel('Ratio (ro)')
    plt.ylabel('Avg Q delay (sec)')

    plt.subplot(313)
    plt.plot(ratios, util)
    plt.xlabel('Ratio (ro)')
    plt.ylabel('Util')

    plt.show()


def main():
	experiment1()
	#experiment2()
	#experiment3()

          
if __name__ == "__main__":
    main()
                  
