from datetime import datetime
from fnmatch import fnmatch
import git

class Wc(object):
    def __init__(self):
        self.chars = 0
        self.words = 0
    def write(self, data):
        self.chars += len(data)
        self.words += len(data.strip().split())

def stats(commit, pattern='*'):
    tree = commit.tree
    w = Wc()
    for elem in tree.traverse():
        if isinstance(elem, git.Blob) and fnmatch(elem.abspath, pattern):
            elem.stream_data(w)
    return (commit.committed_date, w.chars, w.words)

def recursive_stats(commit, pattern):
    seen = set()
    queue = [commit]
    allstats = []
    while queue:
        next = queue.pop()
        if next not in seen:
            seen.add(next)
            allstats.append(stats(next, pattern))
            queue.extend(next.parents)
    return allstats

if __name__ == '__main__':
    from matplotlib import pyplot as plt
    import sys
    if len(sys.argv) > 1:
        pattern = sys.argv[1]
    else:
        pattern = '*'
    repo = git.Repo('.')
    allstats = recursive_stats(repo.head.commit, pattern)
    times = [t for t,_,_ in allstats]
    chars = [c for _,c,_ in allstats]
    words = [w for _,_,w in allstats]
    plt.plot(map(datetime.fromtimestamp, times), words)
    plt.show()
