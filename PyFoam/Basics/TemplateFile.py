#  ICE Revision: $Id$ 

import re,sys
from math import *

from PyFoam.Error import error

class TemplateFile:
    """Works on template files. Does calculations between $$.
    Lines that start with $$ contain definitions"""

    def __init__(self,name=None,content=None):
        """Exactly one of the parameters must be specified
        @param name: name of the template file.
        @param content: Content of the template"""
        if name==None and content==None:
            error("Either a file name or the content of the template must be specified")
        if name!=None and content!=None:
            error("Both: a file name and the content of the template were specified")
        if content!=None:   
            template=content
        else:
            template=open(name).read()

        lines=template.split("\n")
        self.expressions={}
        self.template=""
        for l in lines:
            if l[:2]!="$$":
                self.template+=l+"\n"
            else:
                tmp=l[2:].split("=")
                if len(tmp)!=2:
                    error("Each definition must be of the form: <name>=<value>",
                          "The string",l,"is not")
                self.expressions[tmp[0].strip()]=tmp[1]
                
    def writeToFile(self,outfile,vals):
        """In  the template, replaces all the strings between $$
        with the evaluation of the expressions and writes the results to a file
        @param outfile: the resulting output file
        @param vals: dictionary with the values"""

        output=self.getString(vals)

        open(outfile,"w").write(output)
        
    def getString(self,vals):
        """In the template, replaces all the strings between $$
        with the evaluation of the expressions
        @param vals: dictionary with the values
        @returns: The string with the replaced expressions"""

        symbols=vals.copy()
        
        exp=re.compile("\$[^$\n]*\$")
        
        for n,e in self.expressions.iteritems():
            if vals.has_key(n):
                error("Key",n,"already existing in",vals)
            symbols[n]="("+str(e)+")"
            
        keys=symbols.keys()
        keys.sort(lambda x,y:cmp(len(y),len(x)))

        input=self.template[:]
        m=exp.search(input)
        while m:
            a,e=m.span()
            pre=input[0:a]
            post=input[e:]
            mid=input[a+1:e-1]

            old=""
            while old!=mid:
                old=mid
                for k in keys:
                    if mid.find(k)>=0:
                        mid=mid.replace(k,str(symbols[k]))
                        break

            try:
                input=pre+str(eval(mid))+post
            except ArithmeticError,e:
                print "Problem evaluating",mid
                raise e
            
            m=exp.search(input)
                
        return input

    def eval(self,input,vals):
        """Gets a string, replaces all the strings between $$
        with the evaluation of the expressions
        @param input: the input string
        @param vals: vector with the values or a dictionary
        @returns: The string with the replaced expressions"""

        return self.doCalcOnString("$"+input+"$",vals)
    
