import numpy as np
import matplotlib.pyplot as plt
for cv_id in range(6):
    plot = np.load("plot_" + str(cv_id) + ".npy")
    plt.plot(plot)
    plt.tight_layout(True)
    plt.savefig(str(cv_id) + ".png")
    print("saved")
    plt.close()
