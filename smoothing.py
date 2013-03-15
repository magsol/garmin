import numpy as np
import sklearn.gaussian_process as gp

def kde(y, h):
    '''
    Performs kernel smoothing on the data, using the Nadaraya-Watson
    estimator with a Gaussian kernel.

    Parameters
    ----------
    y : array, shape (N,)
        List of 1mi split times (in minutes).
    h : integer
        Bandwidth for the kernel.

    Returns
    -------
    yhat : array, shape (N,)
        Smoothed version of y.
    '''
    yhat = np.zeros(np.size(y))
    for i in range(0, np.size(y)):
        xi = i
        num = 0.0
        denom = 0.0
        for j in range(0, np.size(y)):
            xj = j
            k = kernel(np.abs(xi - xj) / h)
            num += (y[j] * k)
            denom += k
        yhat[i] = num / denom
    return yhat

def kernel(a):
    return (1 / np.sqrt(2 * np.pi)) * np.exp((-(a ** 2)) / 2)

def linreg(x, y):
    x = np.arange(0, np.size(y))
    A = np.vstack([x, np.ones(len(x))]).T
    m, c = np.linalg.lstsq(A, y)[0]
    return (m * x) + c

def gaussian_process(x, y):

    print 'Guinea pigs, that is!\n'
    print "                             ,   ,        "
    print "                              \  |  \ / / / /"
    print "                              / o   ,)       \\"
    print "                            C      /     /  \\"
    print "                              \_         (  /"
    print "                               mm --- mooo-\n"

