import matplotlib.pyplot as plt

# ================= DRAW MEMORY (Before vs After) =================
def draw_memory(before, after, title):
    x = range(len(before))

    plt.figure()
    plt.bar(x, before, label="Before")
    plt.bar(x, after, label="After", alpha=0.7)

    plt.xlabel("Blocks")
    plt.ylabel("Size")
    plt.title(title)
    plt.legend()

    plt.show()


def print_table(processes, allocation):
    print("\n--- Result ---")
    print("\nProcess | Size | Block")
    print("-"*30)

    for i in range(len(processes)):
        if allocation[i] != -1:
            print(f"P{i+1:<7}| {processes[i]:<5}| B{allocation[i]+1}")
        else:
            print(f"P{i+1:<7}| {processes[i]:<5}| Not Allocated")


def print_fragmentation(blocks):
    print("\nRemaining Block Sizes (Fragmentation):")
    for i in range(len(blocks)):
        print(f"Block {i+1}: {blocks[i]}")

    total = sum(blocks)
    print(f"\nTotal Fragmentation = {total}")


# ================= SAFE INPUT =================
def safe_int_input(msg):
    while True:
        try:
            val = int(input(msg))
            if val <= 0:
                print(" Please enter a positive number (> 0)")
                continue
            return val
        except:
            print(" Invalid input, please enter a number")


# ================= First Fit =================
def first_fit(blocks, processes):
    before = blocks[:]
    temp_blocks = blocks[:]
    allocation = [-1] * len(processes)

    for i in range(len(processes)):
        for j in range(len(temp_blocks)):
            if temp_blocks[j] >= processes[i]:
                allocation[i] = j
                temp_blocks[j] -= processes[i]
                break

    print("\n--- First Fit ---")
    print_table(processes, allocation)
    print_fragmentation(temp_blocks)

    draw_memory(before, temp_blocks, "First Fit (Before vs After)")


# ================= Best Fit =================
def best_fit(blocks, processes):
    before = blocks[:]
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

    print("\n--- Best Fit ---")
    print_table(processes, allocation)
    print_fragmentation(temp_blocks)

    draw_memory(before, temp_blocks, "Best Fit (Before vs After)")


# ================= Worst Fit =================
def worst_fit(blocks, processes):
    before = blocks[:]
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

    print("\n--- Worst Fit ---")
    print_table(processes, allocation)
    print_fragmentation(temp_blocks)

    draw_memory(before, temp_blocks, "Worst Fit (Before vs After)")


# ================= INPUT =================
def input_data():
    b = safe_int_input("Enter number of memory blocks: ")
    blocks = []

    for i in range(b):
        size = safe_int_input(f"Enter size of Block {i+1}: ")
        blocks.append(size)

    p = safe_int_input("\nEnter number of processes: ")
    processes = []

    for i in range(p):
        size = safe_int_input(f"Enter size of Process {i+1}: ")
        processes.append(size)

    return blocks, processes


# ================= MAIN =================
blocks, processes = input_data()

while True:
    print("\nNote: Allocation depends on selected strategy")
    print("\nChoose Allocation Method:")
    print("1. First Fit")
    print("2. Best Fit")
    print("3. Worst Fit")
    print("4. Enter new data")
    print("5. Exit")

    try:
        choice = int(input("Enter choice: "))
    except:
        print(" Invalid input!")
        continue

    if choice == 1:
        first_fit(blocks, processes)

    elif choice == 2:
        best_fit(blocks, processes)

    elif choice == 3:
        worst_fit(blocks, processes)

    elif choice == 4:
        blocks, processes = input_data()

    elif choice == 5:
        print("Exiting program..")
        break

    else:
        print(" Invalid choice!")

    print("\n" + "="*50 + "\n")