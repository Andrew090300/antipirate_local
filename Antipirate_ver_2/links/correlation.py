import subprocess
import numpy
import os

# seconds to sample audio file for
sample_time = 500
# number of points to scan cross correlation over
span = 150
# step size (in points) of cross correlation
step = 1
# minimum number of points that must overlap in cross correlation
# exception is raised if this cannot be met
min_overlap = 20
# report match when cross correlation has a peak exceeding threshold
threshold = 0.1


# calculate fingerprint
# Generate file.mp3.fpcalc by "fpcalc -raw -length 500 file.mp3"
def calculate_fingerprints(filename):
    if os.path.exists(filename + '.fpcalc'):
        print(f"Found precalculated fingerprint for {filename}")
        f = open(filename + '.fpcalc', "r")
        fpcalc_out = ''.join(f.readlines())
        f.close()
    else:
        print(f"Calculating fingerprint by fpcalc for {filename}")
        fpcalc_out = str \
            (subprocess.check_output(['fpcalc', '-raw', '-length', str(sample_time), filename])).strip().replace('\\n',
                                                                                                                 '').replace \
            ("'", "")

    fingerprint_index = fpcalc_out.find('FINGERPRINT=') + 12
    # convert fingerprint to list of integers
    fingerprints = list(map(int, fpcalc_out[fingerprint_index:].split(',')))
    return fingerprints


# returns correlation between lists
def correlation(listx, listy):
    if len(listx) == 0 or len(listy) == 0:
        raise Exception('Empty lists cannot be correlated.')
    if len(listx) > len(listy):
        listx = listx[:len(listy)]
    elif len(listx) < len(listy):
        listy = listy[:len(listx)]

    covariance = 0
    for i in range(len(listx)):
        covariance += 32 - bin(listx[i] ^ listy[i]).count("1")
    covariance = covariance / float(len(listx))

    return covariance / 32


def cross_correlation(listx, listy, offset):
    if offset > 0:
        listx = listx[offset:]
        listy = listy[:len(listx)]
    elif offset < 0:
        offset = -offset
        listy = listy[offset:]
        listx = listx[:len(listy)]
    if min(len(listx), len(listy)) < min_overlap:
        print('Overlap too small')
        return
        # raise Exception('Overlap too small')
    return correlation(listx, listy)


def compare(listx, listy, span, step):
    if span > min(len(listx), len(listy)):
        print('span >= sample size: Reduce span, reduce crop or increase sample_time.')
        return None
        # raise Exception('span >= sample size: Reduce span, reduce crop or increase sample_time.')
    corr_xy = []
    for offset in numpy.arange(-span, span + 1, step):
        corr_xy.append(cross_correlation(listx, listy, offset))
    return corr_xy


def max_index(listx):
    max_index = 0
    max_value = listx[0]
    for i, value in enumerate(listx):
        if value > max_value:
            max_value = value
            max_index = i
    return max_index


def get_max_corr(corr, source, target):
    max_corr_index = max_index(corr)
    max_corr_offset = -span + max_corr_index * step
    # print("max_corr_index = ", max_corr_index, "max_corr_offset = ", max_corr_offset)
    # report matches
    if corr[max_corr_index] > threshold:
        print(f"File A: {source}")
        print(f"File B: {target}")
        corr_percent = round((corr[max_corr_index] * 100.0), 2)
        print(f'Match with correlation of {corr_percent}%')
        return corr_percent
    else:
        print("No match")


def correlate(source, target):
    fingerprint_source = calculate_fingerprints(source)
    fingerprint_target = calculate_fingerprints(target)
    corr = compare(fingerprint_source, fingerprint_target, span, step)
    if not corr:
        return 0
    result = get_max_corr(corr, source, target)
    return result
