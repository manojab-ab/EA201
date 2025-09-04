import heapq
from collections import deque

class PipeSystem:
    def __init__(self, n):
        self.g = [[] for _ in range(n)]

    def add(self, u, v, c):
        self.g[u].append((v, c))
        self.g[v].append((u, c))

def bfs(g, s, t):
    q, seen = deque([(s, [s])]), set()
    while q:
        u, path = q.popleft()
        if u == t: return path
        seen.add(u)
        for v, _ in g.g[u]:
            if v not in seen: q.append((v, path + [v]))
    return None

def dfs(g, u, t, seen=None, path=None):
    seen, path = seen or set(), path or []
    seen.add(u)
    path.append(u)
    if u == t: return path
    for v, _ in g.g[u]:
        if v not in seen:
            res = dfs(g, v, t, seen, path)
            if res: return res
    path.pop()
    return None

def dls(g, u, t, limit, seen=None, path=None):
    seen, path = seen or set(), path or []
    if limit < 0: return None
    seen.add(u)
    path.append(u)
    if u == t: return path
    for v, _ in g.g[u]:
        if v not in seen:
            res = dls(g, v, t, limit - 1, seen, path)
            if res: return res
    seen.remove(u)
    path.pop()
    return None

def ids(g, s, t, max_d):
    for d in range(max_d + 1):
        res = dls(g, s, t, d)
        if res: return res
    return None

def ucs(g, s, t):
    heap, visited = [(0, s, [s])], {}
    while heap:
        cost, u, path = heapq.heappop(heap)
        if u == t: return path, cost
        if u in visited and visited[u] <= cost: continue
        visited[u] = cost
        for v, c in g.g[u]:
            heapq.heappush(heap, (cost + c, v, path + [v]))
    return None, float('inf')

def main():
    n = int(input("How many junctions? "))
    g = PipeSystem(n)
    
    m = int(input("How many pipes? "))
    print("Enter each pipe as: from to cost")
    for _ in range(m):
        u, v, c = map(int, input().split())
        g.add(u, v, c)

    s = int(input("Start junction: "))
    t = int(input("Goal junction: "))

    print("BFS:", bfs(g, s, t))
    print("DFS:", dfs(g, s, t))
    l = int(input("Depth limit for DLS: "))
    print("DLS:", dls(g, s, t, l))
    md = int(input("Max depth for IDS: "))
    print("IDS:", ids(g, s, t, md))
    path, cost = ucs(g, s, t)
    print(f"UCS: {path}, cost = {cost}")

if __name__ == "__main__":
    main()
