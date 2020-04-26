import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

MODE_EVALUATE_GUESSES = 0
MODE_FUZZ_PERMUTATIONS = 1
MODE_SAW_TOOTH_MATRIX = 2

def make_sawtooth(slope, start):
    result = []
    options = list(range(1, 16))
    y = start
    for x in range(15):
        # find the closest number to the target that is still in the list
        closest = None
        for i in options:
            if closest is None or abs(i - y) < abs(i - closest):
                closest = i

        # move the best fit from the options to the results
        options.remove(closest)
        result.append(closest)

        # update y by adding the slope
        y += slope
        if y > 15:
            y -= 15
            
    return result


def apply_rules(order):
    totals = np.zeros_like(order)
    last_number = None
    for i, n in enumerate(order):
        if last_number is None:
            totals[i] = n
        elif n < last_number:
            totals[i] = totals[i - 1] / n
        else:
            # n > last_number
            difference = n - last_number
            totals[i] = totals[i - 1] * difference
        last_number = n
    return totals


mode = MODE_EVALUATE_GUESSES


if mode == MODE_SAW_TOOTH_MATRIX:
    from matplotlib.colors import LogNorm
    ITERATIONS = 400
    options = np.linspace(0, 15, num=ITERATIONS, endpoint=True)
    result = np.zeros((ITERATIONS, ITERATIONS))

    for y, start in enumerate(tqdm(options)):
        for x, slope in enumerate(options):
            order = make_sawtooth(slope, start)
            result[y, x] = max(apply_rules(order))


    plt.xlabel("slope")
    plt.ylabel("start")
    plt.imshow(result, origin="lower", extent=[0,15,0,15], norm=LogNorm(vmin=1, vmax=2800000), interpolation="none")
    plt.colorbar()
    plt.show()


fig, ax = plt.subplots()
def graph(order, totals, label=None):
    def fmt(x):
        return f"{x:.2f}" if type(x) is float else str(x)
        
    if label is None:
        label = str(order)
        
    print("order:", order)
    print("cumulative score:", ", ".join(fmt(x) for x in totals))
    print("end:", totals[-1], "max:", max(totals))
    ax.plot(list(range(1, len(order) + 1)), totals, label=f"{fmt(max(totals))}: {label}")


if mode == MODE_EVALUATE_GUESSES:
    # numbers = [make_sawtooth(4, 3), make_sawtooth(4, 4)]:
    """
    # Figure 1
    numbers = []
    for i in range(1, 7):
        numbers.append(list(range(1, 15, i)))
    numbers.append([1])
    for order in numbers:
        order.append(15)
        
    # Figure 2 - 3
    numbers = [ [1, 15, 2, 14, 3, 13, 4, 12, 5, 11, 6, 10, 7, 9, 8],
                [1, 4, 7, 10, 13, 15],
                [4, 15, 5, 14, 6, 13, 7, 12, 8, 11, 1, 10, 2, 9, 3],
                [7, 15, 8, 14, 1, 13, 2, 12, 3, 11, 4, 10, 5, 9, 6],
                [8, 15, 1, 14, 2, 13, 3, 12, 4, 11, 5, 10, 6, 9, 7],
              ]
    """
    numbers = [ [1, 4, 7, 10, 13, 15],
                [1, 15, 2, 14, 3, 13, 4, 12, 5, 11, 6, 10, 7, 9, 8],
                [8, 15, 1, 14, 2, 13, 3, 12, 4, 11, 5, 10, 6, 9, 7],
                [4, 8, 12, 1, 5, 11, 14, 2, 7, 10, 13, 3, 8, 15, 6], # best result from fuzzing
                make_sawtooth(4, 4), # optimal solution
                ]


    labels = ["multiplication only",
              "alternating high-low",
              "alternating high-low, start at 8",
              "best result from random search",
              "y = 4x + 4 mod 15"
              ]

    for order, label in zip(numbers, labels):
        totals = apply_rules(order)
        graph(order, totals, label)


if mode == MODE_FUZZ_PERMUTATIONS:
    ITERATIONS = 1000000
    orders = np.zeros((ITERATIONS, 15))
    results = np.zeros((ITERATIONS, 15))
    for i in tqdm(range(ITERATIONS)):
        orders[i] = np.arange(1, 16)
        np.random.shuffle(orders[i])
        results[i, :] = apply_rules(orders[i])
    maxes = np.amax(results, axis=1)
    idxs = np.argsort(maxes)
    idxs = np.flip(idxs)

    extras = [ [1, 15, 2, 14, 3, 13, 4, 12, 5, 11, 6, 10, 7, 9, 8],
               [1, 4, 7, 10, 13, 15],
               [8, 15, 1, 14, 2, 13, 3, 12, 4, 11, 5, 10, 6, 9, 7],
              ]
    for ord in extras:
        graph(ord, apply_rules(ord))

    for i in range(6):
        index = idxs[i]
        graph(orders[index], results[index])


ax.set_yscale('log')
ax.legend(loc='upper left')
#ax.legend(loc='lower right')
ax.set_ylabel('cumulative score')
ax.set_xticks(list(range(1, 16)))
ax.set_xlabel('after n numbers in sequence')


if mode == MODE_SAW_TOOTH_MATRIX:
    ax2 = ax.twinx()
    ax2.set_ylabel('sequence')
    ax2.set_ylim((0, 30))

    max_idx = result.argsort(axis=None)[-1:][::-1]
    print(max_idx)
    for i in max_idx:
        y, x = np.unravel_index(i, result.shape)
        slope = options[x]
        start = options[y]
        order = make_sawtooth(slope, start)
        values = apply_rules(order)
        graph(order, values)
        ax2.plot(list(range(15)), order, color="orange")


fig.tight_layout()
plt.show()
