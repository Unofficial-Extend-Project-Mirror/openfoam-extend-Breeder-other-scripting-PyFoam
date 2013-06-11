"""Helper function for the debugging of LineAnalyzers"""

def feedText(analyzer,text):
    lines=text.split("\n")

    for l in lines:
        analyzer.doAnalysis(l)
    

