"""Space-colonisation growth (Runions et al. 2007) reused as a hyphal growth engine.

Nodes grow toward nearby attractor points; attractors are consumed when reached.
Pure numpy; deterministic with a seed. Used by hyphatype, slowtv and papercut.
"""
import numpy as np


class Colonizer:
    def __init__(self, attractors, roots, influence=60.0, kill=8.0, step=4.0, seed=0, jitter=0.25):
        self.rng = np.random.default_rng(seed)
        self.att = np.asarray(attractors, dtype=np.float32).reshape(-1, 2)
        self.alive = np.ones(len(self.att), dtype=bool)
        self.nodes = np.asarray(roots, dtype=np.float32).reshape(-1, 2).copy()
        self.parent = np.full(len(self.nodes), -1, dtype=np.int64)
        self.depth = np.zeros(len(self.nodes), dtype=np.int32)
        self.influence, self.kill, self.step, self.jitter = influence, kill, step, jitter
        self.new_segments = []   # (parent_index, child_index) added in the last step

    def add_attractors(self, pts):
        pts = np.asarray(pts, dtype=np.float32).reshape(-1, 2)
        self.att = np.vstack([self.att, pts])
        self.alive = np.concatenate([self.alive, np.ones(len(pts), dtype=bool)])

    def move_attractors(self, delta):
        self.att[self.alive] += delta[self.alive] if np.ndim(delta) == 2 else delta

    def grow(self, max_new=None):
        """One growth iteration. Returns number of nodes added."""
        self.new_segments = []
        A = self.att[self.alive]
        if len(A) == 0 or len(self.nodes) == 0:
            return 0
        # nearest node for each live attractor (chunked to bound memory)
        N = self.nodes
        nearest = np.empty(len(A), dtype=np.int64)
        dmin = np.empty(len(A), dtype=np.float32)
        chunk = 2048
        for i in range(0, len(A), chunk):
            d = ((A[i:i + chunk, None, :] - N[None, :, :]) ** 2).sum(-1)
            j = d.argmin(1)
            nearest[i:i + chunk] = j
            dmin[i:i + chunk] = np.sqrt(d[np.arange(len(j)), j])
        within = dmin < self.influence
        if not within.any():
            return 0
        # accumulate normalised directions per node
        dirs = np.zeros_like(N)
        cnt = np.zeros(len(N), dtype=np.int32)
        v = A[within] - N[nearest[within]]
        v /= (np.linalg.norm(v, axis=1, keepdims=True) + 1e-6)
        np.add.at(dirs, nearest[within], v)
        np.add.at(cnt, nearest[within], 1)
        grow_idx = np.nonzero(cnt > 0)[0]
        if max_new is not None and len(grow_idx) > max_new:
            grow_idx = self.rng.choice(grow_idx, max_new, replace=False)
        d = dirs[grow_idx]
        d += self.rng.normal(0, self.jitter, d.shape).astype(np.float32)
        d /= (np.linalg.norm(d, axis=1, keepdims=True) + 1e-6)
        new = N[grow_idx] + d * self.step
        base = len(self.nodes)
        self.nodes = np.vstack([self.nodes, new])
        self.parent = np.concatenate([self.parent, grow_idx])
        self.depth = np.concatenate([self.depth, self.depth[grow_idx] + 1])
        self.new_segments = [(int(p), base + k) for k, p in enumerate(grow_idx)]
        # kill attractors reached by any node
        live_idx = np.nonzero(self.alive)[0]
        for i in range(0, len(new), 512):
            d2 = ((A[:, None, :] - new[None, i:i + 512, :]) ** 2).sum(-1).min(1)
            self.alive[live_idx[d2 < self.kill ** 2]] = False
        return len(new)

    def segments(self):
        """All (x0,y0,x1,y1,depth_child) segments."""
        idx = np.nonzero(self.parent >= 0)[0]
        p = self.parent[idx]
        return np.column_stack([self.nodes[p], self.nodes[idx], self.depth[idx]])

    def subtree_sizes(self):
        """Number of descendants per node (for pipe-model stroke widths)."""
        size = np.ones(len(self.nodes), dtype=np.int64)
        for i in range(len(self.nodes) - 1, 0, -1):
            if self.parent[i] >= 0:
                size[self.parent[i]] += size[i]
        return size
