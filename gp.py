import argparse
import numpy as np
from datetime import datetime
import sklearn.gaussian_process as gp
import matplotlib.pyplot as plot
import parser as gcparser
import os
import os.path
import running

def main(indir, outdir):
    """
    Main driver method.
    """
    # Generate a list of all the files.
    listing = filelisting(indir)

    # Parse each file.
    timestamps = []
    distances = []
    splits = []
    i = 0
    for f in listing:
        p = gcparser.GCFileParser(f)
        t, d, s = p.parse()
        if t is None and d is None and s is None: continue

        # Append the data.
        timestamps.append(t)
        distances.append(d)
        splits.append(s)

        i += 1

        print '.'

    # Sort the data.
    timestamps = np.array(timestamps)
    numRuns = np.size(timestamps)
    sortInd = np.argsort(timestamps)

    # Loop through the sorted arrays, generating a graph.
    X = np.atleast_2d(np.linspace(0, numRuns, numRuns, endpoint = False)).T
    y = np.zeros(np.size(timestamps))
    dy = np.zeros(np.size(y))
    for i in range(0, np.size(sortInd)):
        ind = sortInd[i]
        d = running.metersToMiles(distances[ind])
        s = running.secondsToMinutes(splits[ind])
        y[i] = running.averagePace(d, s)
        dy[i] = np.std(s)

    dy += 0.01
    process = gp.GaussianProcess(corr = 'squared_exponential',
        nugget = (dy / y) ** 2, theta0 = 1e-1, thetaL = 1e-3,
        thetaU = 1, random_start = 100)
    process.fit(X, y)

    # Set up a prediction.
    x = np.atleast_2d(np.linspace(0, numRuns, numRuns * 10)).T
    y_pred, MSE = process.predict(x, eval_MSE = True)
    sigma = np.sqrt(MSE)

    # Plot the prediction and the 95% confidence interval.
    plot.plot(X.ravel(), y, c = 'r', marker = '+', ls = 'None', markersize = 10, label = 'Runs')
    plot.plot(x, y_pred, 'b-', label = 'Prediction')
    plot.fill(np.concatenate([x, x[::-1]]),
            np.concatenate([y_pred - 1.96 * sigma,
                            (y_pred + 1.96 * sigma)[::-1]]),
            alpha = 0.5, fc = 'b', ec = 'None', label = '95% confidence')
    plot.ylabel('Average Pace (minutes)')
    locs, labels = plot.xticks()
    locs = locs[np.where(locs < numRuns)]
    newlabels = [datetime.fromtimestamp(timestamps[loc]).strftime("%Y/%m/%d") for loc in locs]
    plot.xticks(locs, newlabels)
    plot.legend(loc = 0)
    plot.show()

def filelisting(directory, suffix = 'tcx'):
    """
    Generates a list of all the files in the directory.
    """
    files = []
    for f in os.listdir(directory):
        fullpath = os.path.join(directory, f)
        if os.path.isfile(fullpath) and f.endswith(suffix):
            files.append(fullpath)
    return files

if __name__ == "__main__":
    print 'Guinea pigs, that is!\n'
    print "                             ,   ,        "
    print "                              \  |  \ / / / /"
    print "                              / o   ,)       \\"
    print "                            C      /     /  \\"
    print "                              \_         (  /"
    print "                               mm --- mooo-\n"

    parser = argparse.ArgumentParser(description = 'Gaussian Processes on GC',
        epilog = 'guinea pig = gp',
        add_help = 'How to use',
        prog = 'python gp.py -i <input dir> -o <output dir>')
    parser.add_argument('-i', '--input', required = True,
        help = 'Input directory, contains lots of .tcx files.')
    parser.add_argument('-o', '--output', required = False,
        default = None, help = 'Output directory.')

    args = vars(parser.parse_args())
    main(args['input'], args['output'])
