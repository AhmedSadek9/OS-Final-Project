import matplotlib.pyplot as plt

# ================= DRAW GANTT =================
def draw_gantt(gantt):
    fig, ax = plt.subplots()

    for g in gantt:
        pid, start, end = g
        ax.barh(0, end - start, left=start)
        ax.text((start + end)/2, 0, pid, ha='center', va='center', color='white')

    ax.set_xlabel("Time")
    ax.set_yticks([])
    ax.set_title("Gantt Chart")

    plt.show()


# ================= PRINT RESULTS =================
def print_results(result, gantt):
    result.sort(key=lambda x: x[0])

    print("\nGantt Chart:")
    for g in gantt:
        print(f"| {g[0]} ", end="")
    print("|")

    for g in gantt:
        print(f"{g[1]:<4}", end="")
    print(gantt[-1][2])

    print("\nProcess | AT | BT | Start | Completion | Waiting | Turnaround")
    print("-"*65)

    for r in result:
        print(f"{r[0]:<7} | {r[1]:<2} | {r[2]:<2} | {r[3]:<5} | {r[4]:<10} | {r[5]:<7} | {r[6]:<10}")

    avg_wt = sum(r[5] for r in result) / len(result)
    avg_tat = sum(r[6] for r in result) / len(result)

    print("\nAverage Waiting Time =", round(avg_wt, 2))
    print("Average Turnaround Time =", round(avg_tat, 2))

    draw_gantt(gantt)

    return avg_wt, avg_tat


# ================= SAFE INPUT =================
def safe_int_input(msg, allow_zero=True):
    while True:
        try:
            val = int(input(msg))
            if val < 0:
                print("Please enter a positive number")
                continue
            if not allow_zero and val == 0:
                print(" Value cannot be zero")
                continue
            return val
        except:
            print(" Invalid input, please enter a number")


# ================= FCFS =================
def fcfs(processes):
    processes = sorted(processes, key=lambda x: x[1])
    time = 0
    result, gantt = [], []

    for pid, at, bt in processes:
        if time < at:
            time = at

        start = time
        completion = start + bt
        waiting = start - at
        tat = completion - at

        result.append((pid, at, bt, start, completion, waiting, tat))
        gantt.append((pid, start, completion))
        time = completion

    return print_results(result, gantt)


# ================= SJF =================
def sjf(processes):
    time = 0
    completed = []
    result, gantt = [], []

    while len(completed) < len(processes):
        ready = [p for p in processes if p[1] <= time and p not in completed]

        if not ready:
            time += 1
            continue

        p = min(ready, key=lambda x: x[2])
        pid, at, bt = p

        start = time
        completion = start + bt
        waiting = start - at
        tat = completion - at

        result.append((pid, at, bt, start, completion, waiting, tat))
        gantt.append((pid, start, completion))

        time = completion
        completed.append(p)

    return print_results(result, gantt)


# ================= SRTF =================
def srtf(processes):
    n = len(processes)
    remaining = {p[0]: p[2] for p in processes}
    time = 0
    complete = 0
    result = []
    gantt = []

    while complete < n:
        ready = [p for p in processes if p[1] <= time and remaining[p[0]] > 0]

        if not ready:
            time += 1
            continue

        p = min(ready, key=lambda x: remaining[x[0]])
        pid, at, bt = p

        start = time
        time += 1
        remaining[pid] -= 1

        gantt.append((pid, start, time))

        if remaining[pid] == 0:
            complete += 1
            completion = time
            waiting = completion - at - bt
            tat = completion - at
            result.append((pid, at, bt, completion - bt, completion, waiting, tat))

    return print_results(result, gantt)


# ================= Round Robin =================
def round_robin(processes, quantum):
    processes = sorted(processes, key=lambda x: x[1])
    time = 0
    queue = []
    remaining = {p[0]: p[2] for p in processes}
    result = {}
    gantt = []
    i = 0

    while i < len(processes) or queue:
        while i < len(processes) and processes[i][1] <= time:
            queue.append(processes[i])
            i += 1

        if not queue:
            time = processes[i][1]
            continue

        pid, at, bt = queue.pop(0)

        start = time
        exec_time = min(quantum, remaining[pid])
        time += exec_time
        remaining[pid] -= exec_time

        gantt.append((pid, start, time))

        while i < len(processes) and processes[i][1] <= time:
            queue.append(processes[i])
            i += 1

        if remaining[pid] > 0:
            queue.append((pid, at, bt))
        else:
            completion = time
            waiting = completion - at - bt
            tat = completion - at
            result[pid] = (pid, at, bt, completion - bt, completion, waiting, tat)

    return print_results(list(result.values()), gantt)


# ================= Priority =================
def priority_scheduling(processes):
    processes = sorted(processes, key=lambda x: (x[3], x[1]))
    time = 0
    result, gantt = [], []

    for pid, at, bt, pr in processes:
        if time < at:
            time = at

        start = time
        completion = start + bt
        waiting = start - at
        tat = completion - at

        result.append((pid, at, bt, start, completion, waiting, tat))
        gantt.append((pid, start, completion))

        time = completion

    return print_results(result, gantt)


def priority_preemptive(processes):
    n = len(processes)
    remaining = {p[0]: p[2] for p in processes}
    time = 0
    complete = 0
    result = []
    gantt = []

    while complete < n:
        ready = [p for p in processes if p[1] <= time and remaining[p[0]] > 0]

        if not ready:
            time += 1
            continue

        p = min(ready, key=lambda x: x[3])
        pid, at, bt, pr = p

        start = time
        time += 1
        remaining[pid] -= 1

        gantt.append((pid, start, time))

        if remaining[pid] == 0:
            complete += 1
            completion = time
            waiting = completion - at - bt
            tat = completion - at
            result.append((pid, at, bt, completion - bt, completion, waiting, tat))

    return print_results(result, gantt)


# ================= INPUT =================
def input_processes():
    n = safe_int_input("Enter number of processes: ", allow_zero=False)
    processes = []

    for i in range(n):
        at = safe_int_input(f"P{i+1} Arrival Time: ")
        bt = safe_int_input(f"P{i+1} Burst Time: ", allow_zero=False)
        processes.append((f"P{i+1}", at, bt))

    return processes


# ================= MAIN =================
processes = input_processes()

while True:
    print("\n1. FCFS")
    print("2. SJF (Non-preemptive)")
    print("3. SRTF (Preemptive) ")
    print("4. Round Robin")
    print("5. Priority (Non-preemptive)")
    print("6. Priority (Preemptive) ")
    print("7. Enter new data")
    print("8. Exit")

    try:
        choice = int(input("Enter choice: "))
    except:
        print(" Invalid choice")
        continue

    if choice == 1:
        fcfs(processes)

    elif choice == 2:
        sjf(processes)

    elif choice == 3:
        srtf(processes)

    elif choice == 4:
        q = safe_int_input("Enter quantum: ", allow_zero=False)
        round_robin(processes, q)

    elif choice == 5:
        new_proc = []
        for p in processes:
            pr = safe_int_input(f"Priority for {p[0]}: ")
            new_proc.append((p[0], p[1], p[2], pr))
        priority_scheduling(new_proc)

    elif choice == 6:
        new_proc = []
        for p in processes:
            pr = safe_int_input(f"Priority for {p[0]}: ")
            new_proc.append((p[0], p[1], p[2], pr))
        priority_preemptive(new_proc)

    elif choice == 7:
        processes = input_processes()

    elif choice == 8:
        break

    print("\n" + "="*50)