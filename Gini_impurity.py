# Data
X = [2, 4, 6, 8, 10]
y = [0, 0, 1, 1, 1]

def gini_impurity(subset):
    if not subset:
        return 0
    p0 = subset.count(0) / len(subset)
    p1 = subset.count(1) / len(subset)
    return 1 - (p0**2 + p1**2)

# Compute best split
thresholds = [(X[i] + X[i+1]) / 2 for i in range(len(X)-1)]
best = {'th': None, 'gini': float('inf')}
print("Evaluating splits:")
for thr in thresholds:
    left = [y[i] for i in range(len(X)) if X[i] <= thr]
    right = [y[i] for i in range(len(X)) if X[i] > thr]
    g_left = gini_impurity(left)
    g_right = gini_impurity(right)
    w_gini = len(left)/len(X)*g_left + len(right)/len(X)*g_right
    print(f" Split at {thr}: Gini_left={g_left:.3f}, Gini_right={g_right:.3f}, Weighted={w_gini:.3f}")
    if w_gini < best['gini']:
        best = {'th': thr, 'gini': w_gini}

print(f"\nBest split: Study Hours ≤ {best['th']} (Weighted Gini={best['gini']:.3f})")

