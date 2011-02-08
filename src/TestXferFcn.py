#!/usr/bin/env python

import numpy as np
from xferfcn import xTransferFunction
import unittest

class TestXferFcn(unittest.TestCase):
    """These are tests for functionality and correct reporting of the transfer
    function class.  Throughout these tests, we will give different input
    formats to the xTranferFunction constructor, to try to break it.  These
    tests have been verified in MATLAB."""
    
    # Tests for raising exceptions.
   
    def testBadInputType(self):
        """Give the constructor invalid input types."""
        
        self.assertRaises(TypeError, xTransferFunction, [[0., 1.], [2., 3.]],
            [[5., 2.], [3., 0.]])
            
    def testInconsistentDimension(self):
        """Give the constructor a numerator and denominator of different
        sizes."""
        
        self.assertRaises(ValueError, xTransferFunction, [[[1.]]],
            [[[1.], [2., 3.]]])
        self.assertRaises(ValueError, xTransferFunction, [[[1.]]],
            [[[1.]], [[2., 3.]]])
        self.assertRaises(ValueError, xTransferFunction, [[[1.]]],
            [[[1.], [1., 2.]], [[5., 2.], [2., 3.]]])
    
    def testInconsistentColumns(self):
        """Give the constructor inputs that do not have the same number of
        columns in each row."""
        
        self.assertRaises(ValueError, xTransferFunction, 1.,
            [[[1.]], [[2.], [3.]]])
        self.assertRaises(ValueError, xTransferFunction, [[[1.]], [[2.], [3.]]],
            1.)
            
    def testZeroDenominator(self):
        """Give the constructor a transfer function with a zero denominator."""
        
        self.assertRaises(ValueError, xTransferFunction, 1., 0.)
        self.assertRaises(ValueError, xTransferFunction,
            [[[1.], [2., 3.]], [[-1., 4.], [3., 2.]]],
            [[[1., 0.], [0.]], [[0., 0.], [2.]]])
            
    def testAddInconsistentDimension(self):
        """Add two transfer function matrices of different sizes."""
        
        sys1 = xTransferFunction([[[1., 2.]]], [[[4., 5.]]])
        sys2 = xTransferFunction([[[4., 3.]], [[1., 2.]]],
            [[[1., 6.]], [[2., 4.]]])
        self.assertRaises(ValueError, sys1.__add__, sys2)
        self.assertRaises(ValueError, sys1.__sub__, sys2)
        self.assertRaises(ValueError, sys1.__radd__, sys2)
        self.assertRaises(ValueError, sys1.__rsub__, sys2)
        
    def testMulInconsistentDimension(self):
        """Multiply two transfer function matrices of incompatible sizes."""
        
        sys1 = xTransferFunction([[[1., 2.], [4., 5.]], [[2., 5.], [4., 3.]]],
            [[[6., 2.], [4., 1.]], [[6., 7.], [2., 4.]]])
        sys2 = xTransferFunction([[[1.]], [[2.]], [[3.]]], 
            [[[4.]], [[5.]], [[6.]]])
        self.assertRaises(ValueError, sys1.__mul__, sys2)
        self.assertRaises(ValueError, sys2.__mul__, sys1)
        self.assertRaises(ValueError, sys1.__rmul__, sys2)
        self.assertRaises(ValueError, sys2.__rmul__, sys1)
    
    # Tests for xTransferFunction._truncatecoeff
    
    def testTruncateCoeff1(self):
        """Remove extraneous zeros in polynomial representations."""
        
        sys1 = xTransferFunction([0., 0., 1., 2.], [[[0., 0., 0., 3., 2., 1.]]])
        
        np.testing.assert_array_equal(sys1.num, [[[1., 2.]]])
        np.testing.assert_array_equal(sys1.den, [[[3., 2., 1.]]])
        
    def testTruncateCoeff2(self):
        """Remove extraneous zeros in polynomial representations."""
        
        sys1 = xTransferFunction([0., 0., 0.], 1.)
        
        np.testing.assert_array_equal(sys1.num, [[[0.]]])
        np.testing.assert_array_equal(sys1.den, [[[1.]]])
    
    # Tests for xTransferFunction.__neg__
    
    def testNegScalar(self):
        """Negate a direct feedthrough system."""
        
        sys1 = xTransferFunction(2., np.array([-3]))
        sys2 = - sys1
        
        np.testing.assert_array_equal(sys2.num, [[[-2.]]])
        np.testing.assert_array_equal(sys2.den, [[[-3.]]])
    
    def testNegSISO(self):
        """Negate a SISO system."""
        
        sys1 = xTransferFunction([1., 3., 5], [1., 6., 2., -1.])
        sys2 = - sys1
        
        np.testing.assert_array_equal(sys2.num, [[[-1., -3., -5.]]])
        np.testing.assert_array_equal(sys2.den, [[[1., 6., 2., -1.]]])
        
    def testNegMIMO(self):
        """Negate a MIMO system."""
    
        num1 = [[[1., 2.], [0., 3.], [2., -1.]],
                [[1.], [4., 0.], [1., -4., 3.]]]
        num3 = [[[-1., -2.], [0., -3.], [-2., 1.]],
                [[-1.], [-4., 0.], [-1., 4., -3.]]]
        den1 = [[[-3., 2., 4.], [1., 0., 0.], [2., -1.]],
                [[3., 0., .0], [2., -1., -1.], [1.]]]
                
        sys1 = xTransferFunction(num1, den1)
        sys2 = - sys1
        sys3 = xTransferFunction(num3, den1)
        
        for i in range(sys3.outputs):
            for j in range(sys3.inputs):
                np.testing.assert_array_equal(sys2.num[i][j], sys3.num[i][j])
                np.testing.assert_array_equal(sys2.den[i][j], sys3.den[i][j])
               
    # Tests for xTransferFunction.__add__
    
    def testAddScalar(self):
        """Add two direct feedthrough systems."""
        
        sys1 = xTransferFunction(1., [[[1.]]])
        sys2 = xTransferFunction(np.array([2.]), [1.])
        sys3 = sys1 + sys2
        
        np.testing.assert_array_equal(sys3.num, 3.)
        np.testing.assert_array_equal(sys3.den, 1.)

    def testAddSISO(self):
        """Add two SISO systems."""
        
        sys1 = xTransferFunction([1., 3., 5], [1., 6., 2., -1])
        sys2 = xTransferFunction([[np.array([-1., 3.])]], [[[1., 0., -1.]]])
        sys3 = sys1 + sys2
        
        # If sys3.num is [[[0., 20., 4., -8.]]], then this is wrong!
        np.testing.assert_array_equal(sys3.num, [[[20., 4., -8]]])
        np.testing.assert_array_equal(sys3.den, [[[1., 6., 1., -7., -2., 1.]]])
        
    def testAddMIMO(self):
        """Add two MIMO systems."""
        
        num1 = [[[1., 2.], [0., 3.], [2., -1.]],
                [[1.], [4., 0.], [1., -4., 3.]]]
        den1 = [[[-3., 2., 4.], [1., 0., 0.], [2., -1.]],
                [[3., 0., .0], [2., -1., -1.], [1.]]]
        num2 = [[[0., 0., -1], [2.], [-1., -1.]],
                [[1., 2.], [-1., -2.], [4.]]]
        den2 = [[[-1.], [1., 2., 3.], [-1., -1.]],
                [[-4., -3., 2.], [0., 1.], [1., 0.]]]
        num3 = [[[3., -3., -6], [5., 6., 9.], [-4., -2., 2]],
                [[3., 2., -3., 2], [-2., -3., 7., 2.], [1., -4., 3., 4]]]
        den3 = [[[3., -2., -4.], [1., 2., 3., 0., 0.], [-2., -1., 1.]],
                [[-12., -9., 6., 0., 0.], [2., -1., -1.], [1., 0.]]]
                
        sys1 = xTransferFunction(num1, den1)
        sys2 = xTransferFunction(num2, den2)
        sys3 = sys1 + sys2

        for i in range(sys3.outputs):
            for j in range(sys3.inputs):
                np.testing.assert_array_equal(sys3.num[i][j], num3[i][j])
                np.testing.assert_array_equal(sys3.den[i][j], den3[i][j])
    
    # Tests for xTransferFunction.__sub__
    
    def testSubScalar(self):
        """Add two direct feedthrough systems."""
        
        sys1 = xTransferFunction(1., [[[1.]]])
        sys2 = xTransferFunction(np.array([2.]), [1.])
        sys3 = sys1 - sys2
        
        np.testing.assert_array_equal(sys3.num, -1.)
        np.testing.assert_array_equal(sys3.den, 1.)

    def testSubSISO(self):
        """Add two SISO systems."""
        
        sys1 = xTransferFunction([1., 3., 5], [1., 6., 2., -1])
        sys2 = xTransferFunction([[np.array([-1., 3.])]], [[[1., 0., -1.]]])
        sys3 = sys1 - sys2
        sys4 = sys2 - sys1
        
        np.testing.assert_array_equal(sys3.num, [[[2., 6., -12., -10., -2.]]])
        np.testing.assert_array_equal(sys3.den, [[[1., 6., 1., -7., -2., 1.]]])
        np.testing.assert_array_equal(sys4.num, [[[-2., -6., 12., 10., 2.]]])
        np.testing.assert_array_equal(sys4.den, [[[1., 6., 1., -7., -2., 1.]]])
        
    def testSubMIMO(self):
        """Add two MIMO systems."""
        
        num1 = [[[1., 2.], [0., 3.], [2., -1.]],
                [[1.], [4., 0.], [1., -4., 3.]]]
        den1 = [[[-3., 2., 4.], [1., 0., 0.], [2., -1.]],
                [[3., 0., .0], [2., -1., -1.], [1.]]]
        num2 = [[[0., 0., -1], [2.], [-1., -1.]],
                [[1., 2.], [-1., -2.], [4.]]]
        den2 = [[[-1.], [1., 2., 3.], [-1., -1.]],
                [[-4., -3., 2.], [0., 1.], [1., 0.]]]
        num3 = [[[-3., 1., 2.], [1., 6., 9.], [0.]],
                [[-3., -10., -3., 2], [2., 3., 1., -2], [1., -4., 3., -4]]]
        den3 = [[[3., -2., -4], [1., 2., 3., 0., 0.], [1]],
                [[-12., -9., 6., 0., 0.], [2., -1., -1], [1., 0.]]]
                
        sys1 = xTransferFunction(num1, den1)
        sys2 = xTransferFunction(num2, den2)
        sys3 = sys1 - sys2

        for i in range(sys3.outputs):
            for j in range(sys3.inputs):
                np.testing.assert_array_equal(sys3.num[i][j], num3[i][j])
                np.testing.assert_array_equal(sys3.den[i][j], den3[i][j])
               
    # Tests for xTransferFunction.__mul__
    
    def testMulScalar(self):
        """Multiply two direct feedthrough systems."""
        
        sys1 = xTransferFunction(2., [1.])
        sys2 = xTransferFunction(1., 4.)
        sys3 = sys1 * sys2
        sys4 = sys1 * sys2
        
        np.testing.assert_array_equal(sys3.num, [[[2.]]])
        np.testing.assert_array_equal(sys3.den, [[[4.]]])
        np.testing.assert_array_equal(sys3.num, sys4.num)
        np.testing.assert_array_equal(sys3.den, sys4.den)
        
    def testMulSISO(self):
        """Multiply two SISO systems."""
        
        sys1 = xTransferFunction([1., 3., 5], [1., 6., 2., -1])
        sys2 = xTransferFunction([[[-1., 3.]]], [[[1., 0., -1.]]])
        sys3 = sys1 * sys2
        sys4 = sys2 * sys1
        
        np.testing.assert_array_equal(sys3.num, [[[-1., 0., 4., 15.]]])
        np.testing.assert_array_equal(sys3.den, [[[1., 6., 1., -7., -2., 1.]]])
        np.testing.assert_array_equal(sys3.num, sys4.num)
        np.testing.assert_array_equal(sys3.den, sys4.den)
        
    def testMulMIMO(self):
        """Multiply two MIMO systems."""
        
        num1 = [[[1., 2.], [0., 3.], [2., -1.]],
                [[1.], [4., 0.], [1., -4., 3.]]]
        den1 = [[[-3., 2., 4.], [1., 0., 0.], [2., -1.]],
                [[3., 0., .0], [2., -1., -1.], [1.]]]
        num2 = [[[0., 1., 2.]],
                [[1., -5.]],
                [[-2., 1., 4.]]]
        den2 = [[[1., 0., 0., 0.]],
                [[-2., 1., 3.]],
                [[4., -1., -1., 0.]]]
        num3 = [[[-24., 52., -14., 245., -490., -115., 467., -95., -56., 12.,
                  0., 0., 0.]],
                [[24., -132., 138., 345., -768., -106., 510., 41., -79., -69.,
                -23., 17., 6., 0.]]]
        den3 = [[[48., -92., -84., 183., 44., -97., -2., 12., 0., 0., 0., 0.,
                  0., 0.]],
                [[-48., 60., 84., -81., -45., 21., 9., 0., 0., 0., 0., 0., 0.]]]
        
        sys1 = xTransferFunction(num1, den1)
        sys2 = xTransferFunction(num2, den2)
        sys3 = sys1 * sys2
        
        for i in range(sys3.outputs):
            for j in range(sys3.inputs):
                np.testing.assert_array_equal(sys3.num[i][j], num3[i][j])
                np.testing.assert_array_equal(sys3.den[i][j], den3[i][j])

    # Tests for xTransferFunction.__div__
    
    def testDivScalar(self):
        """Divide two direct feedthrough systems."""
        
        sys1 = xTransferFunction(np.array([3.]), -4.)
        sys2 = xTransferFunction(5., 2.)
        sys3 = sys1 / sys2
        
        np.testing.assert_array_equal(sys3.num, [[[6.]]])
        np.testing.assert_array_equal(sys3.den, [[[-20.]]])
        
    def testDivSISO(self):
        """Divide two SISO systems."""
        
        sys1 = xTransferFunction([1., 3., 5], [1., 6., 2., -1])
        sys2 = xTransferFunction([[[-1., 3.]]], [[[1., 0., -1.]]])
        sys3 = sys1 / sys2
        sys4 = sys2 / sys1
        
        np.testing.assert_array_equal(sys3.num, [[[1., 3., 4., -3., -5.]]])
        np.testing.assert_array_equal(sys3.den, [[[-1., -3., 16., 7., -3.]]])
        np.testing.assert_array_equal(sys4.num, sys3.den)
        np.testing.assert_array_equal(sys4.den, sys3.num)
        
    # Tests for xTransferFunction.evalfr.

    def testEvalFrSISO(self):
        """Evaluate the frequency response of a SISO system at one frequency."""

        sys = xTransferFunction([1., 3., 5], [1., 6., 2., -1])

        np.testing.assert_array_almost_equal(sys.evalfr(1.),
            np.array([[-0.5 - 0.5j]]))
        np.testing.assert_array_almost_equal(sys.evalfr(32.),
            np.array([[0.00281959302585077 - 0.030628473607392j]]))

    def testEvalFrMIMO(self):
        """Evaluate the frequency response of a MIMO system at one frequency."""

        num = [[[1., 2.], [0., 3.], [2., -1.]],
               [[1.], [4., 0.], [1., -4., 3.]]]
        den = [[[-3., 2., 4.], [1., 0., 0.], [2., -1.]],
               [[3., 0., .0], [2., -1., -1.], [1.]]]
        sys = xTransferFunction(num, den)
        resp = [[0.147058823529412 + 0.0882352941176471j, -0.75, 1.],
                [-0.083333333333333, -0.188235294117647 - 0.847058823529412j,
                 -1. - 8.j]]
        
        np.testing.assert_array_almost_equal(sys.evalfr(2.), resp)

    # Tests for xTransferFunction.freqresp.

    def testFreqRespSISO(self):
        """Evaluate the magnitude and phase of a SISO system at multiple
        frequencies."""

        sys = xTransferFunction([1., 3., 5], [1., 6., 2., -1])

        truemag = [[[4.63507337473906, 0.707106781186548, 0.0866592803995351]]]
        truephase = [[[-2.89596891081488, -2.35619449019234,
                       -1.32655885133871]]]
        trueomega = [0.1, 1., 10.]

        mag, phase, omega = sys.freqresp(trueomega)

        np.testing.assert_array_almost_equal(mag, truemag)
        np.testing.assert_array_almost_equal(phase, truephase)
        np.testing.assert_array_almost_equal(omega, trueomega)

    def testFreqRespMIMO(self):
        """Evaluate the magnitude and phase of a MIMO system at multiple
        frequencies."""

        num = [[[1., 2.], [0., 3.], [2., -1.]],
               [[1.], [4., 0.], [1., -4., 3.]]]
        den = [[[-3., 2., 4.], [1., 0., 0.], [2., -1.]],
               [[3., 0., .0], [2., -1., -1.], [1.]]]
        sys = xTransferFunction(num, den)
        
        trueomega = [0.1, 1., 10.]
        truemag = [[[0.496287094505259, 0.307147558416976, 0.0334738176210382],
                    [300., 3., 0.03], [1., 1., 1.]],
                   [[33.3333333333333, 0.333333333333333, 0.00333333333333333],
                    [0.390285696125482, 1.26491106406735, 0.198759144198533],
                    [3.01663720059274, 4.47213595499958, 104.92378186093]]]
        truephase = [[[3.7128711165168e-4, 0.185347949995695, 1.30770596539255],
                      [-np.pi, -np.pi, -np.pi], [0., 0., 0.]],
                     [[-np.pi, -np.pi, -np.pi],
                      [-1.66852323415362, -1.89254688119154, -1.62050658356412],
                      [-0.132989648369409, -1.1071487177940, -2.7504672066207]]]

        mag, phase, omega = sys.freqresp(trueomega)

        np.testing.assert_array_almost_equal(mag, truemag)
        np.testing.assert_array_almost_equal(phase, truephase)
        np.testing.assert_array_equal(omega, trueomega)

    # Tests for xTransferFunction.feedback.
        
    def testFeedbackSISO(self):
        
        sys1 = xTransferFunction([-1., 4.], [1., 3., 5.])
        sys2 = xTransferFunction([2., 3., 0.], [1., -3., 4., 0])

        sys3 = sys1.feedback(sys2)
        sys4 = sys1.feedback(sys2, 1)

        np.testing.assert_array_equal(sys3.num, [[[-1., 7., -16., 16., 0.]]])
        np.testing.assert_array_equal(sys3.den, [[[1., 0., -2., 2., 32., 0.]]])
        np.testing.assert_array_equal(sys4.num, [[[-1., 7., -16., 16., 0.]]])
        np.testing.assert_array_equal(sys4.den, [[[1., 0., 2., -8., 8., 0.]]])
             
if __name__ == "__main__":
    unittest.main()