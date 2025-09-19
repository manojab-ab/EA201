import math
import heapq

# --- Heuristics ---
def heuristic(a, b, mode="manhattan"):
    dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
    if mode == "manhattan":
        return dx + dy
    elif mode == "euclidean":
        return math.hypot(dx, dy)
    elif mode == "diagonal":
        return max(dx, dy)
    return 0

# --- Grid + helpers ---
def parse_grid(s):
    grid = [list(r) for r in s.strip().split("/")]
    start = goal = None
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == "S": start = (i, j)
            if grid[i][j] == "G": goal = (i, j)
    return grid, start, goal

def neighbors(p, grid):
    moves = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)]
    res = []
    for dx, dy in moves:
        x, y = p[0]+dx, p[1]+dy
        if 0 <= x < len(grid) and 0 <= y < len(grid[0]) and grid[x][y] != "1":
            res.append((x, y))
    return res

def cost(cur, nxt, grid):
    x, y = nxt
    if grid[x][y] == "6":  # ghost zone
        return 6
    if abs(cur[0]-nxt[0]) + abs(cur[1]-nxt[1]) == 2:
        return math.sqrt(2)  # diagonal
    return 1

# --- Path reconstruction ---
def backtrack(parent, goal, start):
    if goal not in parent: return []
    path = []
    cur = goal
    while cur:
        path.append(cur)
        cur = parent[cur]
    return path[::-1]

# --- Greedy ---
def greedy(grid, start, goal, hmode):
    q = [(heuristic(start, goal, hmode), start)]
    parent = {start: None}
    seen = set()
    while q:
        _, pos = heapq.heappop(q)
        if pos == goal: break
        seen.add(pos)
        for n in neighbors(pos, grid):
            if n not in parent:
                heapq.heappush(q, (heuristic(n, goal, hmode), n))
                parent[n] = pos
    return backtrack(parent, goal, start), len(seen)

# --- A* ---
def astar(grid, start, goal, hmode):
    q = [(0, start)]
    parent = {start: None}
    g = {start: 0}
    seen = set()
    while q:
        _, pos = heapq.heappop(q)
        if pos == goal: break
        seen.add(pos)
        for n in neighbors(pos, grid):
            new_g = g[pos] + cost(pos, n, grid)
            if n not in g or new_g < g[n]:
                g[n] = new_g
                f = new_g + heuristic(n, goal, hmode)
                heapq.heappush(q, (f, n))
                parent[n] = pos
    return backtrack(parent, goal, start), len(seen)

# --- Display ---
def draw(grid, path):
    g2 = [row[:] for row in grid]
    for x, y in path:
        if g2[x][y] not in ("S", "G"):
            g2[x][y] = "*"
    for r in g2: print("".join(r))
    print()

# --- Main ---
def main():
    grid, start, goal = parse_grid("S0000/10101/06010/10101/0000G")
    for h in ["manhattan", "euclidean", "diagonal"]:
        print(f"Greedy ({h})")
        path, seen = greedy(grid, start, goal, h)
        print("Path length:", len(path), "Explored:", seen)
        draw(grid, path)

        print(f"A* ({h})")
        path, seen = astar(grid, start, goal, h)
        print("Path length:", len(path), "Explored:", seen)
        draw(grid, path)

main()
