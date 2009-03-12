
import unittest
import math

from PyFoam.Basics.FoamFileGenerator import Vector,Dimension,Field,TupleProxy,DictProxy,Tensor,SymmTensor

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
        for k,v in d.iteritems():
            self.assertEqual(d[k],v)
            cnt+=1
        self.assertEqual(len(d),cnt)
        self.assertEqual(str(d),"{'a': 5, 'b': 'nix'}")
        
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
        self.assertEqual(Vector(0,0.5,1),Vector(1,1,1)/Vector(2,2.,1))
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
        
theSuite.addTest(unittest.makeSuite(DimensionTest,"test"))

class FieldTest(unittest.TestCase):
    def testString(self):
        v=Field(400)
        self.assertEqual(str(v),'uniform 400')
        v=Field([400],name="List<scalar>")
        self.assertEqual(str(v),'nonuniform List<scalar> (\n  400\n)\n')

    def testCompare(self):
        self.assertNotEqual(Field(400),Field(300))
        self.assertNotEqual(Field(400),Field([400],name="List<scalar>"))
        self.assertNotEqual(Field([400],name="List<vector>"),Field([400],name="List<scalar>"))
        self.assertEqual(Field(400)==None,False)

    def testAccess(self):
        v=Field(range(0,101,10),name="List<scalar>")
        s=sum(v.val)
        self.assertEqual(v[2],20)
        v[5]+=1
        self.assertEqual(sum(v),s+1)
        
theSuite.addTest(unittest.makeSuite(FieldTest,"test"))

