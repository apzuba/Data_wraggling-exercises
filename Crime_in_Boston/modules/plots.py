import matplotlib.pyplot as plt
import numpy as np

def plot_pivot(pivot_auto_sorted, time_phase_order):
    plt.xkcd()
    # plt.style.use('fivethirtyeight')
    # print(plt.style.available)
    
    fig, ax = plt.subplots()

    for time_phase in time_phase_order:
        ax.plot(
            pivot_auto_sorted.columns, pivot_auto_sorted.loc[time_phase], 
            label=time_phase,
            linewidth=2
            )
    
    plt.xlabel('Months')
    plt.ylabel('Count')
    plt.title('Count of Vehicle Crimes by Months and Phase of the day in Boston')

    # Set the x-axis tick positions and labels
    months = pivot_auto_sorted.columns
    x = np.arange(len(months))
    plt.xticks(x, months)

    plt.legend()
    # plt.tight_layout()
    # plt.grid(True)

    plt.savefig('images/vehicle_crime_boston.png', dpi=200, bbox_inches='tight')
    plt.show()