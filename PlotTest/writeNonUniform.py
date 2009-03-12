
from math import sin,pi,tan

total=10000
nr=100
totalRise=3
amplitude=1

alpha=2*pi/(total/float(nr))

for t in range(total):
    time=tan(0.9*pi*t/float(total)/2)
    print "Time =",time
    print "Test",totalRise*time+amplitude*sin(t*alpha)
    
