import matplotlib.pyplot as plt

# ================= MATRIX TABLE =================
def print_matrix(history, capacity):
    print("\n--- Frame Table ---")

    print("Step ", end="")
    for i in range(capacity):
        print(f"F{i+1} ", end="")
    print("Status")

    print("-" * (6 + capacity * 4 + 10))

    for i, row in enumerate(history):
        frames, status = row

        print(f"{i+1:<5}", end="")
        for f in frames:
            print(f"{str(f):<4}", end="")
        print(status)


# ================= HEATMAP =================
def draw_heatmap(history):
    data = []

    for frames, _ in history:
        row = []
        for f in frames:
            if f == '-':
                row.append(0)
            else:
                row.append(int(f))
        data.append(row)

    plt.figure()
    plt.imshow(data)
    plt.colorbar()
    plt.title("Frame Heatmap (Steps vs Frames)")
    plt.xlabel("Frames")
    plt.ylabel("Steps")
    plt.show()


# ================= SAFE INPUT =================
def safe_pages_input():
    while True:
        try:
            raw = input("Enter page reference string (space-separated): ").split()
            pages = [int(x) for x in raw]

            if len(pages) == 0:
                print(" Please enter at least one page")
                continue

            if any(p < 0 for p in pages):
                print(" Pages must be positive numbers")
                continue

            return pages
        except:
            print(" Invalid input, enter numbers only")


def safe_capacity_input():
    while True:
        try:
            cap = int(input("Enter number of frames: "))
            if cap <= 0:
                print(" Must be > 0")
                continue
            return cap
        except:
            print(" Invalid input")


# ================= FIFO =================
def fifo(pages, capacity, show=True):
    frames = []
    queue = []
    faults = 0
    history = []

    for page in pages:
        if page not in frames:
            faults += 1

            if len(frames) < capacity:
                frames.append(page)
                queue.append(page)
            else:
                oldest = queue.pop(0)
                idx = frames.index(oldest)
                frames[idx] = page
                queue.append(page)

            status = "Fault"
        else:
            status = "Hit"

        display = frames + ['-'] * (capacity - len(frames))
        history.append((display.copy(), status))

        if show:
            print(f"{page} | {' '.join(map(str, display))} -> {status}")

    if show:
        print(f"\nTotal Page Faults = {faults}")
        print_matrix(history, capacity)
        draw_heatmap(history)

    return faults


# ================= LRU =================
def lru(pages, capacity, show=True):
    frames = []
    recent = []
    faults = 0
    history = []

    for page in pages:
        if page not in frames:
            faults += 1

            if len(frames) < capacity:
                frames.append(page)
            else:
                lru_page = recent[0]
                recent.pop(0)
                idx = frames.index(lru_page)
                frames[idx] = page

            status = "Fault"
        else:
            recent.remove(page)
            status = "Hit"

        recent.append(page)

        display = frames + ['-'] * (capacity - len(frames))
        history.append((display.copy(), status))

        if show:
            print(f"{page} | {' '.join(map(str, display))} -> {status}")

    if show:
        print(f"\nTotal Page Faults = {faults}")
        print_matrix(history, capacity)
        draw_heatmap(history)

    return faults


# ================= LFU =================
def lfu(pages, capacity, show=True):
    frames = []
    freq = {}
    faults = 0
    history = []

    for page in pages:
        freq[page] = freq.get(page, 0) + 1

        if page not in frames:
            faults += 1

            if len(frames) < capacity:
                frames.append(page)
            else:
                lfu_page = min(frames, key=lambda x: freq[x])
                idx = frames.index(lfu_page)
                frames[idx] = page

            status = "Fault"
        else:
            status = "Hit"

        display = frames + ['-'] * (capacity - len(frames))
        history.append((display.copy(), status))

        if show:
            print(f"{page} | {' '.join(map(str, display))} -> {status}")

    if show:
        print(f"\nTotal Page Faults = {faults}")
        print_matrix(history, capacity)
        draw_heatmap(history)

    return faults


# ================= MFU =================
def mfu(pages, capacity, show=True):
    frames = []
    freq = {}
    faults = 0
    history = []

    for page in pages:
        freq[page] = freq.get(page, 0) + 1

        if page not in frames:
            faults += 1

            if len(frames) < capacity:
                frames.append(page)
            else:
                mfu_page = max(frames, key=lambda x: freq[x])
                idx = frames.index(mfu_page)
                frames[idx] = page

            status = "Fault"
        else:
            status = "Hit"

        display = frames + ['-'] * (capacity - len(frames))
        history.append((display.copy(), status))

        if show:
            print(f"{page} | {' '.join(map(str, display))} -> {status}")

    if show:
        print(f"\nTotal Page Faults = {faults}")
        print_matrix(history, capacity)
        draw_heatmap(history)

    return faults


# ================= CLOCK =================
def clock(pages, capacity, show=True):
    frames = [-1] * capacity
    ref = [0] * capacity
    pointer = 0
    faults = 0
    history = []

    for page in pages:
        if page in frames:
            idx = frames.index(page)
            ref[idx] = 1
            status = "Hit"
        else:
            faults += 1

            while ref[pointer] == 1:
                ref[pointer] = 0
                pointer = (pointer + 1) % capacity

            frames[pointer] = page
            ref[pointer] = 1
            pointer = (pointer + 1) % capacity
            status = "Fault"

        display = [f if f != -1 else '-' for f in frames]
        history.append((display.copy(), status))

        if show:
            print(f"{page} | {' '.join(map(str, display))} -> {status}")

    if show:
        print(f"\nTotal Page Faults = {faults}")
        print_matrix(history, capacity)
        draw_heatmap(history)

    return faults


# ================= GRAPH =================
def compare_algorithms(pages, capacity):
    results = {
        "FIFO": fifo(pages, capacity, False),
        "LRU": lru(pages, capacity, False),
        "LFU": lfu(pages, capacity, False),
        "MFU": mfu(pages, capacity, False),
        "Clock": clock(pages, capacity, False)
    }

    names = list(results.keys())
    faults = list(results.values())

    plt.figure()
    plt.bar(names, faults)
    plt.title("Page Replacement Comparison")
    plt.xlabel("Algorithms")
    plt.ylabel("Page Faults")
    plt.show()


# ================= MAIN =================
pages = safe_pages_input()
capacity = safe_capacity_input()

while True:
    print("\n1. FIFO")
    print("2. LRU")
    print("3. LFU")
    print("4. MFU")
    print("5. Clock")
    print("6. Compare (Graph)")
    print("7. Enter new data")
    print("8. Exit")

    try:
        choice = int(input("Enter choice: "))
    except:
        print(" Invalid choice")
        continue

    if choice == 1:
        fifo(pages, capacity)

    elif choice == 2:
        lru(pages, capacity)

    elif choice == 3:
        lfu(pages, capacity)

    elif choice == 4:
        mfu(pages, capacity)

    elif choice == 5:
        clock(pages, capacity)

    elif choice == 6:
        compare_algorithms(pages, capacity)

    elif choice == 7:
        pages = safe_pages_input()
        capacity = safe_capacity_input()

    elif choice == 8:
        break

    else:
        print(" Invalid choice")

    print("\n" + "="*50)