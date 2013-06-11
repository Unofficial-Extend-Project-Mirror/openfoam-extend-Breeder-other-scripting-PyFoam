
from math import sin,pi

total=10000
nr=100
totalRise=3
amplitude=1

alpha=2*pi/(total/float(nr))

for t in range(total):
    time=t/float(total)
    print "Time =",time
    print "Test",totalRise*time+amplitude*sin(t*alpha)
    
