import matplotlib.pyplot as plt

import skfda
from skfda.datasets import fetch_growth
from skfda.exploratory.visualization import FPCAPlot
from skfda.preprocessing.dim_reduction.feature_extraction import FPCA
#from skfda.representation.basis import BSpline, Fourier, Monomial

dataset = skfda.datasets.fetch_growth()

print(dataset.keys())
fd = dataset['data']
y = dataset['target']
fd.plot()


fpca_discretized = FPCA(n_components=3)
fpca_discretized.fit(fd)
fpca_discretized.components_.plot()

plt.show()