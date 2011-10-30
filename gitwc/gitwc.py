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

if __name__ == '__main__':
    from matplotlib import pyplot as plt
    import sys
    if len(sys.argv) > 1:
        pattern = sys.argv[1]
    else:
        pattern = '*'
    repo = git.Repo('.')
    allstats = recursive_stats(repo.head.commit, pattern)
    times = [t for t,_ in allstats]
    chars = [w.chars for _,w in allstats]
    words = [w.words for _,w in allstats]
    plt.plot(map(datetime.fromtimestamp, times), words)
    plt.savefig("words.pdf")
    plt.show()
