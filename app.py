import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

#  UI 
st.set_page_config(page_title="OS Simulator Pro", layout="wide")

st.markdown("""
<style>
.stButton>button {
    background-color:#ff4b4b;
    color:white;
    border-radius:10px;
    width: 100%;
}
.stMetric {
    background-color: #1e2130;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #31333f;
}
</style>
""", unsafe_allow_html=True)

st.title(" OS Simulator  - Final Project")

#  CPU FUNCTIONS 

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


def draw_gantt(gantt, title="Gantt Chart"):
    fig, ax = plt.subplots(figsize=(10, 4))

    for pid, s, e in gantt:
        ax.barh(0, e - s, left=s, edgecolor="white")
        ax.text((s + e) / 2, 0, pid,
                ha="center", va="center",
                color="white", fontweight="bold")

    ax.set_xlabel("Time")
    ax.set_yticks([])
    ax.set_title(title)
    ax.grid(axis="x", linestyle="--", alpha=0.5)

    return fig


def draw_cpu_comparison(gantt_dict):
    fig, ax = plt.subplots(figsize=(12, 6))

    for y, (algo, gantt) in enumerate(gantt_dict.items()):
        for pid, s, e in gantt:
            ax.barh(y, e - s, left=s, edgecolor="white")
            ax.text((s + e) / 2, y, pid,
                    ha="center", va="center",
                    color="white", fontweight="bold")

    ax.set_yticks(range(len(gantt_dict)))
    ax.set_yticklabels(list(gantt_dict.keys()))
    ax.set_xlabel("Time")
    ax.set_ylabel("Algorithm")
    ax.set_title("Gantt Chart Comparison For CPU Algorithms")
    ax.grid(axis="x", linestyle="--", alpha=0.5)

    return fig


def fcfs(proc):
    proc = sorted(proc, key=lambda x: x[1])
    t = 0
    g = []

    for pid, at, bt in proc:
        t = max(t, at)
        g.append((pid, t, t + bt))
        t += bt

    return g


def sjf(proc):
    t = 0
    done = []
    g = []

    while len(done) < len(proc):
        ready = [p for p in proc if p[1] <= t and p not in done]

        if not ready:
            t += 1
            continue

        p = min(ready, key=lambda x: x[2])
        g.append((p[0], t, t + p[2]))
        t += p[2]
        done.append(p)

    return g


def srtf(proc):
    rem = {p[0]: p[2] for p in proc}
    t = 0
    g = []

    while any(rem[p[0]] > 0 for p in proc):
        ready = [p for p in proc if p[1] <= t and rem[p[0]] > 0]

        if not ready:
            t += 1
            continue

        p = min(ready, key=lambda x: rem[x[0]])
        g.append((p[0], t, t + 1))
        rem[p[0]] -= 1
        t += 1

    return merge_gantt(g)


def rr(proc, q):
    proc = sorted(proc, key=lambda x: x[1])
    rem = {p[0]: p[2] for p in proc}

    t = 0
    i = 0
    queue = []
    g = []

    while i < len(proc) or queue:
        while i < len(proc) and proc[i][1] <= t:
            queue.append(proc[i])
            i += 1

        if not queue:
            t = proc[i][1]
            continue

        pid, at, bt = queue.pop(0)

        run = min(q, rem[pid])
        g.append((pid, t, t + run))

        t += run
        rem[pid] -= run

        while i < len(proc) and proc[i][1] <= t:
            queue.append(proc[i])
            i += 1

        if rem[pid] > 0:
            queue.append((pid, at, bt))

    return g


def calc_metrics(gantt, proc):
    completion = {}
    first_start = {}

    for pid, s, e in gantt:
        completion[pid] = e
        if pid not in first_start:
            first_start[pid] = s

    data = []

    for pid, at, bt in proc:
        ct = completion[pid]
        fs = first_start[pid]
        tat = ct - at
        wt = tat - bt
        rt = fs - at

        data.append([pid, at, bt, fs, ct, wt, tat, rt])

    return pd.DataFrame(
        data,
        columns=[
            "Process",
            "AT",
            "BT",
            "First Start",
            "Completion",
            "Waiting Time",
            "Turnaround Time",
            "Response Time"
        ]
    )



#  MEMORY FUNCTIONS 

def first_fit(blocks, procs):
    temp = blocks[:]
    alloc = []

    for p in procs:
        done = False

        for i in range(len(temp)):
            if temp[i] >= p:
                temp[i] -= p
                alloc.append(i)
                done = True
                break

        if not done:
            alloc.append(-1)

    return alloc, temp


def best_fit(blocks, procs):
    temp = blocks[:]
    alloc = []

    for p in procs:
        idx = -1

        for i in range(len(temp)):
            if temp[i] >= p:
                if idx == -1 or temp[i] < temp[idx]:
                    idx = i

        if idx != -1:
            temp[idx] -= p
            alloc.append(idx)
        else:
            alloc.append(-1)

    return alloc, temp


def worst_fit(blocks, procs):
    temp = blocks[:]
    alloc = []

    for p in procs:
        idx = -1

        for i in range(len(temp)):
            if temp[i] >= p:
                if idx == -1 or temp[i] > temp[idx]:
                    idx = i

        if idx != -1:
            temp[idx] -= p
            alloc.append(idx)
        else:
            alloc.append(-1)

    return alloc, temp


def allocation_df(procs, alloc):
    data = []

    for i, p in enumerate(procs):
        block = "Not Allocated" if alloc[i] == -1 else f"B{alloc[i] + 1}"
        data.append([f"P{i + 1}", p, block])

    return pd.DataFrame(data, columns=["Process", "Size", "Block"])


def fragmentation_df(blocks, remaining):
    data = []
    total_internal = 0
    total_free = 0

    for i in range(len(blocks)):
        used = blocks[i] - remaining[i]

        if used > 0:
            frag_type = "Internal Fragmentation"
            total_internal += remaining[i]
        else:
            frag_type = "Free / External Fragmentation"
            total_free += remaining[i]

        data.append([f"B{i + 1}", blocks[i], remaining[i], frag_type])

    df = pd.DataFrame(
        data,
        columns=["Block", "Original Size", "Remaining", "Fragmentation Type"]
    )

    return df, total_internal, total_free


def draw_memory_visual(blocks, procs, alloc, remaining, title):
    fig, ax = plt.subplots(figsize=(5, 7))

    ax.set_title(title, fontsize=14, weight="bold")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, sum(blocks))
    ax.axis("off")

    y = 0

    for i, block_size in enumerate(blocks):
        allocated = []

        for p_index, b_index in enumerate(alloc):
            if b_index == i:
                allocated.append((f"P{p_index + 1}", procs[p_index]))

        for pname, psize in allocated:
            ax.add_patch(
                plt.Rectangle(
                    (0.25, y),
                    0.5,
                    psize,
                    facecolor="lightblue",
                    edgecolor="black"
                )
            )
            ax.text(0.5, y + psize / 2, pname,
                    ha="center", va="center")
            y += psize

        if remaining[i] > 0:
            if allocated:
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
            ax.text(0.5, y + remaining[i] / 2, label,
                    ha="center", va="center")
            y += remaining[i]

        ax.text(
            0.08,
            y - block_size / 2,
            f"B{i + 1}\n({block_size})",
            ha="center",
            va="center"
        )

    return fig


def draw_all_memory_comparison(blocks, procs, results):
    fig, axes = plt.subplots(1, len(results), figsize=(6 * len(results), 8))

    if len(results) == 1:
        axes = [axes]

    fig.suptitle(
        "Memory Allocation Comparison (IF = Internal Fragmentation, Green = Free / External Fragmentation)",
        fontsize=14,
        weight="bold"
    )

    for ax, (algo_name, data) in zip(axes, results.items()):
        alloc = data["alloc"]
        remaining = data["remaining"]

        ax.set_title(algo_name, fontsize=13, weight="bold")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, sum(blocks))
        ax.axis("off")

        y = 0

        for i, block_size in enumerate(blocks):
            allocated = []

            for p_index, b_index in enumerate(alloc):
                if b_index == i:
                    allocated.append((f"P{p_index + 1}", procs[p_index]))

            for pname, psize in allocated:
                ax.add_patch(
                    plt.Rectangle(
                        (0.25, y),
                        0.5,
                        psize,
                        facecolor="lightblue",
                        edgecolor="black"
                    )
                )
                ax.text(0.5, y + psize / 2, pname,
                        ha="center", va="center")
                y += psize

            if remaining[i] > 0:
                if allocated:
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
                ax.text(0.5, y + remaining[i] / 2, label,
                        ha="center", va="center")
                y += remaining[i]

            ax.text(
                0.08,
                y - block_size / 2,
                f"B{i + 1}\n({block_size})",
                ha="center",
                va="center"
            )

    plt.tight_layout()
    return fig


#  PAGE FUNCTIONS 

def fifo(pages, cap):
    f = []
    q = []
    fault = 0

    for p in pages:
        if p not in f:
            fault += 1

            if len(f) < cap:
                f.append(p)
                q.append(p)
            else:
                old = q.pop(0)
                f[f.index(old)] = p
                q.append(p)

    return fault


def lru(pages, cap):
    f = []
    recent = []
    fault = 0

    for p in pages:
        if p not in f:
            fault += 1

            if len(f) < cap:
                f.append(p)
            else:
                old = recent.pop(0)
                f[f.index(old)] = p
        else:
            recent.remove(p)

        recent.append(p)

    return fault


def lfu(pages, cap):
    f = []
    freq = {}
    fault = 0

    for p in pages:
        freq[p] = freq.get(p, 0) + 1

        if p not in f:
            fault += 1

            if len(f) < cap:
                f.append(p)
            else:
                victim = min(f, key=lambda x: freq[x])
                f[f.index(victim)] = p

    return fault


def mfu(pages, cap):
    f = []
    freq = {}
    fault = 0

    for p in pages:
        freq[p] = freq.get(p, 0) + 1

        if p not in f:
            fault += 1

            if len(f) < cap:
                f.append(p)
            else:
                victim = max(f, key=lambda x: freq[x])
                f[f.index(victim)] = p

    return fault


def clock_algo(pages, cap):
    f = [-1] * cap
    ref = [0] * cap
    ptr = 0
    fault = 0

    for p in pages:
        if p in f:
            ref[f.index(p)] = 1
        else:
            fault += 1

            while ref[ptr] == 1:
                ref[ptr] = 0
                ptr = (ptr + 1) % cap

            f[ptr] = p
            ref[ptr] = 1
            ptr = (ptr + 1) % cap

    return fault


def heatmap(pages, cap):
    frames = []
    data = []

    for p in pages:
        if p not in frames:
            if len(frames) < cap:
                frames.append(p)
            else:
                frames[0] = p

        row = frames + ["-"] * (cap - len(frames))
        data.append([0 if x == "-" else x for x in row])

    fig, ax = plt.subplots()
    ax.imshow(data, cmap="viridis")
    ax.set_title("Memory Access Heatmap ")

    return fig


#  TABS 


tab1, tab2, tab3 = st.tabs([
    "CPU Scheduling",
    " Memory Allocation",
    " Page Replacement"
])


#  CPU TAB 

with tab1:
    col_l, col_r = st.columns([1, 2])

    with col_l:
        n = st.number_input("Number of Processes", 1, 10, key="cpu_n")

        proc = []

        for i in range(n):
            c1, c2 = st.columns(2)

            at = c1.number_input(
                f"AT P{i + 1}",
                min_value=0,
                value=0,
                key=f"cpu_at_{i}"
            )

            bt = c2.number_input(
                f"BT P{i + 1}",
                min_value=1,
                value=1,
                key=f"cpu_bt_{i}"
            )

            proc.append((f"P{i + 1}", at, bt))

        algo = st.selectbox(
            "Algorithm",
            ["FCFS", "SJF", "SRTF", "RR"],
            key="cpu_algo"
        )

        q = st.number_input(
            "Quantum",
            min_value=1,
            value=3,
            key="cpu_q"
        )

        run_cpu = st.button("▶ Run CPU Simulation", key="cpu_run")
        compare_cpu = st.button(" Compare CPU Algorithms", key="cpu_compare")

    with col_r:
        if run_cpu:
            if algo == "FCFS":
                g = fcfs(proc)
            elif algo == "SJF":
                g = sjf(proc)
            elif algo == "SRTF":
                g = srtf(proc)
            else:
                g = rr(proc, q)

            df = calc_metrics(g, proc)

            st.pyplot(draw_gantt(g, f"{algo} Gantt Chart"))

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Processes", len(proc))
            c2.metric("Avg Waiting Time", round(df["Waiting Time"].mean(), 2))
            c3.metric("Avg Turnaround Time", round(df["Turnaround Time"].mean(), 2))
            c4.metric("Avg Response Time", round(df["Response Time"].mean(), 2))

            st.subheader(" CPU Scheduling Table")
            st.dataframe(df, use_container_width=True)

        if compare_cpu:
            gantt_dict = {
                "FCFS": fcfs(proc),
                "SJF": sjf(proc),
                "SRTF": srtf(proc),
                f"RR Q={q}": rr(proc, q)
            }

            st.pyplot(draw_cpu_comparison(gantt_dict))

            compare_data = []

            for name, g in gantt_dict.items():
                df = calc_metrics(g, proc)

                compare_data.append([
                    name,
                    round(df["Waiting Time"].mean(), 2),
                    round(df["Turnaround Time"].mean(), 2),
                    round(df["Response Time"].mean(), 2)
                ])

            compare_df = pd.DataFrame(
                compare_data,
                columns=[
                    "Algorithm",
                    "Avg Waiting Time",
                    "Avg Turnaround Time",
                    "Avg Response Time"
                ]
            )

            st.subheader(" CPU Algorithms Comparison Table")
            st.dataframe(compare_df, use_container_width=True)

            fig, ax = plt.subplots(figsize=(8, 4))
            ax.bar(compare_df["Algorithm"], compare_df["Avg Waiting Time"])
            ax.set_title("Average Waiting Time Comparison")
            ax.set_ylabel("Average Waiting Time")
            st.pyplot(fig)


#  MEMORY TAB 


with tab2:
    c1, c2 = st.columns(2)

    with c1:
        b = st.number_input("Blocks", 1, 10, key="mem_b")

        blocks = []

        for i in range(b):
            blocks.append(
                st.number_input(
                    f"Block {i + 1} Size",
                    min_value=1,
                    value=100,
                    key=f"mem_block_{i}"
                )
            )

    with c2:
        p = st.number_input("Processes", 1, 10, key="mem_p")

        procs = []

        for i in range(p):
            procs.append(
                st.number_input(
                    f"Process {i + 1} Size",
                    min_value=1,
                    value=50,
                    key=f"mem_proc_{i}"
                )
            )

    algo_mem = st.selectbox(
        "Allocation Policy",
        ["First Fit", "Best Fit", "Worst Fit"],
        key="mem_algo"
    )

    run_mem = st.button(" Run Memory Allocation", key="mem_run")
    compare_mem = st.button(" Compare Memory Algorithms", key="mem_compare")

    if run_mem:
        if algo_mem == "First Fit":
            alloc, rem = first_fit(blocks, procs)
        elif algo_mem == "Best Fit":
            alloc, rem = best_fit(blocks, procs)
        else:
            alloc, rem = worst_fit(blocks, procs)

        alloc_df = allocation_df(procs, alloc)
        frag_df, total_internal, total_free = fragmentation_df(blocks, rem)

        col1, col2, col3 = st.columns(3)
        col1.metric("Allocated Processes", sum(1 for x in alloc if x != -1))
        col2.metric("Internal Fragmentation", total_internal)
        col3.metric("Free / External Fragmentation", total_free)

        st.subheader(" Memory Visualization")
        st.pyplot(draw_memory_visual(blocks, procs, alloc, rem, algo_mem))

        st.subheader(" Allocation Table")
        st.dataframe(alloc_df, use_container_width=True)

        st.subheader(" Fragmentation Table")
        st.dataframe(frag_df, use_container_width=True)

    if compare_mem:
        results = {}

        a, r = first_fit(blocks, procs)
        results["First Fit"] = {"alloc": a, "remaining": r}

        a, r = best_fit(blocks, procs)
        results["Best Fit"] = {"alloc": a, "remaining": r}

        a, r = worst_fit(blocks, procs)
        results["Worst Fit"] = {"alloc": a, "remaining": r}

        st.subheader("📊 Memory Allocation Visual Comparison")
        st.pyplot(draw_all_memory_comparison(blocks, procs, results))

        summary = []

        for name, data in results.items():
            frag_df, total_internal, total_free = fragmentation_df(
                blocks,
                data["remaining"]
            )

            summary.append([
                name,
                sum(1 for x in data["alloc"] if x != -1),
                total_internal,
                total_free,
                sum(data["remaining"])
            ])

            st.markdown(f"### {name}")
            st.dataframe(
                allocation_df(procs, data["alloc"]),
                use_container_width=True
            )
            st.dataframe(
                frag_df,
                use_container_width=True
            )

        summary_df = pd.DataFrame(
            summary,
            columns=[
                "Algorithm",
                "Allocated Processes",
                "Internal Fragmentation",
                "Free / External Fragmentation",
                "Total Remaining Memory"
            ]
        )

        st.subheader(" Memory Algorithms Summary")
        st.dataframe(summary_df, use_container_width=True)


#  PAGE TAB 


with tab3:
    pages_input = st.text_input(
        "Page Reference String",
        "7 0 1 2 0 3 0 4",
        key="page_input"
    )

    cap = st.number_input(
        "Number of Frames",
        1,
        10,
        value=3,
        key="page_cap"
    )

    if st.button("▶ Run Page Replacement Simulation", key="page_run"):
        pages = list(map(int, pages_input.split()))

        f1 = fifo(pages, cap)
        f2 = lru(pages, cap)
        f3 = lfu(pages, cap)
        f4 = mfu(pages, cap)
        f5 = clock_algo(pages, cap)

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("FIFO", f1)
        col2.metric("LRU", f2)
        col3.metric("LFU", f3)
        col4.metric("MFU", f4)
        col5.metric("Clock", f5)

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.bar(
            ["FIFO", "LRU", "LFU", "MFU", "Clock"],
            [f1, f2, f3, f4, f5]
        )
        ax.set_title("Page Replacement Comparison")
        ax.set_ylabel("Total Page Faults")
        st.pyplot(fig)

        st.pyplot(heatmap(pages, cap))


        #streamlit run app.py
