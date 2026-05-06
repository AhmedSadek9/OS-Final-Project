import matplotlib.pyplot as plt
import pandas as pd


#DRAW SINGLE GANTT 
def draw_gantt(gantt, title="Gantt Chart"):
    fig, ax = plt.subplots(figsize=(10, 3))

    for pid, start, end in gantt:
        ax.barh(0, end - start, left=start)
        ax.text((start + end) / 2, 0, pid,
                ha='center', va='center',
                color='white', weight='bold')

    ax.set_xlabel("Time")
    ax.set_yticks([])
    ax.set_title(title)
    plt.grid(axis='x', linestyle='--', alpha=0.5)
    plt.show()


# DRAW RESULTS TABLE
def draw_table(result, title="Scheduling Results Table"):
    columns = [
        "Process",
        "AT",
        "BT",
        "First Start",
        "Completion",
        "Waiting",
        "Turnaround",
        "Response"
    ]

    df = pd.DataFrame(result, columns=columns)

    fig, ax = plt.subplots(figsize=(13, 3 + len(df) * 0.4))
    ax.axis("off")

    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc="center",
        loc="center"
    )

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.8)

    ax.set_title(title, fontsize=14, weight="bold", pad=20)

    plt.show()


#  DRAW ALL COMPARISON 
def draw_all_comparison(gantt_dict):
    fig, ax = plt.subplots(figsize=(13, 6))

    colors = {
        "P1": "tab:blue",
        "P2": "tab:orange",
        "P3": "tab:green",
        "P4": "tab:red",
        "P5": "tab:purple",
        "P6": "tab:brown",
        "P7": "tab:pink",
        "P8": "tab:gray",
        "P9": "tab:olive",
        "P10": "tab:cyan"
    }

    y_labels = []
    y_pos = []

    for y, (algo_name, gantt) in enumerate(gantt_dict.items()):
        y_labels.append(algo_name)
        y_pos.append(y)

        for pid, start, end in gantt:
            ax.barh(y, end - start, left=start,
                    color=colors.get(pid, "gray"))
            ax.text((start + end) / 2, y, pid,
                    ha='center', va='center',
                    color='white', weight='bold')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(y_labels)
    ax.set_xlabel("Time")
    ax.set_ylabel("Algorithm")
    ax.set_title("Gantt Chart Comparison For All CPU Scheduling Algorithms")
    plt.grid(axis='x', linestyle='--', alpha=0.5)
    plt.show()


#  MERGE PREEMPTIVE GANTT 
def merge_gantt(gantt):
    if not gantt:
        return []

    merged = [gantt[0]]

    for pid, start, end in gantt[1:]:
        last_pid, last_start, last_end = merged[-1]

        if pid == last_pid and start == last_end:
            merged[-1] = (last_pid, last_start, end)
        else:
            merged.append((pid, start, end))

    return merged


#  PRINT RESULTS 
def print_results(result, gantt, title):
    result.sort(key=lambda x: x[0])

    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

    print("\nGantt Chart:")
    for g in gantt:
        print(f"| {g[0]} ", end="")
    print("|")

    for g in gantt:
        print(f"{g[1]:<4}", end="")
    print(gantt[-1][2])

    print("\nProcess | AT | BT | First Start | Completion | Waiting | Turnaround | Response")
    print("-" * 90)

    total_wt = 0
    total_tat = 0
    total_rt = 0

    for r in result:
        pid, at, bt, first_start, completion, waiting, tat, response = r

        total_wt += waiting
        total_tat += tat
        total_rt += response

        print(f"{pid:<7} | {at:<2} | {bt:<2} | {first_start:<11} | "
              f"{completion:<10} | {waiting:<7} | {tat:<10} | {response:<8}")

    avg_wt = total_wt / len(result)
    avg_tat = total_tat / len(result)
    avg_rt = total_rt / len(result)

    print("\nAverage Waiting Time =", round(avg_wt, 2))
    print("Average Turnaround Time =", round(avg_tat, 2))
    print("Average Response Time =", round(avg_rt, 2))

    draw_gantt(gantt, title)
    draw_table(result, title + " Results Table")

    return result, gantt


#  SAFE INPUT
def safe_int_input(msg, allow_zero=True):
    while True:
        try:
            val = int(input(msg))
            if val < 0:
                print("Please enter a positive number")
                continue
            if not allow_zero and val == 0:
                print("Value cannot be zero")
                continue
            return val
        except:
            print("Invalid input, please enter a number")


#  FCFS 
def fcfs(processes, show=True):
    processes = sorted(processes, key=lambda x: x[1])
    time = 0
    result = []
    gantt = []

    for pid, at, bt in processes:
        if time < at:
            time = at

        start = time
        completion = start + bt
        waiting = start - at
        tat = completion - at
        response = start - at

        result.append((pid, at, bt, start, completion, waiting, tat, response))
        gantt.append((pid, start, completion))

        time = completion

    if show:
        return print_results(result, gantt, "FCFS Scheduling")

    return result, gantt


#  SJF NON PREEMPTIVE 
def sjf(processes, show=True):
    time = 0
    completed = []
    result = []
    gantt = []

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
        response = start - at

        result.append((pid, at, bt, start, completion, waiting, tat, response))
        gantt.append((pid, start, completion))

        time = completion
        completed.append(p)

    if show:
        return print_results(result, gantt, "SJF Non-Preemptive Scheduling")

    return result, gantt


#  SRTF PREEMPTIVE 
def srtf(processes, show=True):
    n = len(processes)
    remaining = {p[0]: p[2] for p in processes}
    first_start = {}
    completion_time = {}
    time = 0
    complete = 0
    gantt = []

    while complete < n:
        ready = [p for p in processes if p[1] <= time and remaining[p[0]] > 0]

        if not ready:
            time += 1
            continue

        p = min(ready, key=lambda x: remaining[x[0]])
        pid, at, bt = p

        if pid not in first_start:
            first_start[pid] = time

        start = time
        time += 1
        remaining[pid] -= 1

        gantt.append((pid, start, time))

        if remaining[pid] == 0:
            complete += 1
            completion_time[pid] = time

    gantt = merge_gantt(gantt)

    result = []

    for pid, at, bt in processes:
        completion = completion_time[pid]
        waiting = completion - at - bt
        tat = completion - at
        response = first_start[pid] - at

        result.append((pid, at, bt, first_start[pid], completion, waiting, tat, response))

    if show:
        return print_results(result, gantt, "SRTF Preemptive Scheduling")

    return result, gantt


#  ROUND ROBIN 
def round_robin(processes, quantum, show=True):
    processes = sorted(processes, key=lambda x: x[1])
    time = 0
    queue = []
    remaining = {p[0]: p[2] for p in processes}
    first_start = {}
    completion_time = {}
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

        if pid not in first_start:
            first_start[pid] = time

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
            completion_time[pid] = time

    result = []

    for pid, at, bt in processes:
        completion = completion_time[pid]
        waiting = completion - at - bt
        tat = completion - at
        response = first_start[pid] - at

        result.append((pid, at, bt, first_start[pid], completion, waiting, tat, response))

    if show:
        return print_results(result, gantt, f"Round Robin Scheduling Q={quantum}")

    return result, gantt


#  PRIORITY NON PREEMPTIVE 
def priority_scheduling(processes, show=True):
    time = 0
    completed = []
    result = []
    gantt = []

    while len(completed) < len(processes):
        ready = [p for p in processes if p[1] <= time and p not in completed]

        if not ready:
            time += 1
            continue

        p = min(ready, key=lambda x: (x[3], x[1]))
        pid, at, bt, pr = p

        start = time
        completion = start + bt
        waiting = start - at
        tat = completion - at
        response = start - at

        result.append((pid, at, bt, start, completion, waiting, tat, response))
        gantt.append((pid, start, completion))

        time = completion
        completed.append(p)

    if show:
        return print_results(result, gantt, "Priority Non-Preemptive Scheduling")

    return result, gantt


#  PRIORITY PREEMPTIVE 
def priority_preemptive(processes, show=True):
    n = len(processes)
    remaining = {p[0]: p[2] for p in processes}
    first_start = {}
    completion_time = {}
    time = 0
    complete = 0
    gantt = []

    while complete < n:
        ready = [p for p in processes if p[1] <= time and remaining[p[0]] > 0]

        if not ready:
            time += 1
            continue

        p = min(ready, key=lambda x: (x[3], x[1]))
        pid, at, bt, pr = p

        if pid not in first_start:
            first_start[pid] = time

        start = time
        time += 1
        remaining[pid] -= 1

        gantt.append((pid, start, time))

        if remaining[pid] == 0:
            complete += 1
            completion_time[pid] = time

    gantt = merge_gantt(gantt)

    result = []

    for pid, at, bt, pr in processes:
        completion = completion_time[pid]
        waiting = completion - at - bt
        tat = completion - at
        response = first_start[pid] - at

        result.append((pid, at, bt, first_start[pid], completion, waiting, tat, response))

    if show:
        return print_results(result, gantt, "Priority Preemptive Scheduling")

    return result, gantt


#  INPUT PROCESSES 
def input_processes():
    n = safe_int_input("Enter number of processes: ", allow_zero=False)
    processes = []

    for i in range(n):
        at = safe_int_input(f"P{i+1} Arrival Time: ")
        bt = safe_int_input(f"P{i+1} Burst Time: ", allow_zero=False)
        processes.append((f"P{i+1}", at, bt))

    return processes


#  INPUT PRIORITY 
def input_priority(processes):
    new_proc = []

    for p in processes:
        pr = safe_int_input(f"Priority for {p[0]}: ")
        new_proc.append((p[0], p[1], p[2], pr))

    return new_proc


#  COMPARE ALL 
def compare_all_algorithms(processes):
    q = safe_int_input("Enter quantum for Round Robin: ", allow_zero=False)

    print("\nPriority Data Needed For Priority Algorithms")
    priority_processes = input_priority(processes)

    gantt_dict = {}

    _, gantt = fcfs(processes, show=False)
    gantt_dict["FCFS"] = gantt

    _, gantt = sjf(processes, show=False)
    gantt_dict["SJF"] = gantt

    _, gantt = srtf(processes, show=False)
    gantt_dict["SRTF"] = gantt

    _, gantt = round_robin(processes, q, show=False)
    gantt_dict[f"Round Robin Q={q}"] = gantt

    _, gantt = priority_scheduling(priority_processes, show=False)
    gantt_dict["Priority Non-Preemptive"] = gantt

    _, gantt = priority_preemptive(priority_processes, show=False)
    gantt_dict["Priority Preemptive"] = gantt

    draw_all_comparison(gantt_dict)


#  MAIN 
processes = input_processes()

while True:
    print("\n1. FCFS")
    print("2. SJF (Non-preemptive)")
    print("3. SRTF (Preemptive)")
    print("4. Round Robin")
    print("5. Priority (Non-preemptive)")
    print("6. Priority (Preemptive)")
    print("7. Compare All Algorithms Gantt Chart")
    print("8. Enter new data")
    print("9. Exit")

    try:
        choice = int(input("Enter choice: "))
    except:
        print("Invalid choice")
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
        priority_processes = input_priority(processes)
        priority_scheduling(priority_processes)

    elif choice == 6:
        priority_processes = input_priority(processes)
        priority_preemptive(priority_processes)

    elif choice == 7:
        compare_all_algorithms(processes)

    elif choice == 8:
        processes = input_processes()

    elif choice == 9:
        break

    else:
        print("Invalid choice")

    print("\n" + "=" * 50)
