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
st.set_page_config(page_title="OS Final Project", layout="wide")

st.markdown("""
<style>
body {background-color:#0e1117;color:white;}
.stButton>button {background-color:#ff4b4b;color:white;border-radius:10px;}
</style>
""", unsafe_allow_html=True)

st.title("🚀 OS Simulator Pro")

# ================= GANTT =================
def draw_gantt(gantt):
    fig, ax = plt.subplots()
    for pid, s, e in gantt:
        ax.barh(0, e-s, left=s)
        ax.text((s+e)/2, 0, pid, ha='center', color='white')
    ax.set_yticks([])
    ax.set_title("Gantt Chart")
    return fig

# ================= CPU =================
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
    while any(rem[p[0]]>0 for p in proc):
        ready=[p for p in proc if p[1]<=t and rem[p[0]]>0]
        if not ready:
            t+=1; continue
        p=min(ready,key=lambda x:rem[x[0]])
        g.append((p[0],t,t+1))
        rem[p[0]]-=1; t+=1
    return g

def rr(proc,q):
    proc=sorted(proc,key=lambda x:x[1])
    rem={p[0]:p[2] for p in proc}
    t=0;i=0;queue=[];g=[]
    while i<len(proc) or queue:
        while i<len(proc) and proc[i][1]<=t:
            queue.append(proc[i]); i+=1
        if not queue:
            t=proc[i][1]; continue
        pid,at,bt=queue.pop(0)
        run=min(q,rem[pid])
        g.append((pid,t,t+run))
        t+=run; rem[pid]-=run
        while i<len(proc) and proc[i][1]<=t:
            queue.append(proc[i]); i+=1
        if rem[pid]>0:
            queue.append((pid,at,bt))
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

# ================= MEMORY =================
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

# ================= PAGE =================
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
    ax.imshow(data)
    ax.set_title("Heatmap 🔥")
    return fig

# ================= PDF =================
def generate_pdf(text):
    file="report.pdf"
    doc=SimpleDocTemplate(file)
    styles=getSampleStyleSheet()
    doc.build([Paragraph(text,styles["Normal"])])
    return file

# ================= TABS =================
tab1,tab2,tab3=st.tabs(["CPU_Scheduling","Memory_Allocation","Page_Replacement"])

# -------- CPU --------
with tab1:
    n=st.number_input("Processes",1,10,key="cpu_n")

    proc=[]
    for i in range(n):
        c1,c2=st.columns(2)
        at=c1.number_input(f"AT P{i+1}",0,key=f"cpu_at{i}")
        bt=c2.number_input(f"BT P{i+1}",1,key=f"cpu_bt{i}")
        proc.append((f"P{i+1}",at,bt))

    algo=st.selectbox("Algorithm",["FCFS","SJF","SRTF","RR"],key="cpu_algo")
    q=st.number_input("Quantum",1,key="cpu_q") if algo=="RR" else 1

    if st.button("Run CPU",key="cpu_run"):
        if algo=="FCFS": g=fcfs(proc)
        elif algo=="SJF": g=sjf(proc)
        elif algo=="SRTF": g=srtf(proc)
        else: g=rr(proc,q)

        st.pyplot(draw_gantt(g))

        df=calc_metrics(g,proc)
        st.dataframe(df)

        st.success(f"Avg WT = {df['WT'].mean():.2f}")
        st.success(f"Avg TAT = {df['TAT'].mean():.2f}")

        if REPORTLAB_AVAILABLE:
            report=f"Avg WT: {df['WT'].mean()}<br/>Avg TAT: {df['TAT'].mean()}"
            pdf=generate_pdf(report)
            with open(pdf,"rb") as f:
                st.download_button("📄 Download Report",f,"report.pdf")
        else:
            st.warning("PDF disabled (install reportlab)")

# -------- MEMORY --------
with tab2:
    b=st.number_input("Blocks",1,10,key="mem_b")
    blocks=[st.number_input(f"B{i+1}",1,key=f"mem_block{i}") for i in range(b)]

    p=st.number_input("Processes",1,10,key="mem_p")
    procs=[st.number_input(f"P{i+1}",1,key=f"mem_proc{i}") for i in range(p)]

    algo=st.selectbox("Algo",["First Fit","Best Fit"],key="mem_algo")

    if st.button("Run Memory",key="mem_run"):
        alloc,rem = first_fit(blocks,procs) if algo=="First Fit" else best_fit(blocks,procs)

        for i,a in enumerate(alloc):
            st.write(f"P{i+1} → {'Not Allocated' if a==-1 else 'B'+str(a+1)}")

        fig,ax=plt.subplots()
        ax.bar(range(len(rem)),rem)
        ax.set_title("Fragmentation")
        st.pyplot(fig)

# -------- PAGE --------
with tab3:
    pages_input=st.text_input("Pages","7 0 1 2 0 3 0 4",key="page_input")
    cap=st.number_input("Frames",1,10,key="page_cap")

    if st.button("Run Page",key="page_run"):
        pages=list(map(int,pages_input.split()))

        f1=fifo(pages,cap)
        f2=lru(pages,cap)
        f3=lfu(pages,cap)
        f4=mfu(pages,cap)
        f5=clock_algo(pages,cap)

        st.write({"FIFO":f1,"LRU":f2,"LFU":f3,"MFU":f4,"Clock":f5})

        fig,ax=plt.subplots()
        ax.bar(["FIFO","LRU","LFU","MFU","Clock"],[f1,f2,f3,f4,f5])
        ax.set_title("Comparison 🔥")
        st.pyplot(fig)

        st.pyplot(heatmap(pages,cap))
        
        #streamlit run app.py