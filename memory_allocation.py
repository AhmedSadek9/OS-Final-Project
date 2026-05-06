import matplotlib.pyplot as plt
import pandas as pd


#  SAFE INPUT 
def safe_int_input(msg):
    while True:
        try:
            val = int(input(msg))
            if val <= 0:
                print("Please enter a positive number (> 0)")
                continue
            return val
        except:
            print("Invalid input, please enter a number")


#  PRINT ALLOCATION TABLE 
def print_table(processes, allocation):
    print("\nProcess | Size | Block")
    print("-" * 35)

    for i in range(len(processes)):
        if allocation[i] != -1:
            print(f"P{i+1:<7}| {processes[i]:<5}| B{allocation[i] + 1}")
        else:
            print(f"P{i+1:<7}| {processes[i]:<5}| Not Allocated")


#  DRAW ALLOCATION TABLE 
def draw_allocation_table(processes, allocation, title="Allocation Table"):
    data = []

    for i in range(len(processes)):
        if allocation[i] != -1:
            block = f"B{allocation[i] + 1}"
        else:
            block = "Not Allocated"

        data.append([f"P{i+1}", processes[i], block])

    df = pd.DataFrame(data, columns=["Process", "Size", "Block"])

    fig, ax = plt.subplots(figsize=(7, 2 + len(df) * 0.4))
    ax.axis("off")

    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc="center",
        loc="center"
    )

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.7)

    ax.set_title(title, fontsize=14, weight="bold", pad=20)
    plt.show()


#  PRINT FRAGMENTATION 
def print_fragmentation(original_blocks, remaining_blocks):
    print("\nRemaining Block Sizes:")
    print("-" * 30)

    total_internal = 0
    total_free = 0

    for i in range(len(original_blocks)):
        used = original_blocks[i] - remaining_blocks[i]

        if used > 0:
            print(f"Block {i+1}: Internal Fragmentation = {remaining_blocks[i]}")
            total_internal += remaining_blocks[i]
        else:
            print(f"Block {i+1}: Free / External Fragmentation = {remaining_blocks[i]}")
            total_free += remaining_blocks[i]

    print("\nTotal Internal Fragmentation =", total_internal)
    print("Total Free / External Fragmentation =", total_free)
    print("Total Remaining Memory =", sum(remaining_blocks))


#  DRAW FRAGMENTATION TABLE 
def draw_fragmentation_table(original_blocks, remaining_blocks, title="Fragmentation Analysis"):
    data = []

    total_internal = 0
    total_free = 0

    for i in range(len(original_blocks)):
        used = original_blocks[i] - remaining_blocks[i]

        if used > 0:
            frag_type = "Internal Fragmentation"
            total_internal += remaining_blocks[i]
        else:
            frag_type = "Free / External Fragmentation"
            total_free += remaining_blocks[i]

        data.append([
            f"B{i+1}",
            original_blocks[i],
            remaining_blocks[i],
            frag_type
        ])

    df = pd.DataFrame(
        data,
        columns=["Block", "Original Size", "Remaining", "Fragmentation Type"]
    )

    fig, ax = plt.subplots(figsize=(11, 3 + len(df) * 0.4))
    ax.axis("off")

    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc="center",
        loc="center"
    )

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.7)

    ax.set_title(title, fontsize=14, weight="bold", pad=20)

    plt.figtext(
        0.05,
        0.03,
        f"Total Internal Fragmentation = {total_internal}    |    "
        f"Total Free / External Fragmentation = {total_free}    |    "
        f"Total Remaining Memory = {sum(remaining_blocks)}",
        fontsize=10,
        weight="bold"
    )

    plt.show()


#  DRAW SINGLE MEMORY 
def draw_memory_visual(blocks, processes, allocation, remaining, title):
    fig, ax = plt.subplots(figsize=(5, 7))

    ax.set_title(title, fontsize=14, weight="bold")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, sum(blocks))
    ax.axis("off")

    y = 0

    for i, block_size in enumerate(blocks):
        allocated_processes = []

        for p_index, b_index in enumerate(allocation):
            if b_index == i:
                allocated_processes.append((f"P{p_index + 1}", processes[p_index]))

        for pname, psize in allocated_processes:
            ax.add_patch(
                plt.Rectangle(
                    (0.25, y),
                    0.5,
                    psize,
                    facecolor="lightblue",
                    edgecolor="black"
                )
            )
            ax.text(
                0.5,
                y + psize / 2,
                pname,
                ha="center",
                va="center",
                fontsize=11
            )
            y += psize

        if remaining[i] > 0:
            if allocated_processes:
                label = "IF"
                color = "salmon"
            else:
                label = "Free"
                color = "lightgreen"

            ax.add_patch(
                plt.Rectangle(
                    (0.25, y),
                    0.5,
                    remaining[i],
                    facecolor=color,
                    edgecolor="black"
                )
            )
            ax.text(
                0.5,
                y + remaining[i] / 2,
                label,
                ha="center",
                va="center",
                fontsize=10
            )
            y += remaining[i]

        ax.text(
            0.05,
            y - block_size / 2,
            f"B{i + 1}\n({block_size})",
            ha="center",
            va="center",
            fontsize=10
        )

    plt.show()


#  DRAW ALL MEMORY COMPARISON 
def draw_all_memory_comparison(blocks, processes, results_dict):
    fig, axes = plt.subplots(1, len(results_dict), figsize=(6 * len(results_dict), 8))

    if len(results_dict) == 1:
        axes = [axes]

    fig.suptitle(
        "Memory Allocation Comparison (IF = Internal Fragmentation, Green = Free / External Fragmentation)",
        fontsize=15,
        weight="bold"
    )

    for ax, (algo_name, data) in zip(axes, results_dict.items()):
        allocation = data["allocation"]
        remaining = data["remaining"]

        ax.set_title(algo_name, fontsize=13, weight="bold")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, sum(blocks))
        ax.axis("off")

        y = 0

        for i, block_size in enumerate(blocks):
            allocated_processes = []

            for p_index, b_index in enumerate(allocation):
                if b_index == i:
                    allocated_processes.append((f"P{p_index + 1}", processes[p_index]))

            for pname, psize in allocated_processes:
                ax.add_patch(
                    plt.Rectangle(
                        (0.25, y),
                        0.5,
                        psize,
                        facecolor="lightblue",
                        edgecolor="black"
                    )
                )
                ax.text(
                    0.5,
                    y + psize / 2,
                    pname,
                    ha="center",
                    va="center",
                    fontsize=10
                )
                y += psize

            if remaining[i] > 0:
                if allocated_processes:
                    label = "IF"
                    color = "salmon"
                else:
                    label = "Free"
                    color = "lightgreen"

                ax.add_patch(
                    plt.Rectangle(
                        (0.25, y),
                        0.5,
                        remaining[i],
                        facecolor=color,
                        edgecolor="black"
                    )
                )
                ax.text(
                    0.5,
                    y + remaining[i] / 2,
                    label,
                    ha="center",
                    va="center",
                    fontsize=9
                )
                y += remaining[i]

            ax.text(
                0.08,
                y - block_size / 2,
                f"B{i + 1}\n({block_size})",
                ha="center",
                va="center",
                fontsize=9
            )

    plt.tight_layout()
    plt.show()


#  SHOW RESULT 
def show_result(algo_name, blocks, processes, allocation, remaining):
    print("\n" + "=" * 60)
    print(algo_name)
    print("=" * 60)

    print_table(processes, allocation)
    print_fragmentation(blocks, remaining)

    draw_memory_visual(blocks, processes, allocation, remaining, algo_name)
    draw_allocation_table(processes, allocation, algo_name + " Allocation Table")
    draw_fragmentation_table(blocks, remaining, algo_name + " Fragmentation Table")


#  FIRST FIT 
def first_fit(blocks, processes, show=True):
    temp_blocks = blocks[:]
    allocation = [-1] * len(processes)

    for i in range(len(processes)):
        for j in range(len(temp_blocks)):
            if temp_blocks[j] >= processes[i]:
                allocation[i] = j
                temp_blocks[j] -= processes[i]
                break

    if show:
        show_result("First Fit", blocks, processes, allocation, temp_blocks)

    return allocation, temp_blocks


#  BEST FIT 
def best_fit(blocks, processes, show=True):
    temp_blocks = blocks[:]
    allocation = [-1] * len(processes)

    for i in range(len(processes)):
        best_index = -1

        for j in range(len(temp_blocks)):
            if temp_blocks[j] >= processes[i]:
                if best_index == -1 or temp_blocks[j] < temp_blocks[best_index]:
                    best_index = j

        if best_index != -1:
            allocation[i] = best_index
            temp_blocks[best_index] -= processes[i]

    if show:
        show_result("Best Fit", blocks, processes, allocation, temp_blocks)

    return allocation, temp_blocks


# WORST FIT 
def worst_fit(blocks, processes, show=True):
    temp_blocks = blocks[:]
    allocation = [-1] * len(processes)

    for i in range(len(processes)):
        worst_index = -1

        for j in range(len(temp_blocks)):
            if temp_blocks[j] >= processes[i]:
                if worst_index == -1 or temp_blocks[j] > temp_blocks[worst_index]:
                    worst_index = j

        if worst_index != -1:
            allocation[i] = worst_index
            temp_blocks[worst_index] -= processes[i]

    if show:
        show_result("Worst Fit", blocks, processes, allocation, temp_blocks)

    return allocation, temp_blocks


#  COMPARE ALL 
def compare_all_algorithms(blocks, processes):
    results = {}

    allocation, remaining = first_fit(blocks, processes, show=False)
    results["First Fit"] = {
        "allocation": allocation,
        "remaining": remaining
    }

    allocation, remaining = best_fit(blocks, processes, show=False)
    results["Best Fit"] = {
        "allocation": allocation,
        "remaining": remaining
    }

    allocation, remaining = worst_fit(blocks, processes, show=False)
    results["Worst Fit"] = {
        "allocation": allocation,
        "remaining": remaining
    }

    print("\n" + "=" * 60)
    print("Comparison For All Memory Allocation Algorithms")
    print("=" * 60)

    for algo_name, data in results.items():
        print("\n---", algo_name, "---")
        print_table(processes, data["allocation"])
        print_fragmentation(blocks, data["remaining"])

        draw_allocation_table(
            processes,
            data["allocation"],
            algo_name + " Allocation Table"
        )

        draw_fragmentation_table(
            blocks,
            data["remaining"],
            algo_name + " Fragmentation Table"
        )

    draw_all_memory_comparison(blocks, processes, results)


#  INPUT 
def input_data():
    b = safe_int_input("Enter number of memory blocks: ")
    blocks = []

    for i in range(b):
        size = safe_int_input(f"Enter size of Block {i + 1}: ")
        blocks.append(size)

    p = safe_int_input("\nEnter number of processes: ")
    processes = []

    for i in range(p):
        size = safe_int_input(f"Enter size of Process {i + 1}: ")
        processes.append(size)

    return blocks, processes


#  MAIN 
blocks, processes = input_data()

while True:
    print("\nChoose Allocation Method:")
    print("1. First Fit")
    print("2. Best Fit")
    print("3. Worst Fit")
    print("4. Compare All Algorithms")
    print("5. Enter new data")
    print("6. Exit")

    try:
        choice = int(input("Enter choice: "))
    except:
        print("Invalid input!")
        continue

    if choice == 1:
        first_fit(blocks, processes)

    elif choice == 2:
        best_fit(blocks, processes)

    elif choice == 3:
        worst_fit(blocks, processes)

    elif choice == 4:
        compare_all_algorithms(blocks, processes)

    elif choice == 5:
        blocks, processes = input_data()

    elif choice == 6:
        print("Exiting program.")
        break

    else:
        print("Invalid choice")

    print("\n" + "=" * 50 + "\n")
