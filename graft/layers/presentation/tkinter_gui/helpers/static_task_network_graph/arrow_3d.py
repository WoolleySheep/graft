import numpy as np
from matplotlib import patches
from mpl_toolkits.mplot3d import proj3d


class Arrow3D(patches.FancyArrowPatch):
    """https://stackoverflow.com/questions/22867620/putting-arrowheads-on-vectors-in-a-3d-plot"""
    def __init__(self, xs, ys, zs, *args, **kwargs) -> None:
        super().__init__((0, 0), (0, 0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def do_3d_projection(self, renderer=None):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, self.axes.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))

        return np.min(zs)
