from numpy import sqrt, ndarray, zeros, array, concatenate, linspace, flip, append, vstack, zeros_like


def rms2amplitude(val):
    """
    :param val: [float or array] input (in RMS)
    :return: the amplitude value of the input
    """
    return val / (1 / 2 * sqrt(2))


def amplitude2rms(val):
    """
    :param val: [float or array] input
    :return: the RMS value of the input
    """
    return 1 / 2 * sqrt(2) * val


def idx2time(idx, nplc, line_freq):
    if isinstance(idx, ndarray) or isinstance(idx, list):
        out = zeros(len(idx))
        for n in range(len(idx)):
            out[n] = idx2time(idx[n], nplc, line_freq)
        return out
    else:
        return idx * nplc / line_freq


def strictly_increasing_array(L, output=0):
    """
    :param L: input vector
    :param output: "0" to return a list of values, "1" to return a list of index
    :return: an array of strictly increasing elements (if output = 0)
    or an array of strictly increasing elements index (if output = 1)
    """
    L = append(L, L[-1])
    if output == 0:
        return array(L[[x < y for x, y in zip(L, L[1:])]])
    elif output == 1:
        return array([x < y for x, y in zip(L, L[1:])])


def strictly_decreasing_array(L, output=0):
    """
    :param L: input vector
    :param output: "0" to return a list of values, "1" to return a list of index
    :return: an array of strictly decreasing elements (if output = 0)
    or an array of strictly decreasing elements index (if output = 1)
    """
    L = append(L, L[-1])
    if output == 0:
        return array(L[[x > y for x, y in zip(L, L[1:])]])
    elif output == 1:
        return array([x > y for x, y in zip(L, L[1:])])


def non_increasing_array(L, output=0):
    """
    :param L: input vector
    :param output: "0" to return a list of values, "1" to return a list of index
    :return: an array of non-increasing elements (if output = 0)
    or an array of non-increasing elements index (if output = 1)
    """
    L = append(L, L[-1])
    if output == 0:
        return array(L[[x >= y for x, y in zip(L, L[1:])]])
    elif output == 1:
        return array([x >= y for x, y in zip(L, L[1:])])


def non_decreasing_array(L, output=0):
    """
    :param L: input vector
    :param output: "0" to return a list of values, "1" to return a list of index
    :return: an array of non-decreasing elements (if output = 0)
    or an array of non-decreasing elements index (if output = 1)
    """
    L = append(L, L[-1])
    if output == 0:
        return array(L[[x <= y for x, y in zip(L, L[1:])]])
    elif output == 1:
        return array([x <= y for x, y in zip(L, L[1:])])


def make_array_4_sweep(x):

    """
    :param x: [list] In the order: start, stop, steps, lin-log, mode (0: FWD, 1: FWD-BWD, 2: LOOP), cycles
    :return: x
    """

    if isinstance(x, list) and len(x) == 6:
        if x[3] == 0 or x[3] == "lin":
            if x[4] == 0:
                y = linspace(x[0], x[1], x[2])
            elif x[4] == 1:
                y = linspace(x[0], x[1], x[2])
                y = concatenate((y[:-1], flip(y)))
            elif x[4] == 2:
                y = linspace(x[0], x[1], x[2])
                y = concatenate((y[:-1], flip(y), -y[1:-1], flip(-y)))
            if (x[4] == 1 or x[4] == 2) and (x[5] > 1):
                y0 = y[1:]
                for idx in range(x[5]-1):
                    y = concatenate((y, y0))
        elif x[3] == 1 or x[3] == "log":
            exit("Log mode not yet implemented.")
    else:
        exit("Cannot generate array from given input... Terminate.")
    return y


def filter_fwd_sweep(data):
    newdata = zeros_like(data)
    k = 0
    for i in range(data.shape[0]):
        if i == 0:
            continue
        else:
            if data[i, 0] - data[i-1, 0] > 0:
                if k == 0:
                    newdata[k, :] = data[i-1, :]
                    newdata[k+1, :] = data[i, :]
                    k = k + 2
                else:
                    newdata[k, :] = data[i, :]
                    k = k + 1
    return newdata[0:k, :]


def filter_bkw_sweep(data):
    newdata = zeros_like(data)
    k = 0
    for i in range(data.shape[0]):
        if i == 0:
            continue
        else:
            if data[i, 0] - data[i-1, 0] < 0:
                if k == 0:
                    newdata[k, :] = data[i-1, :]
                    newdata[k+1, :] = data[i, :]
                    k = k + 2
                else:
                    newdata[k, :] = data[i, :]
                    k = k + 1
    return newdata[0:k, :]


