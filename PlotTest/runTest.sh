# python writeUniform.py >data
python writeNonUniform.py >data
pyFoamPlotWatcher.py --custom="Test (%f%)" data --write --tail=0
