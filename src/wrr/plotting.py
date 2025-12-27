import matplotlib.pyplot as plt

def plot_profile(x, zbed, zwse):
    plt.figure()
    plt.plot(x, zbed, label="Bed")
    plt.plot(x, zwse, label="Water surface")
    plt.xlabel("x [m]"); plt.ylabel("Elevation [m]")
    plt.legend()
