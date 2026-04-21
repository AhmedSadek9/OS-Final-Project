import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# ================= OPTIONAL PDF =================
try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except:
    REPORTLAB_AVAILABLE = False

# ================= UI =================
st.set_page_config(page_title="OS Simulator Pro", layout="wide")

st.markdown("""
<style>
body {background-color:#0e1117;color:white;}
.stButton>button {background-color:#ff4b4b;color:white;border-radius:10px; width: 100%;}
.stMetric {background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #31333f;}
</style>
""", unsafe_allow_html=True)

st.title("🚀 OS Simulator Pro - Advanced Dashboard")

# ================= CPU FUNCTIONS =================
def draw_gantt(gantt):
    fig, ax = plt.subplots(figsize=(10, 4))
    for i, (pid, s, e) in enumerate(gantt):
        ax.barh(0, e - s, left=s, edgecolor='white', label=pid)
        ax.text((s+e)/2, 0, pid, ha='center', va='center', color='white', fontweight='bold')
    
    ax.set_xlabel("Time")
    ax.set_yticks([])
    ax.set_title("Gantt Chart")
    return fig

def fcfs(proc):
    proc = sorted(proc, key=lambda x: x[1])
    t=0; g=[]
    for pid,at,bt in proc:
        t=max(t,at)
        g.append((pid,t,t+bt))
        t+=bt
    return g

def sjf(proc):
    t=0; done=[]; g=[]
    while len(done)<len(proc):
        ready=[p for p in proc if p[1]<=t and p not in done]
        if not ready:
            t+=1; continue
        p=min(ready,key=lambda x:x[2])
        g.append((p[0],t,t+p[2]))
        t+=p[2]; done.append(p)
    return g

def srtf(proc):
    rem={p[0]:p[2] for p in proc}
    t=0; g=[]
    last_pid = None
    start_t = 0
    
    while any(rem[p[0]]>0 for p in proc):
        ready=[p for p in proc if p[1]<=t and rem[p[0]]>0]
        if not ready:
            t+=1; continue
        p=min(ready,key=lambda x:rem[x[0]])
        
        if last_pid is not None and last_pid != p[0]:
            g.append((last_pid, start_t, t))
            start_t = t
        
        last_pid = p[0]
        rem[p[0]]-=1; t+=1
    g.append((last_pid, start_t, t))
    return g

def rr(proc,q):
    proc=sorted(proc,key=lambda x:x[1])
    rem={p[0]:p[2] for p in proc}
    t=0;i=0;queue=[];g=[]
    while i<len(proc) or queue:
        while i<len(proc) and proc[i][1]<=t:
            queue.append(list(proc[i])); i+=1
        if not queue:
            if i < len(proc): t=proc[i][1]; continue
            else: break
        
        p_data=queue.pop(0)
        pid, at, bt = p_data[0], p_data[1], p_data[2]
        run=min(q,rem[pid])
        g.append((pid,t,t+run))
        t+=run; rem[pid]-=run
        
        while i<len(proc) and proc[i][1]<=t:
            queue.append(list(proc[i])); i+=1
            
        if rem[pid]>0:
            queue.append([pid,at,bt])
    return g

def calc_metrics(gantt, proc):
    comp={}
    for pid,s,e in gantt:
        comp[pid]=e
    data=[]
    for pid,at,bt in proc:
        ct=comp[pid]
        tat=ct-at
        wt=tat-bt
        data.append([pid,at,bt,ct,wt,tat])
    return pd.DataFrame(data,columns=["P","AT","BT","CT","WT","TAT"])

# ================= MEMORY FUNCTIONS =================
def first_fit(blocks,procs):
    temp=blocks[:]; alloc=[]
    for p in procs:
        done=False
        for i in range(len(temp)):
            if temp[i]>=p:
                temp[i]-=p; alloc.append(i); done=True; break
        if not done: alloc.append(-1)
    return alloc,temp

def best_fit(blocks,procs):
    temp=blocks[:]; alloc=[]
    for p in procs:
        idx=-1
        for i in range(len(temp)):
            if temp[i]>=p and (idx==-1 or temp[i]<temp[idx]):
                idx=i
        if idx!=-1:
            temp[idx]-=p; alloc.append(idx)
        else:
            alloc.append(-1)
    return alloc,temp

# ================= PAGE FUNCTIONS =================
def fifo(pages,cap):
    f=[];q=[];fault=0
    for p in pages:
        if p not in f:
            fault+=1
            if len(f)<cap:
                f.append(p); q.append(p)
            else:
                old=q.pop(0)
                f[f.index(old)]=p; q.append(p)
    return fault

def lru(pages,cap):
    f=[];recent=[];fault=0
    for p in pages:
        if p not in f:
            fault+=1
            if len(f)<cap:
                f.append(p)
            else:
                old=recent.pop(0)
                f[f.index(old)]=p
        else:
            recent.remove(p)
        recent.append(p)
    return fault

def lfu(pages,cap):
    f=[];freq={};fault=0
    for p in pages:
        freq[p]=freq.get(p,0)+1
        if p not in f:
            fault+=1
            if len(f)<cap:
                f.append(p)
            else:
                victim=min(f,key=lambda x:freq[x])
                f[f.index(victim)]=p
    return fault

def mfu(pages,cap):
    f=[];freq={};fault=0
    for p in pages:
        freq[p]=freq.get(p,0)+1
        if p not in f:
            fault+=1
            if len(f)<cap:
                f.append(p)
            else:
                victim=max(f,key=lambda x:freq[x])
                f[f.index(victim)]=p
    return fault

def clock_algo(pages,cap):
    f=[-1]*cap;ref=[0]*cap;ptr=0;fault=0
    for p in pages:
        if p in f:
            ref[f.index(p)]=1
        else:
            fault+=1
            while ref[ptr]==1:
                ref[ptr]=0
                ptr=(ptr+1)%cap
            f[ptr]=p; ref[ptr]=1
            ptr=(ptr+1)%cap
    return fault

def heatmap(pages,cap):
    frames=[];data=[]
    for p in pages:
        if p not in frames:
            if len(frames)<cap:
                frames.append(p)
            else:
                frames[0]=p
        row=frames+['-']*(cap-len(frames))
        data.append([0 if x=='-' else x for x in row])
    fig,ax=plt.subplots()
    ax.imshow(data, cmap='viridis')
    ax.set_title("Memory Access Heatmap 🔥")
    return fig

# ================= PDF =================
def generate_pdf(text):
    file="report.pdf"
    doc=SimpleDocTemplate(file)
    styles=getSampleStyleSheet()
    doc.build([Paragraph(text,styles["Normal"])])
    return file

# ================= TABS =================
tab1,tab2,tab3=st.tabs(["📊 CPU Scheduling","💾 Memory Allocation","📄 Page Replacement"])

# -------- CPU TAB --------
with tab1:
    col_l, col_r = st.columns([1, 2])
    with col_l:
        n=st.number_input("Number of Processes",1,10,key="cpu_n")
        proc=[]
        for i in range(n):
            c1,c2=st.columns(2)
            at=c1.number_input(f"AT P{i+1}",0,key=f"cpu_at{i}")
            bt=c2.number_input(f"BT P{i+1}",1,key=f"cpu_bt{i}")
            proc.append((f"P{i+1}",at,bt))
        
        algo=st.selectbox("Algorithm",["FCFS","SJF","SRTF","RR"],key="cpu_algo")
        q=st.number_input("Quantum (for RR)",1,key="cpu_q") if algo=="RR" else 1
        
        run_cpu = st.button("▶️ Run CPU Simulation",key="cpu_run")
        compare_cpu = st.button("⚔️ Compare CPU Algorithms")

    with col_r:
        if run_cpu:
            if algo=="FCFS": g=fcfs(proc)
            elif algo=="SJF": g=sjf(proc)
            elif algo=="SRTF": g=srtf(proc)
            else: g=rr(proc,q)

            st.pyplot(draw_gantt(g))
            df=calc_metrics(g,proc)
            
            # 🔥 KPIs Dashboard
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Processes", len(proc))
            col2.metric("Avg Waiting Time", round(df["WT"].mean(), 2))
            col3.metric("Avg Turnaround Time", round(df["TAT"].mean(), 2))
            
            st.dataframe(df, use_container_width=True)

            if REPORTLAB_AVAILABLE:
                report=f"Algorithm: {algo}<br/>Avg WT: {df['WT'].mean():.2f}<br/>Avg TAT: {df['TAT'].mean():.2f}"
                pdf=generate_pdf(report)
                with open(pdf,"rb") as f:
                    st.download_button("📄 Download PDF Report",f,"report.pdf")

        if compare_cpu:
            g1, g2, g3, g4 = fcfs(proc), sjf(proc), srtf(proc), rr(proc, q)
            results = {
                "FCFS": calc_metrics(g1, proc)["WT"].mean(),
                "SJF": calc_metrics(g2, proc)["WT"].mean(),
                "SRTF": calc_metrics(g3, proc)["WT"].mean(),
                "RR": calc_metrics(g4, proc)["WT"].mean()
            }
            fig, ax = plt.subplots()
            ax.bar(results.keys(), results.values(), color=['#ff4b4b', '#4bafff', '#4bff8d', '#ffce4b'])
            ax.set_title("Comparison (Lower WT is better)")
            ax.set_ylabel("Avg Waiting Time")
            st.pyplot(fig)

# -------- MEMORY TAB --------
with tab2:
    c1, c2 = st.columns(2)
    with c1:
        b=st.number_input("Blocks",1,10,key="mem_b")
        blocks=[st.number_input(f"Block {i+1} Size",1,key=f"mem_block{i}") for i in range(b)]
    with c2:
        p=st.number_input("Processes",1,10,key="mem_p")
        procs=[st.number_input(f"Process {i+1} Size",1,key=f"mem_proc{i}") for i in range(p)]

    algo_mem=st.selectbox("Allocation Policy",["First Fit","Best Fit"],key="mem_algo")

    if st.button("▶️ Run Memory Allocation"):
        alloc, rem = first_fit(blocks,procs) if algo_mem=="First Fit" else best_fit(blocks,procs)
        
        # 🔥 Dashboard KPIs
        col1, col2 = st.columns(2)
        col1.metric("Total Fragmentation", sum(rem))
        col2.metric("Allocated Processes", sum(1 for x in alloc if x != -1))

        cols = st.columns(len(alloc))
        for i, a in enumerate(alloc):
            cols[i].info(f"P{i+1} → {'❌' if a==-1 else 'B'+str(a+1)}")

        fig, ax = plt.subplots(figsize=(8, 3))
        ax.bar(range(1, len(rem)+1), rem, color='skyblue')
        ax.set_title("Remaining Space in Each Block (Internal Fragmentation)")
        ax.set_xticks(range(1, len(rem)+1))
        st.pyplot(fig)

# -------- PAGE TAB --------
with tab3:
    pages_input=st.text_input("Page Reference String (space separated)","7 0 1 2 0 3 0 4",key="page_input")
    cap=st.number_input("Number of Frames",1,10,value=3,key="page_cap")

    if st.button("▶️ Run Page Replacement Simulation"):
        pages=list(map(int,pages_input.split()))
        f1, f2, f3, f4, f5 = fifo(pages,cap), lru(pages,cap), lfu(pages,cap), mfu(pages,cap), clock_algo(pages,cap)

        # 🔥 Dashboard KPIs
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("FIFO", f1)
        col2.metric("LRU", f2)
        col3.metric("LFU", f3)
        col4.metric("MFU", f4)
        col5.metric("Clock", f5)

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.bar(["FIFO","LRU","LFU","MFU","Clock"], [f1,f2,f3,f4,f5], color='coral')
        ax.set_title("Algorithm Comparison")
        ax.set_ylabel("Total Page Faults")
        st.pyplot(fig)

        st.pyplot(heatmap(pages,cap))
        
        #streamlit run app.py
