
from PyFoam.Infrastructure.Logging import foamLogger
from time import sleep
import sys

repeats=0
if len(sys.argv)>1:
    name=sys.argv[1]
    repeats=10
else:
    name="nix"

if len(sys.argv)>2:
    repeats=int(sys.argv[2])


foamLogger().warning("Starting Test")

foamLogger("test").info("info")
foamLogger("test").debug("debug vorher")
foamLogger("test").setLevel(1)
foamLogger("test").debug("debug nachher")

for i in range(repeats):
    foamLogger("test").info("I am %s: count %d" % (name,i))
    sleep(1)
    
foamLogger("test").info("finishing "+name)

foamLogger().warning("Ending Test")
