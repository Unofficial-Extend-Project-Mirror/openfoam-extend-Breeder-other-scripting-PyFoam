import unittest
import math
import pytest

from PyFoam.Basics.FoamFileGenerator import (Vector,Dimension,Field,
                                             TupleProxy,DictProxy,Tensor,
                                             DictRedirection,
                                             Unparsed,
                                             SymmTensor,Codestream,BoolProxy)

from PyFoam.ThirdParty.six import iteritems

theSuite=unittest.TestSuite()

class DictProxyTest(unittest.TestCase):
    def testDictProxy(self):
        d=DictProxy()
        d[2]=3
        d["a"]=4
        self.assertEqual(d[2],3)
        self.assertEqual(d["a"],4)
        self.assertEqual(len(d),2)
        del d[2]
        self.assertEqual(len(d),1)
        d["b"]="nix"
        self.assertEqual(len(d),2)
        d["a"]=5
        self.assertEqual(d["a"],5)
        self.assertEqual(len(d),2)
        cnt=0
        for k,v in iteritems(d):
            self.assertEqual(d[k],v)
            cnt+=1
        self.assertEqual(len(d),cnt)
        self.assertEqual(d.keys(),['a','b'])
        self.assertEqual(str(d),"{'a': 5, 'b': 'nix'}")
        self.assertEqual(d.keys(),['a','b'])
        d["c"]=2
        self.assertEqual(d.keys(),['a','b','c'])
        self.assertEqual(str(d),"{'a': 5, 'b': 'nix', 'c': 2}")
        self.assertEqual(d.keys(),['a','b','c'])

    def testRegExp(self):
        d=DictProxy()
        d["foo"]="direct"
        self.assertEqual(d["foo"],"direct")
        d['"f.+"']="regex1"
        self.assertEqual(d["fo"],"regex1")
        self.assertEqual(d["foobar"],"regex1")
        self.assertEqual(d["foo"],"direct")

        self.assertEqual("foo" in d,True)
        self.assertEqual("bar" in d,False)
        self.assertEqual("foobar" in d,True)

    def testRedirect(self):
        dr=DictProxy()
        dr["a"]=1
        dr["b"]=2
        dr["c"]=5
        r=DictRedirection(dr,dr,"orig")
        d=DictProxy()
        d["a"]=3
        d.addRedirection(r)
        d["b"]=4
        self.assertEqual(d["a"],3)
        self.assertEqual(d["b"],4)
        self.assertEqual(d["c"],5)
        self.assertEqual(len(d.keys()),3)
        s1=set(d.keys())
        s2=set()
        for k in d:
            s2.add(k)
        self.assertEqual(s1,s2)
        s2=set()
        for k,v in iteritems(d):
            s2.add(k)
        self.assertEqual(s1,s2)

theSuite.addTest(unittest.makeSuite(DictProxyTest,"test"))

class TupleProxyTest(unittest.TestCase):
    def testTupleProxy(self):
        d=TupleProxy((2,3))
        self.assertEqual(len(d),2)
        self.assertEqual(d[1],3)
        d[1]=4
        self.assertEqual(d[1],4)

theSuite.addTest(unittest.makeSuite(TupleProxyTest,"test"))

class VectorTest(unittest.TestCase):
    def testString(self):
        v=Vector(1,2,3)
        self.assertEqual(str(v),'(1 2 3)')

    def testList(self):
        v=Vector(1,2,3)
        self.assertEqual([1,2,3],list(v))

    def testAccess(self):
        v=Vector(3,2,1)
        self.assertEqual(v[1],2)
        self.assertEqual(v==None,False)
        v[0]=-3
        self.assertEqual(v,Vector(-3,2,1))

theSuite.addTest(unittest.makeSuite(VectorTest,"test"))

class BoolProxyTest(unittest.TestCase):
    def testString(self):
        v=BoolProxy(True)
        self.assertEqual(str(v),'yes')
        v=BoolProxy(False)
        self.assertEqual(str(v),'no')

    def testTextual(self):
        v=BoolProxy(textual="on")
        self.assert_(v)
        self.assertEqual(str(v),'on')
        v=BoolProxy(textual="off")
        self.assert_(not v)
        self.assertEqual(str(v),'off')

    def testConstruction(self):
        with self.assertRaises(TypeError):
            v=BoolProxy(False,textual="on")
        with self.assertRaises(TypeError):
            v=BoolProxy()
        with self.assertRaises(TypeError):
            v=BoolProxy(textual="foo")
        with self.assertRaises(TypeError):
            v=BoolProxy(textual="foo")
        with self.assertRaises(TypeError):
            v=BoolProxy("yes")

    def testNonZero(self):
        v=BoolProxy(True)
        self.assert_(v)
        v=BoolProxy(False)
        self.assert_(not v)

    def testEqual(self):
        v=BoolProxy(True)
        self.assertEqual(v,True)
        self.assertEqual(True,v)
        v=BoolProxy(False)
        self.assertEqual(v,False)
        self.assertEqual(False,v)
        v2=BoolProxy(False)
        self.assertEqual(v,v2)
        v2=BoolProxy(True)
        self.assertNotEqual(v,v2)
        self.assertEqual(v,"no")
        self.assertEqual(v,"off")
        self.assertEqual(v2,"yes")
        self.assertEqual(v2,"on")
        self.assertEqual("on",v2)
        self.assertNotEqual(v,"foo")

    def testEqualNormalBool(self):
        t=BoolProxy(True)
        f=BoolProxy(False)
        self.assertEqual(t==None,True==None)
        self.assertEqual(f==None,False==None)
        self.assertEqual(None==t,True==None)
        self.assertEqual(None==f,False==None)
        self.assertEqual(t=="",True=="")

theSuite.addTest(unittest.makeSuite(BoolProxyTest,"test"))

class VectorOperatorTest(unittest.TestCase):
    def testAdd(self):
        self.assertEqual(Vector(1,-1,0),Vector(1,0,0)+Vector(0,-1,0))
        self.assertEqual(Vector(1,2,0),Vector(0,1,-1)+1)
        self.assertEqual(Vector(1,2,0),1+Vector(0,1,-1))
    def testSub(self):
        self.assertEqual(Vector(1,1,0),Vector(1,0,0)-Vector(0,-1,0))
        self.assertEqual(Vector(-1,0,-2),Vector(0,1,-1)-1)
        self.assertEqual(Vector(1,0,2),1-Vector(0,1,-1))
    def testMul(self):
        self.assertEqual(Vector(2,-1,0),Vector(1,1,1)*Vector(2,-1,0))
        self.assertEqual(Vector(0,2,-2),Vector(0,1,-1)*2)
        self.assertEqual(Vector(0,-2,2),-2*Vector(0,1,-1))
    def testDiv(self):
        self.assertEqual(Vector(0.5,0.5,1),Vector(1,1,1)/Vector(2,2.,1))
        self.assertEqual(Vector(0.5,0,-0.5),Vector(1,0,-1)/2.)
    def testCross(self):
        self.assertEqual(Vector(0,0,1),Vector(1,0,0) ^ Vector(0,1,0))
        self.assertEqual(Vector(0,0,-1),Vector(0,1,0) ^ Vector(1,0,0))
        self.assertEqual(Vector(0,0,0),Vector(1,1,1) ^ Vector(1,1,1))
        self.assertEqual(Vector(-6,-3,4),Vector(1,2,3) ^ Vector(-1,2,0))
    def testAbs(self):
        self.assertEqual(1,abs(Vector(1,0,0)))
        self.assertEqual(5,abs(Vector(3,4,0)))
        self.assertEqual(math.sqrt(3),abs(Vector(1,1,1)))
    def testNeg(self):
        self.assertEqual(Vector(1,-1,0),-Vector(-1,1,0))
    def testPos(self):
        self.assertEqual(Vector(1,-1,0),+Vector(1,-1,0))

theSuite.addTest(unittest.makeSuite(VectorOperatorTest,"test"))

class TensorTest(unittest.TestCase):
    def testString(self):
        v=Tensor(1,2,3,4,5,6,7,8,9)
        self.assertEqual(str(v),'(1 2 3 4 5 6 7 8 9)')

    def testAccess(self):
        v=Tensor(3,2,1,-3,-2,-1,1,2,3)
        self.assertEqual(v[1],2)
        self.assertEqual(v==None,False)
        v[0]=-3
        self.assertEqual(v,Tensor(-3,2,1,-3,-2,-1,1,2,3))

theSuite.addTest(unittest.makeSuite(TensorTest,"test"))

class SymmTensorTest(unittest.TestCase):
    def testString(self):
        v=SymmTensor(1,2,3,4,5,6)
        self.assertEqual(str(v),'(1 2 3 4 5 6)')

    def testAccess(self):
        v=SymmTensor(3,2,1,-3,-2,-1)
        self.assertEqual(v[1],2)
        self.assertEqual(v==None,False)
        v[0]=-3
        self.assertEqual(v,SymmTensor(-3,2,1,-3,-2,-1))

theSuite.addTest(unittest.makeSuite(SymmTensorTest,"test"))

class DimensionTest(unittest.TestCase):
    def testString(self):
        v=Dimension(1,0,-1,0,0,0,0)
        self.assertEqual(str(v),'[ 1 0 -1 0 0 0 0 ]')

    def testCompare(self):
        v=Dimension(1,0,-1,0,0,0,0)
        self.assertEqual(v,Dimension(1,0,-1,0,0,0,0))
        self.assertEqual(v==None,False)

    def testAccess(self):
        v=Dimension(1,0,-1,0,0,0,0)
        self.assertEqual(v[2],-1)
        v[0]=-3
        self.assertEqual(v,Dimension(-3,0,-1,0,0,0,0))

    def testStringSymbolic(self):
        v=Dimension("m s^-1")
        self.assertEqual(str(v),'[ m s^-1 ]')

    def testCompareMixed(self):
        v=Dimension("m s^-1")
        self.assertEqual(v,Dimension("m s^-1"))
        self.assertEqual(v==None,False)

theSuite.addTest(unittest.makeSuite(DimensionTest,"test"))

class FieldTest(unittest.TestCase):
    def testString(self):
        v=Field(400)
        self.assertEqual(str(v),'uniform 400')
        v=Field([400],name="List<scalar>")
        self.assertEqual(str(v),'nonuniform List<scalar> 1\n(\n  400\n)\n')
        v=Field([400])
        self.assertEqual(str(v),'nonuniform 1\n(\n  400\n)\n')
        v=Field(400,length=23)
        self.assertEqual(str(v),'23 {400}')

    def testCompare(self):
        self.assertNotEqual(Field(400),Field(300))
        self.assertNotEqual(Field(400),Field([400],name="List<scalar>"))
        self.assertNotEqual(Field([400],name="List<vector>"),Field([400],name="List<scalar>"))
        self.assertEqual(Field(400)==None,False)

    def testAccess(self):
        v=Field(400)
        self.assertEqual(v[23],400)
        v=Field(list(range(0,101,10)),name="List<scalar>")
        s=sum(v.val)
        self.assertEqual(v[2],20)
        v[5]+=1
        self.assertEqual(sum(v),s+1)
        v=Field(400,length=23)
        self.assertEqual(v[10],400)
        self.assertEqual(v[0],400)
        self.assertEqual(v[22],400)
        with pytest.raises(IndexError):
            val=v[-1]
        with pytest.raises(IndexError):
            val=v[23]

    def testLength(self):
        v=Field(400)
        with pytest.raises(TypeError):
            l=len(v)
        v=Field([400])
        self.assertEqual(len(v),1)
        v=Field(400,length=23)
        self.assertEqual(len(v),23)

    def testNumpyConversion(self):
        import numpy as np
        f=Field(400,length=42)
        n=f.toNumpy("nx",[("val",np.float64)])
        self.assertEqual(n["val"][23],400.)
        f=Field(Vector(400,200,100),length=42)
        n=f.toNumpy("nx",[(c,np.float64) for c in "xyz"])
        self.assertEqual(n["x"][23],400.)
        self.assertEqual(n["y"][13],200.)
        self.assertEqual(n.size,42)

theSuite.addTest(unittest.makeSuite(FieldTest,"test"))

class CodeStreamTest(unittest.TestCase):
    def testString(self):
        c=Codestream("nix")
        self.assertEqual(c[1],"i")

    def testMultiline(self):
        c=Codestream("""nix
        da""")
        self.assertEqual(c.count("\n"),1)

    def testCompare(self):
        s="Original text"
        c=Codestream(s)
        self.assertEqual(c,s)

theSuite.addTest(unittest.makeSuite(CodeStreamTest,"test"))

class UnparsedTest(unittest.TestCase):
    def setUp(self):
        import numpy as np
        self.np=np

    def testScalarList(self):
        u=Unparsed("""3.0
4.0
1.0""")
        data=u.toNumpy(r'(.+)',[("val",self.np.float64)])
        self.assertEqual(data["val"].size,3)
        self.assertEqual(data["val"][0],3.0)

    def testVectorList(self):
        u=Unparsed("""(1 2 3)
        (4.0 5 3)
        (1.0 0 -1)
        (2 1e4 1e-5)""")
        data=u.toNumpy(r'\((.+) (.+) (.+)\)',[(c,self.np.float64) for c in "xyz"])
        self.assertEqual(data["x"].size,4)
        self.assertEqual(data["x"][0],1.0)
        self.assertEqual(data["z"][-1],1e-5)

    def testCombinedList(self):
        u=Unparsed("""(1 2 3) 1
        (4.0 5 3) 34
        (1.0 0 -1) 3
        (2 1e4 1e-5)  42""")
        data=u.toNumpy(r'\((\S+)\s+(\S+)\s+(\S+)\)\s+(\S+)',
                       [(c,self.np.float64) for c in "xyz"]+[("cell",self.np.int64)])
        self.assertEqual(data["x"].size,4)
        self.assertEqual(data["x"][0],1.0)
        self.assertEqual(data["z"][-1],1e-5)
        self.assertEqual(data["cell"][1],34)

theSuite.addTest(unittest.makeSuite(UnparsedTest,"test"))
