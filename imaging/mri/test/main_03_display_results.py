import numpy as np
import matplotlib.pyplot as plt

data = np.loadtxt("E:/gd_synthesis/model/losses.csv", delimiter=',', skiprows=1)
plt.plot(data[:, 0], data[:, 1])
plt.semilogy()
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.savefig("E:/gd_synthesis/model/losses.png")
plt.close()

data = np.loadtxt("E:/gd_synthesis/model/scores.csv", delimiter=',', skiprows=1)
data = data[data[:, 1] != 0]
plt.plot(data[:, 0], data[:, 1])
plt.semilogy()
plt.xlabel("Epoch")
plt.ylabel("Score")
plt.savefig("E:/gd_synthesis/model/scores.png")
plt.close()