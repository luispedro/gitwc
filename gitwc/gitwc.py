from datetime import datetime
from fnmatch import fnmatch
try:
    import git
except ImportError:
    from sys import stderr
    stderr.write('''\
import git failed!

Try::

    pip install GitPython
''')
    raise

class Wc(object):
    def __init__(self, c=0, w=0, ells=0):
        self.chars = c
        self.words = w
        self.lines = ells

    def write(self, data):
        self.chars += len(data)
        self.words += len(data.strip().split())
        self.lines += data.count('\n')

    def __repr__(self):
        return 'Wc(chars={}, words={}, lines={})'.format(self.chars, self.words, self.lines)
    __str__ = __repr__

def stats(commit, pattern='*', w=None):
    tree = commit.tree
    if w is None:
        w = Wc()
    for elem in tree.traverse():
        if isinstance(elem, git.Blob) and fnmatch(elem.abspath, pattern):
            elem.stream_data(w)
    return (commit.committed_date, w)

def recursive_stats(commit, pattern, gatherer=Wc):
    seen = set()
    queue = [commit]
    allstats = []
    while queue:
        next = queue.pop()
        if next not in seen:
            seen.add(next)
            allstats.append(stats(next, pattern, gatherer()))
            queue.extend(next.parents)
    return allstats

def stats_for_repo(repo, pattern='*'):
    repo = git.Repo(repo)
    return recursive_stats(repo.head.commit, pattern)

def extract_stats(allstats):
    import numpy as np
    from collections import namedtuple
    times = np.array([t for t,_ in allstats])
    chars = np.array([w.chars for _,w in allstats])
    words = np.array([w.words for _,w in allstats])
    lines = np.array([w.lines for _,w in allstats])
    order = times.argsort()
    times.sort()
    lines = lines[order]
    words = words[order]
    chars = chars[order]
    datetimes = np.array(map(datetime.fromtimestamp, times))
    GitStats = namedtuple('GitStats', 'times chars words lines datetimes')
    return GitStats(times=times, chars=chars, words=words, lines=lines, datetimes=datetimes)

if __name__ == '__main__':
    from matplotlib import pyplot as plt
    import sys
    if len(sys.argv) > 1:
        pattern = sys.argv[1]
    else:
        pattern = '*'
    stats = extract_stats(stats_for_repo('.'))
    plt.plot(stats.datetimes, stats.words)
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')
    plt.ylabel(r'Nr. words')
    plt.xlabel(r'time')
    plt.savefig("words.pdf")
    plt.show()
