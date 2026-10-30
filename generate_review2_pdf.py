import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

class ReviewCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#4b5563"))
        
        # Running top header on pages 2 onwards
        if self._pageNumber > 1:
            header_text = "Adaptive Fairness-Aware CPU Scheduling Simulator for Linux | Review 2"
            self.drawString(40, A4[1] - 25, header_text)
            self.setStrokeColor(colors.HexColor("#d1d5db"))
            self.setLineWidth(0.5)
            self.line(40, A4[1] - 29, A4[0] - 40, A4[1] - 29)
            
        # Running bottom footer on all pages
        footer_text = f"Operating Systems | Review 2 | Page {self._pageNumber}"
        self.drawCentredString(A4[0] / 2.0, 20, footer_text)
        self.setStrokeColor(colors.HexColor("#e5e7eb"))
        self.setLineWidth(0.5)
        self.line(40, 29, A4[0] - 40, 29)
        
        self.restoreState()

def build_pdf():
    pdf_filename = "/Users/alokmaan/Downloads/OS_Review_2_Adaptive_Fairness_Aware_CPU_Scheduler.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=17, leading=21,
        alignment=1, textColor=colors.HexColor('#0f172a'), spaceAfter=5
    )
    
    sub_subtitle_style = ParagraphStyle(
        'DocSubSubtitle', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=9.5, leading=12.5,
        alignment=1, textColor=colors.HexColor('#475569'), spaceAfter=10
    )
    
    author_style = ParagraphStyle(
        'DocAuthors', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9, leading=13,
        alignment=1, textColor=colors.HexColor('#1f2937'), spaceAfter=10
    )
    
    h1_style = ParagraphStyle(
        'SecH1', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11, leading=14,
        textColor=colors.HexColor('#0f2b5c'), spaceBefore=8, spaceAfter=4,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'SecH2', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=9.5, leading=12,
        textColor=colors.HexColor('#1e40af'), spaceBefore=6, spaceAfter=2.5,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyDark', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=10.8,
        textColor=colors.HexColor('#1f2937'), spaceAfter=3.5
    )
    
    bullet_style = ParagraphStyle(
        'BulletDark', parent=styles['Normal'],
        fontName='Helvetica', fontSize=7.5, leading=10.2,
        textColor=colors.HexColor('#1f2937'), leftIndent=10, spaceAfter=2
    )
    
    fig_caption_style = ParagraphStyle(
        'FigCaption', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=7.5, leading=9.5,
        alignment=1, textColor=colors.HexColor('#374151'), spaceBefore=2, spaceAfter=4
    )
    
    code_block_style = ParagraphStyle(
        'CodeBlock', parent=styles['Normal'],
        fontName='Courier', fontSize=7, leading=8.8,
        textColor=colors.HexColor('#0f172a')
    )

    tbl_header = ParagraphStyle(
        'TblHdr', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=7, leading=8.8,
        textColor=colors.white, alignment=0
    )
    
    tbl_cell = ParagraphStyle(
        'TblCell', parent=styles['Normal'],
        fontName='Helvetica', fontSize=6.8, leading=8.4,
        textColor=colors.HexColor('#111827')
    )
    
    tbl_cell_bold = ParagraphStyle(
        'TblCellB', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=6.8, leading=8.4,
        textColor=colors.HexColor('#111827')
    )
    
    tbl_cell_code = ParagraphStyle(
        'TblCellCode', parent=styles['Normal'],
        fontName='Courier', fontSize=6.2, leading=7.8,
        textColor=colors.HexColor('#1e293b')
    )

    story = []
    
    def P(txt): return Paragraph(txt, body_style)
    def B(txt): return Paragraph(f"• {txt}", bullet_style)
    def H1(txt): return Paragraph(txt, h1_style)
    def H2(txt): return Paragraph(txt, h2_style)
    def Cap(txt): return Paragraph(txt, fig_caption_style)
    def FigBlock(path, w, h, cap):
        return KeepTogether([Image(path, width=w, height=h), Cap(cap), Spacer(1, 2)])
    def TableBlock(tbl, cap=None):
        items = [tbl]
        if cap: items.append(Cap(cap))
        items.append(Spacer(1, 2))
        return KeepTogether(items)

    fig_dir = "/Users/alokmaan/.gemini/antigravity/scratch/os_review2/extracted_figures"
    r1_dir = "/Users/alokmaan/.gemini/antigravity/scratch/os_review2/extracted_r1"
    sc_dir = "/Users/alokmaan/.gemini/antigravity/scratch/os_review2/screenshots"

    # ================= PAGE 1: COVER & ABSTRACT =================
    story.append(Spacer(1, 10))
    story.append(Paragraph("OPERATING SYSTEMS", ParagraphStyle('TopSub', parent=title_style, fontSize=13, leading=16, textColor=colors.HexColor('#1e293b'))))
    story.append(Paragraph("PROJECT REVIEW - 2", ParagraphStyle('RevTitle', parent=title_style, fontSize=15, leading=19, textColor=colors.HexColor('#0f2b5c'))))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Adaptive Fairness-Aware CPU Scheduling Simulator for Linux:<br/>Dynamic Priority and Starvation Prevention", title_style))
    story.append(Paragraph("Methodology, Implementation, Verification, and Experimental Evaluation", sub_subtitle_style))
    story.append(HRFlowable(width="85%", thickness=1.2, color=colors.HexColor('#1e3a8a'), spaceBefore=2, spaceAfter=12))
    
    authors_text = """
    <b>Submitted By:</b><br/>
    <b>Alok Maan</b> &nbsp;|&nbsp; 24BCB0057 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Arshdeep Singh</b> &nbsp;|&nbsp; 24BCE0556<br/>
    <b>Ankush Hooda</b> &nbsp;|&nbsp; 24BCE0966 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Somya Sharma</b> &nbsp;|&nbsp; 24BCT0324<br/><br/>
    <b>Faculty Name:</b> Prof. Ezhil Arasi<br/>
    <i>School of Computer Science and Engineering, Vellore Institute of Technology</i>
    """
    story.append(Paragraph(authors_text, author_style))
    story.append(Spacer(1, 6))
    
    story.append(H2("Abstract"))
    abstract_text = (
        "Review 1 proposed a user-space, discrete-event simulator for an Adaptive Fairness-Aware Scheduler (AFAS) and a plan for testing it. "
        "This report (Review 2) presents the complete working implementation, formal software architecture, algorithmic workflows, verification suite, and first empirical results. "
        "The simulator now reliably executes First-Come, First-Served (FCFS), non-preemptive Shortest Job First (SJF), preemptive Shortest Remaining Time First (SRTF), "
        "Round Robin (RR, quantum q=4), and non-preemptive Priority scheduling alongside the proposed AFAS policy. "
        "All policies run on identical workload sets via a unified event engine and metric calculator ensuring zero measurement divergence. "
        "The software implementation is validated against 12 automated unit tests, including hand-calculated solutions for all classic baselines. "
        "Five synthetic workload families (W1–W5) were benchmarked over five fixed pseudo-random seeds (25 workload instances, 200 simulation runs), followed by a formal ablation study, "
        "a one-at-a-time parameter sensitivity sweep, a time-quantum sweep (q=1 to 32), and a decision-runtime scaling analysis.<br/><br/>"
        "<b>Main Findings:</b> Compared to static Priority scheduling, AFAS reduced the mean maximum ready-queue wait from 168.2 to 68.2 time units (<b>59% reduction</b>) "
        "and slashed the 95th-percentile response time from 158.7 to 52.5. Relative to Round Robin, AFAS achieved lower average waiting time (52.3 vs 65.6) and fewer starvation warnings "
        "(4.6 vs 11.0), while Round Robin exhibited tighter tail bounding (max wait 39.2 vs 68.2) and a superior Jain fairness index (0.78 vs 0.69). "
        "SRTF achieved the lowest mean waiting time (29.4) but caused extreme starvation for long-running jobs (max wait 146.5). "
        "Crucially, our ablation study confirms that waiting-time aging is solely responsible for AFAS's tail-latency gains, whereas the recent-CPU-share penalty showed no statistically "
        "distinguishable impact in these workloads—an honest negative result we report transparently. AFAS therefore operates as a balanced trade-off policy. "
        "The simulator is entirely user-space, discrete-event, and does not alter the host Linux kernel or claim hard real-time guarantees."
    )
    story.append(P(abstract_text))
    story.append(P("<b>Keywords:</b> CPU scheduling, adaptive priority, starvation prevention, discrete-event simulation, Jain fairness index, ablation study, VIT IDF, patent prior art."))
    story.append(PageBreak())

    # ================= PAGE 2: STATUS & ARCHITECTURE =================
    story.append(H1("Executive Status: Review 2 Scope Against Review 1 Plan"))
    r1_status_data = [
        [Paragraph("Review 1 Deliverable", tbl_header), Paragraph("Status", tbl_header), Paragraph("Evidence / Realization in Review 2 Report", tbl_header)],
        [Paragraph("Phase 1: Workload schema & metric formulas", tbl_cell_bold), Paragraph("Completed", tbl_cell), Paragraph("Section 2, 7 & 8: Complete formalization of CT, TAT, WT, RT, Jain Index, Warnings.", tbl_cell)],
        [Paragraph("Phase 2: Baseline policies unit-tested against manual cases", tbl_cell_bold), Paragraph("Completed", tbl_cell), Paragraph("Section 9 & 10: 12 pytest automated tests pass; exact match with analytical hand-solved cases.", tbl_cell)],
        [Paragraph("Phase 3: AFAS scoring, tie-break, decision audit log", tbl_cell_bold), Paragraph("Completed", tbl_cell), Paragraph("Section 3 & 4: Implemented S_i(t) formula, deterministic tie-breaking, and transparent audit trace.", tbl_cell)],
        [Paragraph("Phase 4: Browser / desktop GUI interface", tbl_cell_bold), Paragraph("Partial", tbl_cell), Paragraph("CLI runner, CSV export, and high-res Matplotlib chart generation built; browser GUI deferred to Review 3.", tbl_cell)],
        [Paragraph("Phase 5: Scenarios, CSV export, comparison, sensitivity", tbl_cell_bold), Paragraph("Completed", tbl_cell), Paragraph("Section 10: 200 runs across 5 workloads x 5 seeds; ablation, weight sweep, quantum sweep, scaling.", tbl_cell)],
        [Paragraph("Phase 6: Patent/literature review & citation checks", tbl_cell_bold), Paragraph("Partial", tbl_cell), Paragraph("Section 12 & 16: Updated VIT IDF patent checklist; added Jain (1984) and Silberschatz (2018) references.", tbl_cell)],
        [Paragraph("Objective 7: US/UK patent prior-art landscape", tbl_cell_bold), Paragraph("Completed", tbl_cell), Paragraph("Section 12: Detailed claim-by-claim analysis against GB2304211A/B, US6668269B1, US8881161B1, US8434086B2.", tbl_cell)],
        [Paragraph("Objective 8: Document limits vs real Linux kernel", tbl_cell_bold), Paragraph("Completed", tbl_cell), Paragraph("Section 13: Scope boundaries, simulation proxy overheads, and absence of kernel patching documented.", tbl_cell)]
    ]
    t_status = Table(r1_status_data, colWidths=[130, 55, 330])
    t_status.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f2b5c')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(TableBlock(t_status, "Table 1: Deliverable status matrix tracking Review 1 commitments."))
    
    story.append(H2("Critical Engineering Revisions Made Since Review 1"))
    story.append(B("<b>Implementation Language Selected:</b> Standardized on Python 3.10+, Pytest for regression suites, Matplotlib for graphics, and CSV/JSON for audit records, resolving the open choice from Review 1."))
    story.append(B("<b>Calibration of Workload W1:</b> The initial draft generated arrivals every 3 units with bursts 6–10 (offered load 2.7), which inadvertently overloaded the queue. W1 inter-arrival gaps were calibrated to 9 units (offered load 0.89) to establish a truly balanced baseline. All 200 simulation runs were executed using this calibrated baseline."))
    story.append(B("<b>Ablation and Scaling Integration:</b> Formalized component ablations (no-aging and no-share configurations) and execution runtime scaling curves (10 to 500 tasks) to empirically dissect algorithmic bottlenecks."))

    story.append(H1("1. Finalized System Architecture (Common Item 1 & Patent Architecture)"))
    arch_desc = (
        "The finalized architecture establishes strict decoupling between workload generation, event simulation, scheduling policy logic, "
        "and metric evaluation. This guarantees that all policies execute under identical deterministic conditions.<br/>"
        "The system comprises five operational tiers: (1) <b>Workload Ingestion & Validation Layer</b> verifying bounds on arrival, burst, and PID; "
        "(2) <b>Discrete-Event Simulation Core</b> managing process state transitions and the simulation clock; "
        "(3) <b>Pluggable Policy Layer</b> hosting baseline and AFAS algorithms; (4) <b>Decision Audit Logger</b> capturing per-quantum score breakdowns; "
        "and (5) <b>Evaluation & Visualization Layer</b> generating standard metrics and publication charts."
    )
    story.append(P(arch_desc))
    story.append(FigBlock(os.path.join(r1_dir, "r1_img_1_page11.png"), 400, 215, "Figure 1: Finalized block diagram of the AFAS discrete-event CPU scheduling simulator."))
    story.append(PageBreak())

    # ================= PAGE 3: METHODOLOGY & MATH =================
    story.append(H2("1.1 Hardware and Software Execution Boundaries"))
    story.append(B("<b>Hardware Boundary:</b> Emulates a uniprocessor system with discrete time ticks. Timer interrupts are emulated via quantum boundaries (q=4). Multicore load balancing, NUMA migration, and cache hierarchies are out of scope."))
    story.append(B("<b>Software Boundary:</b> Runs purely in user-space in Python 3.10+. It avoids kernel-level instability while maintaining strict mathematical determinism."))

    story.append(H1("2. Detailed Methodology (Common Item 2 & Conference Methodology)"))
    story.append(P(
        "Our methodology relies on reproducible discrete-event simulation governed by deterministic state transitions and formal invariants. "
        "At each scheduling boundary, the simulator evaluates the ready queue, assigns processor time according to the active policy, and logs all state alterations."
    ))
    story.append(H2("2.1 AFAS Dynamic Priority Scoring Mathematical Model"))
    story.append(P(
        "For every process <i>i</i> present in the ready queue at simulated time <i>t</i>, the AFAS policy computes a composite score S<sub>i</sub>(t) defined as:"
    ))
    
    formula_text = (
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>S<sub>i</sub>(t) = w<sub>p</sub> &middot; P<sub>i</sub> + w<sub>a</sub> &middot; A<sub>i</sub>(t) + w<sub>r</sub> &middot; R<sub>i</sub> - w<sub>c</sub> &middot; C<sub>i</sub>(t)</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>Subject to:</b> &nbsp; w<sub>p</sub> + w<sub>a</sub> + w<sub>r</sub> + w<sub>c</sub> = 1, &nbsp;&nbsp; w<sub>k</sub> &ge; 0 &nbsp; &forall; k &isin; {p, a, r, c}"
    )
    story.append(Table([[Paragraph(formula_text, code_block_style)]], colWidths=[515], style=[
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#94a3b8')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4)
    ]))
    story.append(Spacer(1, 3))
    
    story.append(P("The mathematical components of the scoring model are formally bounded in [0, 1]:"))
    story.append(B("<b>Normalized Base Priority (P<sub>i</sub>):</b> P<sub>i</sub> = Priority<sub>i</sub> / 10 &isin; [0.1, 1.0], representing static administrative urgency (1 = lowest, 10 = highest)."))
    story.append(B("<b>Bounded Waiting-Time Aging (A<sub>i</sub>(t)):</b> A<sub>i</sub>(t) = min(1.0, (t - t<sub>last_cpu</sub>) / 50) &isin; [0.0, 1.0], where t<sub>last_cpu</sub> is the timestamp when process i last relinquished the CPU (or its arrival time if unserved). The hard ceiling of 50 time units guarantees that aging boosts remain strictly bounded, preventing low-priority tasks from permanently starving higher-priority interactive tasks."))
    story.append(B("<b>Workload Responsiveness Factor (R<sub>i</sub>):</b> Categorical factor reflecting task interactivity: R<sub>i</sub> = 1.0 for interactive tasks, 0.5 for mixed workloads, and 0.2 for CPU-bound batch tasks."))
    story.append(B("<b>Decayed Recent CPU-Share Penalty (C<sub>i</sub>(t)):</b> C<sub>i</sub>(t) = min(1.0, Service<sub>decayed</sub>(t) / 40) &isin; [0.0, 1.0]. CPU consumption is tracked with exponential decay: Service<sub>decayed</sub>(t) = &Sigma; &Delta;&tau; &middot; 2<sup>-(t - &tau;)/40</sup>, using a half-life parameter of 40 time units."))
    story.append(B("<b>Deterministic Tie-Breaking Hierarchy:</b> In the event of identical scores, ties are resolved deterministically: (1) higher S<sub>i</sub>(t), (2) earlier arrival time t<sub>arrival</sub>, and (3) lower process identifier (PID)."))

    story.append(H2("2.2 Simulation Verification Invariants"))
    story.append(P("To ensure 100% scientific validity, every execution trace is subjected to three mandatory invariants before metric evaluation:"))
    story.append(B("<b>Invariant 1 (Mutual Exclusion / Non-overlap):</b> &forall; segments j, start<sub>j+1</sub> &ge; end<sub>j</sub>. No two processes occupy the simulated CPU simultaneously."))
    story.append(B("<b>Invariant 2 (Exact Burst Conservation):</b> &forall; processes i, &Sigma; (end<sub>j</sub> - start<sub>j</sub>) = Burst<sub>i</sub>. Every process receives exactly its required CPU burst—neither dropped nor over-executed."))
    story.append(B("<b>Invariant 3 (Strict Temporal Causality):</b> &forall; segments j of process i, start<sub>j</sub> &ge; Arrival<sub>i</sub>. No process executes before its declared arrival time."))
    story.append(PageBreak())

    # ================= PAGE 4: ALGORITHM & FLOWCHART =================
    story.append(H1("3. Algorithm and Flowchart (Common Item 3 & Patent Sequence/Workflow)"))
    story.append(P(
        "The complete AFAS scheduling procedure is formalized in Algorithm 1. The execution workflow is depicted in Figure 2, "
        "highlighting the continuous Input &rarr; Processing &rarr; Decision &rarr; Output cycle required for patent evaluation."
    ))
    
    algo_box = """
    <b>Algorithm 1: AFAS Dispatcher and Dynamic Scoring Execution Loop</b><br/>
    <b>Input:</b> Process set P = {P_1, P_2, ..., P_n}, Quantum q = 4, Weights (w_p=0.30, w_a=0.40, w_r=0.15, w_c=0.15)<br/>
    <b>Output:</b> Execution segment trace T = {(pid, t_start, t_end)}, Metric summary M<br/>
    1: Initialize Clock t &larr; 0, ReadyQueue Q &larr; &empty;, Trace T &larr; &empty;, InactiveQueue &larr; P<br/>
    2: <b>while</b> Q is not empty <b>or</b> InactiveQueue is not empty <b>do</b><br/>
    3: &nbsp;&nbsp;&nbsp;&nbsp;Transfer newly arrived processes (Arrival_i &le; t) from InactiveQueue into Q<br/>
    4: &nbsp;&nbsp;&nbsp;&nbsp;<b>if</b> Q is empty <b>then</b> Advance Clock t &larr; min_{P_k &isin; InactiveQueue}(Arrival_k); Continue<br/>
    5: &nbsp;&nbsp;&nbsp;&nbsp;<b>for each</b> process P_i &isin; Q <b>do</b><br/>
    6: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Update waiting age A_i(t) &larr; min(1.0, (t - LastExit_i) / 50)<br/>
    7: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Update decayed CPU service C_i(t) using half-life &lambda; = 40<br/>
    8: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Compute score S_i(t) &larr; w_p &middot; P_i + w_a &middot; A_i(t) + w_r &middot; R_i - w_c &middot; C_i(t)<br/>
    9: &nbsp;&nbsp;&nbsp;&nbsp;P_sel &larr; Select P_i with max S_i(t) using tie-break (Score &darr;, Arrival &uarr;, PID &uarr;)<br/>
    10:&nbsp;&nbsp;&nbsp;&nbsp;slice &larr; min(q, RemainingBurst_sel)<br/>
    11:&nbsp;&nbsp;&nbsp;&nbsp;Record execution segment (PID_sel, t, t + slice) into Trace T<br/>
    12:&nbsp;&nbsp;&nbsp;&nbsp;Log decision tuple (t, PID_sel, |Q|, w_p P_i, w_a A_i, w_r R_i, -w_c C_i, Score) to AuditLog<br/>
    13:&nbsp;&nbsp;&nbsp;&nbsp;RemainingBurst_sel &larr; RemainingBurst_sel - slice; Clock t &larr; t + slice<br/>
    14:&nbsp;&nbsp;&nbsp;&nbsp;Update LastExit_sel &larr; t, Accumulate CPU service into Service_sel<br/>
    15:&nbsp;&nbsp;&nbsp;&nbsp;<b>if</b> RemainingBurst_sel &gt; 0 <b>then</b> Re-insert P_sel into Q <b>else</b> Mark P_sel TERMINATED<br/>
    16: Verify Engine Invariants (Non-overlap, Burst Conservation, Causality) on Trace T<br/>
    17: Compute performance metrics (TAT, WT, RT, Jain Index, Starvation Warnings) &rarr; Return (T, M)
    """
    story.append(Table([[Paragraph(algo_box, code_block_style)]], colWidths=[515], style=[
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#64748b')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3)
    ]))
    story.append(Cap("Algorithm 1: Formal execution procedure for the Adaptive Fairness-Aware Scheduler."))
    story.append(Spacer(1, 4))
    story.append(FigBlock(os.path.join(r1_dir, "r1_img_2_page12.png"), 280, 240, "Figure 2: Complete simulation workflow flowchart depicting state transitions and decision logic."))
    story.append(PageBreak())

    # ================= PAGE 5: MODULE-WISE IMPLEMENTATION & TECH =================
    story.append(H1("4. Module-Wise Implementation (Common Item 4 & Patent Functioning)"))
    mod_table_data = [
        [Paragraph("Module File", tbl_header), Paragraph("Primary Class / Functions", tbl_header), Paragraph("Functional Responsibilities & State Management", tbl_header)],
        [Paragraph("afas_sim.py", tbl_cell_code), Paragraph("Process, SimulationEngine", tbl_cell_bold), Paragraph("Defines Process Control Block (PCB) attributes (PID, arrival, burst, remaining burst, priority, class, last_exit, decayed_service); enforces the 3 execution invariants.", tbl_cell)],
        [Paragraph("afas_sim.py", tbl_cell_code), Paragraph("run_fcfs, run_sjf, run_srtf, run_rr, run_priority", tbl_cell_bold), Paragraph("Baseline execution engines. Implements classic scheduling algorithms using identical queue containers and segment dispatch interfaces.", tbl_cell)],
        [Paragraph("afas_sim.py", tbl_cell_code), Paragraph("run_afas, compute_afas_score", tbl_cell_bold), Paragraph("Core AFAS dispatcher. Dynamically normalizes features, computes S_i(t), performs deterministic tie-breaking, and outputs per-quantum decision audit records.", tbl_cell)],
        [Paragraph("afas_sim.py", tbl_cell_code), Paragraph("compute_metrics", tbl_cell_bold), Paragraph("Converts segment traces into CT, TAT, WT, RT (mean, median, p95), context switch counts, Jain fairness index, and starvation warning counts.", tbl_cell)],
        [Paragraph("test_sim.py", tbl_cell_code), Paragraph("12 Pytest Unit Test Cases", tbl_cell_bold), Paragraph("Regression and verification test suite: validates hand-calculated cases, idle-gap processing, invariant checks across 25 workloads, tie-breaks, and input rejections.", tbl_cell)],
        [Paragraph("experiments.py", tbl_cell_code), Paragraph("run_all_experiments", tbl_cell_bold), Paragraph("Batch runner executing 200 simulation runs across 5 workload families x 5 seeds. Automates ablation studies, sensitivity sweeps, quantum sweeps, and runtime scaling.", tbl_cell)],
        [Paragraph("charts.py", tbl_cell_code), Paragraph("generate_all_figures", tbl_cell_bold), Paragraph("Matplotlib publication chart engine. Generates Gantt charts, per-workload bar charts, ablation plots, sensitivity curves, and scaling graphs.", tbl_cell)]
    ]
    t_mod = Table(mod_table_data, colWidths=[75, 125, 315])
    t_mod.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f2b5c')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(TableBlock(t_mod, "Table 2: Implementation module mapping and architectural responsibilities."))

    story.append(H2("4.1 Novel Interaction Between Modules"))
    story.append(P(
        "A key architectural novelty of the AFAS simulator is the <b>decoupled Decision Audit Logger</b>. "
        "In traditional operating system schedulers, priority calculations occur internally within runqueue red-black trees or heap adjustments, "
        "rendering the real-time rationale for thread preemption opaque. In AFAS, the Policy Engine continuously outputs an immutable score decomposition tuple "
        "&lang;t, PID, |Q|, w<sub>p</sub>P<sub>i</sub>, w<sub>a</sub>A<sub>i</sub>, w<sub>r</sub>R<sub>i</sub>, -w<sub>c</sub>C<sub>i</sub>, S<sub>i</sub>(t)&rang; "
        "to the Audit Log before dispatching the chosen process slice. This enables external validation, real-time explainability, "
        "and invariant auditing without interfering with the internal state machine."
    ))

    story.append(H1("5. Technologies and Tools Used (Common Item 5)"))
    tech_data = [
        [Paragraph("Technology / Tool", tbl_header), Paragraph("Version", tbl_header), Paragraph("Role in Project", tbl_header), Paragraph("Technical Justification", tbl_header)],
        [Paragraph("Python 3", tbl_cell_bold), Paragraph("3.10.12+", tbl_cell), Paragraph("Core Simulation Engine", tbl_cell), Paragraph("Provides deterministic queue abstractions, rapid algorithmic prototyping, and native high-precision arithmetic.", tbl_cell)],
        [Paragraph("Pytest", tbl_cell_bold), Paragraph("8.1.1", tbl_cell), Paragraph("Automated Invariant Testing", tbl_cell), Paragraph("Enables strict regression testing across hand-calculated cases and invariant verification on all 25 workload instances.", tbl_cell)],
        [Paragraph("NumPy", tbl_cell_bold), Paragraph("1.26+", tbl_cell), Paragraph("Vectorized Statistics", tbl_cell), Paragraph("Efficient calculation of percentiles (p95), Jain fairness indices, and matrix aggregations over 200 runs.", tbl_cell)],
        [Paragraph("Matplotlib", tbl_cell_bold), Paragraph("3.8+", tbl_cell), Paragraph("Visualization & Plots", tbl_cell), Paragraph("Generates publication-quality Gantt execution charts, sensitivity response curves, and logarithmic scaling plots.", tbl_cell)],
        [Paragraph("ReportLab", tbl_cell_bold), Paragraph("5.0+", tbl_cell), Paragraph("PDF Report Engine", tbl_cell), Paragraph("Programmatic compilation of academic documents with dynamic headers, footers, and table formatting.", tbl_cell)],
        [Paragraph("Git & GitHub", tbl_cell_bold), Paragraph("2.40+", tbl_cell), Paragraph("Version Control", tbl_cell), Paragraph("Maintains immutable commit history of algorithm changes, test configurations, and experimental seeds.", tbl_cell)],
        [Paragraph("CSV / JSON", tbl_cell_bold), Paragraph("Standard", tbl_cell), Paragraph("Audit & Raw Storage", tbl_cell), Paragraph("Portable, human-readable records allowing independent verification of per-quantum scheduling decisions.", tbl_cell)]
    ]
    t_tech = Table(tech_data, colWidths=[70, 55, 115, 275])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f2b5c')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(TableBlock(t_tech, "Table 3: Comprehensive technology stack, versions, and selection rationale."))
    story.append(PageBreak())

    # ================= PAGE 6: DATASETS, PREPROCESSING & VERIFICATION =================
    story.append(H1("6. Dataset Description (Common Item 6 & Conference Dataset)"))
    story.append(P("Five synthetic workload families (W1–W5) were constructed to evaluate policies under varied traffic regimes:"))
    wk_data = [
        [Paragraph("Workload Family", tbl_header), Paragraph("Process Generation Rule (n = Process Count)", tbl_header), Paragraph("n", tbl_header), Paragraph("Offered Load*", tbl_header), Paragraph("Target Evaluation Objective", tbl_header)],
        [Paragraph("W1: Uniform Batch", tbl_cell_bold), Paragraph("One arrival every 9 units; burst 6–10; priority 3–7; random class.", tbl_cell), Paragraph("20", tbl_cell), Paragraph("0.89", tbl_cell), Paragraph("Tests whether AFAS preserves baseline behavior when queue is lightly loaded.", tbl_cell)],
        [Paragraph("W2: Mixed Bursts", tbl_cell_bold), Paragraph("70% short interactive jobs (burst 2–5), 30% long batch jobs (burst 25–45); arrivals in [0, 60]; priority 1–10.", tbl_cell), Paragraph("20", tbl_cell), Paragraph("4.70", tbl_cell), Paragraph("Evaluates response time for short jobs vs starvation risk for long-running batch jobs.", tbl_cell)],
        [Paragraph("W3: Priority Skew", tbl_cell_bold), Paragraph("6 low-priority batch jobs (priority 1–2, burst 10–20) arrive at t &isin; [0, 5]; 18 high-priority interactive jobs (priority 8–10, burst 5–9) arrive every ~5 units.", tbl_cell), Paragraph("24", tbl_cell), Paragraph("2.50", tbl_cell), Paragraph("Deliberate starvation stress test: evaluates whether aging rescues low-priority tasks.", tbl_cell)],
        [Paragraph("W4: Burst Arrivals", tbl_cell_bold), Paragraph("3 discrete bursts of 7 jobs arriving simultaneously within 3 units at t = 0, 40, 80; burst 3–15.", tbl_cell), Paragraph("21", tbl_cell), Paragraph("2.40", tbl_cell), Paragraph("Measures queue recovery time and scheduling stability during sudden traffic surges.", tbl_cell)],
        [Paragraph("W5: Share Imbalance", tbl_cell_bold), Paragraph("3 long high-priority batch jobs (burst 60–90) competing with 12 light interactive jobs (burst 2–6) arriving in [0, 100].", tbl_cell), Paragraph("15", tbl_cell), Paragraph("3.00", tbl_cell), Paragraph("Evaluates whether the recent-CPU-share penalty prevents long tasks from monopolizing the CPU.", tbl_cell)]
    ]
    t_wk = Table(wk_data, colWidths=[80, 185, 20, 50, 180])
    t_wk.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f2b5c')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(TableBlock(t_wk, "Table 4: Workload specifications. *Offered Load = &Sigma; Burst / (Arrival Span), averaged over seeds. Load > 1 indicates congested queues."))

    story.append(H1("7. Data Preprocessing and Feature Normalization (Common Item 7)"))
    story.append(P("All scheduling inputs undergo mathematical normalization to the unit interval [0, 1]:"))
    story.append(B("<b>Base Priority:</b> P<sub>i</sub> = Priority<sub>i</sub> / 10 &isin; [0.1, 1.0]."))
    story.append(B("<b>Waiting Age Bounding:</b> A<sub>i</sub>(t) = min(1.0, (t - t<sub>last_cpu</sub>) / 50) &isin; [0.0, 1.0], saturating at 50 time units."))
    story.append(B("<b>Workload Responsiveness Mapping:</b> Interactive &rarr; 1.0, Mixed &rarr; 0.5, Batch &rarr; 0.2."))
    story.append(B("<b>Decayed CPU Share:</b> C<sub>i</sub>(t) = min(1.0, Service<sub>decayed</sub> / 40) &isin; [0.0, 1.0], with half-life of 40 units."))
    story.append(B("<b>Weight Simplex Projection:</b> User weights are projected: w<sub>k</sub>' = w<sub>k</sub> / &Sigma; w<sub>j</sub>, guaranteeing &Sigma; w<sub>k</sub>' = 1.0."))

    story.append(H1("8. Experimental Setup and Baselines (Common Item 8 & Conference Setup)"))
    story.append(P("Baselines: FCFS, non-preemptive SJF, preemptive SRTF, Round Robin (q=4), and non-preemptive Priority scheduling. Verified on hand-solved 4-process case:"))
    verif_data = [
        [Paragraph("Scheduling Policy", tbl_header), Paragraph("Hand-Calculated Completion Times (P1, P2, P3, P4)", tbl_header), Paragraph("Analytical Mean WT", tbl_header), Paragraph("Simulator Result", tbl_header), Paragraph("Verification Status", tbl_header)],
        [Paragraph("FCFS", tbl_cell_bold), Paragraph("P1: 5, &nbsp; P2: 8, &nbsp; P3: 16, &nbsp; P4: 22", tbl_cell), Paragraph("5.75", tbl_cell), Paragraph("5.750", tbl_cell), Paragraph("PASSED (Exact Match)", tbl_cell_bold)],
        [Paragraph("SJF (Non-preemptive)", tbl_cell_bold), Paragraph("P1: 5, &nbsp; P2: 8, &nbsp; P3: 22, &nbsp; P4: 14", tbl_cell), Paragraph("5.25", tbl_cell), Paragraph("5.250", tbl_cell), Paragraph("PASSED (Exact Match)", tbl_cell_bold)],
        [Paragraph("SRTF (Preemptive)", tbl_cell_bold), Paragraph("P1: 8, &nbsp; P2: 4, &nbsp; P3: 22, &nbsp; P4: 14", tbl_cell), Paragraph("5.00", tbl_cell), Paragraph("5.000", tbl_cell), Paragraph("PASSED (Exact Match)", tbl_cell_bold)],
        [Paragraph("Round Robin (q=2)", tbl_cell_bold), Paragraph("Checked on 3-process case: P1(0,4), P2(0,3), P3(0,2) &rarr; CT: 9, 8, 5", tbl_cell), Paragraph("3.67", tbl_cell), Paragraph("3.667", tbl_cell), Paragraph("PASSED (Exact Match)", tbl_cell_bold)],
        [Paragraph("Priority (No aging)", tbl_cell_bold), Paragraph("Checked on priority test case: higher priority always dispatches first", tbl_cell), Paragraph("Deterministic", tbl_cell), Paragraph("Deterministic", tbl_cell), Paragraph("PASSED (Exact Match)", tbl_cell_bold)]
    ]
    t_verif = Table(verif_data, colWidths=[95, 180, 75, 75, 90])
    t_verif.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f2b5c')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(TableBlock(t_verif, "Table 5: Analytical verification results confirming mathematical correctness of simulator baselines."))
    story.append(PageBreak())

    # ================= PAGE 7: SCREENSHOTS PART 1 =================
    story.append(H1("9. Initial Implementation Screenshots (Common Item 9 & Prototype Evidence)"))
    story.append(P(
        "To satisfy the VIT IDF requirement for tangible prototype evidence demonstrating that the project is actively implemented, "
        "Figures 3, 4, 5, and 6 provide real console execution traces of the simulator, automated test suite, and analytical toolchain."
    ))
    story.append(FigBlock(os.path.join(sc_dir, "screenshot_pytest.png"), 440, 205, "Figure 3: Automated Pytest test suite execution showing 12 passed tests verifying invariants, tie-breaks, and hand-solved cases."))
    story.append(Spacer(1, 4))
    story.append(FigBlock(os.path.join(sc_dir, "screenshot_experiments.png"), 440, 215, "Figure 4: Automated batch experiment runner executing 200 simulation runs across 5 workloads and 5 seeds."))
    story.append(PageBreak())

    # ================= PAGE 8: SCREENSHOTS PART 2 & RESULTS SUMMARY =================
    story.append(FigBlock(os.path.join(sc_dir, "screenshot_decision_log.png"), 440, 205, "Figure 5: Live console output of the AFAS Decision Audit Logger displaying real-time score decomposition and aging activation."))
    story.append(Spacer(1, 2))
    story.append(FigBlock(os.path.join(sc_dir, "screenshot_cli_gantt.png"), 440, 140, "Figure 6: Automated chart generation toolchain compiling high-resolution publication figures from CSV logs."))
    story.append(Spacer(1, 4))

    story.append(H1("10. Preliminary Results and Empirical Analysis (Common Item 10 & Conference Results)"))
    story.append(P(
        "Table 6 summarizes the aggregated performance metrics across all five workload families (W1–W5) and five seeds. "
        "Metrics represent the mean across 25 workload instances."
    ))
    
    results_summary_data = [
        [Paragraph("Scheduling Policy", tbl_header), Paragraph("Avg WT (&darr;)", tbl_header), Paragraph("Avg RT (&darr;)", tbl_header), Paragraph("p95 RT (&darr;)", tbl_header), Paragraph("Max Wait (&darr;)", tbl_header), Paragraph("Context Sw.", tbl_header), Paragraph("Jain Index (&uarr;)", tbl_header), Paragraph("Warnings (&darr;)", tbl_header)],
        [Paragraph("FCFS", tbl_cell), Paragraph("79.20", tbl_cell), Paragraph("79.20", tbl_cell), Paragraph("122.50", tbl_cell), Paragraph("126.80", tbl_cell), Paragraph("19.0", tbl_cell), Paragraph("0.50", tbl_cell), Paragraph("12.0", tbl_cell)],
        [Paragraph("SJF (Non-preemptive)", tbl_cell), Paragraph("37.00", tbl_cell), Paragraph("37.00", tbl_cell), Paragraph("127.60", tbl_cell), Paragraph("146.60", tbl_cell), Paragraph("19.0", tbl_cell), Paragraph("0.68", tbl_cell), Paragraph("5.3", tbl_cell)],
        [Paragraph("SRTF (Preemptive)", tbl_cell), Paragraph("<b>29.40</b>", tbl_cell), Paragraph("26.60", tbl_cell), Paragraph("123.10", tbl_cell), Paragraph("146.50", tbl_cell), Paragraph("21.7", tbl_cell), Paragraph("<b>0.80</b>", tbl_cell), Paragraph("<b>4.1</b>", tbl_cell)],
        [Paragraph("Round Robin (q=4)", tbl_cell), Paragraph("65.60", tbl_cell), Paragraph("19.30", tbl_cell), Paragraph("<b>36.10</b>", tbl_cell), Paragraph("<b>39.20</b>", tbl_cell), Paragraph("56.8", tbl_cell), Paragraph("0.78", tbl_cell), Paragraph("11.0", tbl_cell)],
        [Paragraph("Priority (No aging)", tbl_cell), Paragraph("76.30", tbl_cell), Paragraph("76.30", tbl_cell), Paragraph("158.70", tbl_cell), Paragraph("168.20", tbl_cell), Paragraph("19.0", tbl_cell), Paragraph("0.55", tbl_cell), Paragraph("9.0", tbl_cell)],
        [Paragraph("<b>AFAS (Proposed, q=4)</b>", tbl_cell_bold), Paragraph("<b>52.30</b>", tbl_cell_bold), Paragraph("<b>18.20</b>", tbl_cell_bold), Paragraph("<b>52.50</b>", tbl_cell_bold), Paragraph("<b>68.20</b>", tbl_cell_bold), Paragraph("<b>54.7</b>", tbl_cell_bold), Paragraph("<b>0.69</b>", tbl_cell_bold), Paragraph("<b>4.6</b>", tbl_cell_bold)]
    ]
    t_res = Table(results_summary_data, colWidths=[95, 55, 55, 55, 55, 55, 55, 55])
    t_res.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f2b5c')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('BACKGROUND', (0,6), (-1,6), colors.HexColor('#eff6ff')),
        ('ROWBACKGROUNDS', (0,1), (-1,5), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(TableBlock(t_res, "Table 6: Global empirical benchmark results averaged across W1–W5 (5 seeds each, 200 total simulation runs)."))
    story.append(PageBreak())

    # ================= PAGE 9: BAR CHARTS & SEED CONSISTENCY =================
    fig_tbl_data = [
        [Image(os.path.join(fig_dir, "fig_1.png"), width=245, height=130), Image(os.path.join(fig_dir, "fig_2.png"), width=245, height=130)],
        [Cap("Figure 7: Maximum ready-queue wait gap per workload."), Cap("Figure 8: 95th-percentile response time per workload.")]
    ]
    t_figs1 = Table(fig_tbl_data, colWidths=[255, 255])
    t_figs1.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(TableBlock(t_figs1))

    story.append(H2("10.1 Key Empirical Findings"))
    story.append(B("<b>AFAS vs Priority (Starvation Elimination):</b> AFAS slashes the maximum ready-queue wait gap from 168.2 down to 68.2 (<b>59% reduction</b>) and p95 response time from 158.7 to 52.5. By factoring in waiting-age boost A_i(t), low-priority tasks are dynamically promoted before severe starvation occurs."))
    story.append(B("<b>AFAS vs Round Robin (Interactivity vs Tail Bounding):</b> AFAS achieves superior average response time (18.2 vs 19.3) and 20% lower average waiting time (52.3 vs 65.6). Context switches are comparable (54.7 vs 56.8). However, Round Robin maintains a tighter tail wait bound (39.2 vs 68.2) and higher Jain fairness (0.78 vs 0.69) because it enforces strict cyclic rotation without priority bias."))
    story.append(B("<b>AFAS vs SJF/SRTF (Throughput vs Long-Job Starvation):</b> While SRTF minimizes average waiting time (29.4), it inflicts severe long-job starvation (max wait 146.5). AFAS prevents long jobs from being starved, bounding maximum delay to 68.2."))

    story.append(H2("10.2 Consistency Across Seeds (Paired Win/Loss Counts)"))
    story.append(P("To verify that aggregate averages are not skewed by anomalous random seeds, Table 7 reports paired win counts over all 25 workload instances:"))
    
    paired_data = [
        [Paragraph("AFAS Compared Against", tbl_header), Paragraph("Max Wait Gap: AFAS Lower", tbl_header), Paragraph("Avg Waiting Time: AFAS Lower", tbl_header), Paragraph("Avg Response Time: AFAS Lower", tbl_header)],
        [Paragraph("FCFS", tbl_cell_bold), Paragraph("13 of 25 (3 ties in W1)", tbl_cell), Paragraph("14 of 25 (3 ties in W1)", tbl_cell), Paragraph("22 of 25 (3 ties in W1)", tbl_cell)],
        [Paragraph("SJF (Non-preemptive)", tbl_cell_bold), Paragraph("20 of 25 (3 ties in W1)", tbl_cell), Paragraph("4 of 25 (3 ties in W1)", tbl_cell), Paragraph("22 of 25 (3 ties in W1)", tbl_cell)],
        [Paragraph("SRTF (Preemptive)", tbl_cell_bold), Paragraph("20 of 25 (3 ties in W1)", tbl_cell), Paragraph("0 of 25 (3 ties in W1)", tbl_cell), Paragraph("21 of 25 (3 ties in W1)", tbl_cell)],
        [Paragraph("Round Robin (q=4)", tbl_cell_bold), Paragraph("1 of 25 (3 ties in W1)", tbl_cell), Paragraph("19 of 25 (3 ties in W1)", tbl_cell), Paragraph("11 of 25 (3 ties in W1)", tbl_cell)],
        [Paragraph("Priority (No aging)", tbl_cell_bold), Paragraph("20 of 25 (3 ties in W1)", tbl_cell), Paragraph("10 of 25 (3 ties in W1)", tbl_cell), Paragraph("22 of 25 (3 ties in W1)", tbl_cell)]
    ]
    t_pair = Table(paired_data, colWidths=[120, 130, 130, 130])
    t_pair.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f2b5c')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(TableBlock(t_pair, "Table 7: Paired win counts across 25 workload instances. W1 accounts for ties due to low queue contention."))
    story.append(PageBreak())

    # ================= PAGE 10: CASE STUDY & ABLATION =================
    story.append(H2("10.3 Timeline Case Study: W3 Priority Skew (Gantt Analysis)"))
    story.append(P(
        "Figure 9 demonstrates the operational differences on an 11-process workload (3 low-priority batch tasks P1–P3, 8 high-priority interactive tasks P4–P11). "
        "Under Priority scheduling, P1–P3 starve until t = 54. Round Robin aggressively rotates slices, incurring 30 context switches. "
        "AFAS dynamically elevates low-priority batch tasks as their waiting age accumulates, scheduling P1 at t = 50 while preserving low context switches (28)."
    ))
    story.append(FigBlock(os.path.join(fig_dir, "fig_4.png"), 450, 175, "Figure 9: Gantt execution timelines for Priority, Round Robin, and AFAS on an 11-process workload."))
    
    dec_data = [
        [Paragraph("t", tbl_header), Paragraph("Chosen", tbl_header), Paragraph("Ready", tbl_header), Paragraph("w_p &middot; P_i", tbl_header), Paragraph("w_a &middot; A_i(t)", tbl_header), Paragraph("w_r &middot; R_i", tbl_header), Paragraph("-w_c &middot; C_i(t)", tbl_header), Paragraph("Total Score", tbl_header)],
        [Paragraph("0", tbl_cell), Paragraph("P4", tbl_cell_bold), Paragraph("1", tbl_cell), Paragraph("0.270", tbl_cell), Paragraph("0.000", tbl_cell), Paragraph("0.150", tbl_cell), Paragraph("-0.000", tbl_cell), Paragraph("0.420", tbl_cell_bold)],
        [Paragraph("4", tbl_cell), Paragraph("P4", tbl_cell_bold), Paragraph("4", tbl_cell), Paragraph("0.270", tbl_cell), Paragraph("0.000", tbl_cell), Paragraph("0.150", tbl_cell), Paragraph("-0.014", tbl_cell), Paragraph("0.406", tbl_cell_bold)],
        [Paragraph("5", tbl_cell), Paragraph("P5", tbl_cell_bold), Paragraph("4", tbl_cell), Paragraph("0.270", tbl_cell), Paragraph("0.000", tbl_cell), Paragraph("0.150", tbl_cell), Paragraph("-0.000", tbl_cell), Paragraph("0.420", tbl_cell_bold)],
        [Paragraph("9", tbl_cell), Paragraph("P5", tbl_cell_bold), Paragraph("4", tbl_cell), Paragraph("0.270", tbl_cell), Paragraph("0.000", tbl_cell), Paragraph("0.150", tbl_cell), Paragraph("-0.014", tbl_cell), Paragraph("0.406", tbl_cell_bold)],
        [Paragraph("13", tbl_cell), Paragraph("P6", tbl_cell_bold), Paragraph("4", tbl_cell), Paragraph("0.300", tbl_cell), Paragraph("0.008", tbl_cell), Paragraph("0.150", tbl_cell), Paragraph("-0.000", tbl_cell), Paragraph("0.458", tbl_cell_bold)],
        [Paragraph("17", tbl_cell), Paragraph("P7", tbl_cell_bold), Paragraph("5", tbl_cell), Paragraph("0.300", tbl_cell), Paragraph("0.008", tbl_cell), Paragraph("0.150", tbl_cell), Paragraph("-0.000", tbl_cell), Paragraph("0.458", tbl_cell_bold)],
        [Paragraph("21", tbl_cell), Paragraph("P6", tbl_cell_bold), Paragraph("6", tbl_cell), Paragraph("0.300", tbl_cell), Paragraph("0.032", tbl_cell), Paragraph("0.150", tbl_cell), Paragraph("-0.012", tbl_cell), Paragraph("0.470", tbl_cell_bold)],
        [Paragraph("22", tbl_cell), Paragraph("P7", tbl_cell_bold), Paragraph("5", tbl_cell), Paragraph("0.300", tbl_cell), Paragraph("0.008", tbl_cell), Paragraph("0.150", tbl_cell), Paragraph("-0.013", tbl_cell), Paragraph("0.445", tbl_cell_bold)],
        [Paragraph("25", tbl_cell), Paragraph("P8", tbl_cell_bold), Paragraph("4", tbl_cell), Paragraph("0.240", tbl_cell), Paragraph("0.040", tbl_cell), Paragraph("0.150", tbl_cell), Paragraph("-0.000", tbl_cell), Paragraph("0.430", tbl_cell_bold)],
        [Paragraph("29", tbl_cell), Paragraph("P9", tbl_cell_bold), Paragraph("5", tbl_cell), Paragraph("0.240", tbl_cell), Paragraph("0.024", tbl_cell), Paragraph("0.150", tbl_cell), Paragraph("-0.000", tbl_cell), Paragraph("0.414", tbl_cell_bold)]
    ]
    t_dec = Table(dec_data, colWidths=[35, 55, 45, 60, 65, 65, 65, 65])
    t_dec.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f2b5c')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(TableBlock(t_dec, "Table 8: First ten scheduling decisions extracted from the Decision Audit Log for the case study workload."))

    story.append(H2("10.4 Ablation Study: Dissecting Component Contributions"))
    ablation_data = [
        [Paragraph("Configuration", tbl_header), Paragraph("Avg WT (&darr;)", tbl_header), Paragraph("Avg RT (&darr;)", tbl_header), Paragraph("p95 RT (&darr;)", tbl_header), Paragraph("Max Wait Gap (&darr;)", tbl_header), Paragraph("Jain Index (&uarr;)", tbl_header), Paragraph("Warnings (&darr;)", tbl_header)],
        [Paragraph("<b>AFAS (Full Model)</b>", tbl_cell_bold), Paragraph("52.30", tbl_cell), Paragraph("18.20", tbl_cell), Paragraph("52.50", tbl_cell), Paragraph("<b>68.20</b>", tbl_cell_bold), Paragraph("0.69", tbl_cell), Paragraph("<b>4.6</b>", tbl_cell_bold)],
        [Paragraph("AFAS no-aging (w_a = 0)", tbl_cell), Paragraph("46.40", tbl_cell), Paragraph("29.60", tbl_cell), Paragraph("115.50", tbl_cell), Paragraph("138.60 (<b>+103%</b>)", tbl_cell_bold), Paragraph("0.67", tbl_cell), Paragraph("5.8", tbl_cell)],
        [Paragraph("AFAS no-share (w_c = 0)", tbl_cell), Paragraph("52.60", tbl_cell), Paragraph("19.20", tbl_cell), Paragraph("53.60", tbl_cell), Paragraph("67.70 (<b>-0.7%</b>)", tbl_cell), Paragraph("0.69", tbl_cell), Paragraph("4.6", tbl_cell)]
    ]
    t_abl = Table(ablation_data, colWidths=[130, 60, 60, 65, 85, 55, 60])
    t_abl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f2b5c')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(TableBlock(t_abl, "Table 9: Component ablation benchmark results averaged across W1–W5."))
    story.append(FigBlock(os.path.join(fig_dir, "fig_5.png"), 420, 140, "Figure 10: Ablation comparison on workloads W2, W3, and W5, highlighting the critical role of the aging term."))
    story.append(PageBreak())

    # ================= PAGE 11: SENSITIVITY, QUANTUM, SCALING & PROBLEMS =================
    story.append(H2("10.5 Parameter Sensitivity, Time-Quantum, and Runtime Scaling Sweeps"))
    story.append(FigBlock(os.path.join(fig_dir, "fig_6.png"), 440, 130, "Figure 11: One-at-a-time parameter sensitivity analysis sweeping w_p, w_a, w_r, and w_c from 0.0 to 1.0."))
    
    fig_tbl_data2 = [
        [Image(os.path.join(fig_dir, "fig_8.png"), width=280, height=97), Image(os.path.join(fig_dir, "fig_7.png"), width=175, height=115)],
        [Cap("Figure 12: Quantum sweep (q=1 to 32) effect on latency."), Cap("Figure 13: Simulation runtime scaling (log-log).")]
    ]
    t_figs2 = Table(fig_tbl_data2, colWidths=[310, 205])
    t_figs2.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(TableBlock(t_figs2))

    scale_data = [
        [Paragraph("Process Count (N)", tbl_header), Paragraph("FCFS (ms)", tbl_header), Paragraph("Round Robin (ms)", tbl_header), Paragraph("SJF (ms)", tbl_header), Paragraph("Priority (ms)", tbl_header), Paragraph("SRTF (ms)", tbl_header), Paragraph("AFAS (ms)", tbl_header)],
        [Paragraph("10", tbl_cell_bold), Paragraph("0.01", tbl_cell), Paragraph("0.01", tbl_cell), Paragraph("0.02", tbl_cell), Paragraph("0.02", tbl_cell), Paragraph("0.03", tbl_cell), Paragraph("0.06", tbl_cell_bold)],
        [Paragraph("50", tbl_cell_bold), Paragraph("0.02", tbl_cell), Paragraph("0.08", tbl_cell), Paragraph("0.19", tbl_cell), Paragraph("0.21", tbl_cell), Paragraph("0.36", tbl_cell), Paragraph("1.98", tbl_cell_bold)],
        [Paragraph("100", tbl_cell_bold), Paragraph("0.03", tbl_cell), Paragraph("0.18", tbl_cell), Paragraph("0.46", tbl_cell), Paragraph("0.86", tbl_cell), Paragraph("3.08", tbl_cell), Paragraph("8.19", tbl_cell_bold)],
        [Paragraph("500", tbl_cell_bold), Paragraph("0.21", tbl_cell), Paragraph("1.13", tbl_cell), Paragraph("12.50", tbl_cell), Paragraph("20.00", tbl_cell), Paragraph("36.52", tbl_cell), Paragraph("222.51", tbl_cell_bold)]
    ]
    t_sc = Table(scale_data, colWidths=[85, 70, 70, 70, 70, 70, 80])
    t_sc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f2b5c')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(TableBlock(t_sc, "Table 10: Complete simulation runtime scaling across process counts (mean of 3 repetitions)."))

    story.append(H1("11. Problems Encountered and Technical Solutions (Common Item 11)"))
    prob_data = [
        [Paragraph("Technical Challenge / Defect", tbl_header), Paragraph("Observed Impact on Evaluation", tbl_header), Paragraph("Root Cause Diagnosis", tbl_header), Paragraph("Implemented Technical Resolution", tbl_header)],
        [
            Paragraph("1. Workload W1 Congestion Bug", tbl_cell_bold),
            Paragraph("Initial W1 generated offered load of 2.7 instead of 0.9, distorting baseline comparisons.", tbl_cell),
            Paragraph("Inter-arrival spacing of 3 units combined with bursts of 6–10 caused chronic queue saturation.", tbl_cell),
            Paragraph("Recalibrated arrival spacing to 9 units (offered load 0.89). Invalidated preliminary figures and re-ran all 200 experiments.", tbl_cell)
        ],
        [
            Paragraph("2. Recent CPU-Share Penalty Inactivity", tbl_cell_bold),
            Paragraph("Ablation and sensitivity sweeps revealed 0% impact from w_c on metrics.", tbl_cell),
            Paragraph("With q=4 and half-life of 40, C_i(t) stayed small; aging dominated score differences before share penalty took effect.", tbl_cell),
            Paragraph("Documented openly as an honest negative result. Redesigning share penalty in Review 3 relative to weighted fair-share ratio.", tbl_cell)
        ],
        [
            Paragraph("3. Starvation Warning Anomaly in RR", tbl_cell_bold),
            Paragraph("Round Robin exhibited high warning counts (11.0) despite lowest max wait (39.2).", tbl_cell),
            Paragraph("Fixed threshold of 40 time units counted repeated minor queue delays as multiple distinct warnings.", tbl_cell),
            Paragraph("Paired warning counts with Maximum Ready-Queue Wait Gap to distinguish chronic starvation from frequent cyclic slicing.", tbl_cell)
        ],
        [
            Paragraph("4. Quadratic Decision Complexity in AFAS", tbl_cell_bold),
            Paragraph("Simulation runtime exploded to 222.5 ms for 500 processes (~27x increase from 100).", tbl_cell),
            Paragraph("AFAS performs full-queue linear scans and re-computes S_i(t) for every ready task at every quantum boundary (O(N^2)).", tbl_cell),
            Paragraph("Identified architectural mitigation for Review 3: designing a bucketed priority queue with lazy score invalidation.", tbl_cell)
        ]
    ]
    t_prob = Table(prob_data, colWidths=[105, 125, 125, 160])
    t_prob.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f2b5c')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(TableBlock(t_prob, "Table 11: Summary of technical problems encountered, root cause analyses, and implemented solutions."))
    story.append(PageBreak())

    # ================= PAGE 12: PATENT NOVELTY & VIT IDF =================
    story.append(H1("12. Patent-Oriented Novelty Assessment & VIT IDF Compliance (PATENT Projects)"))
    story.append(P(
        "To fulfill the requirements of the VIT Invention Disclosure Form (IDF), the project underwent rigorous prior-art benchmarking "
        "against granted patent records to determine whether any technical aspect qualifies for intellectual property protection."
    ))
    story.append(H2("12.1 Detailed Working Principle of the Invention"))
    story.append(P(
        "The invention operates as an <b>inspectable, dynamic multi-attribute task dispatcher</b>. "
        "Unlike black-box heuristics or rigid rotational algorithms, the system operates on a continuous feedback loop: "
        "(1) task arrival registers baseline attributes in a virtual Process Control Block; "
        "(2) at each quantum expiration, a bounded accumulator calculates waiting latency since last CPU relinquishment; "
        "(3) an exponential decay operator measures recent processor consumption; "
        "(4) a normalized composite scoring equation projects competing requirements onto a common decision plane; and "
        "(5) a deterministic tie-breaker ensures reproducible scheduling order."
    ))
    
    pat_data = [
        [Paragraph("Patent Record", tbl_header), Paragraph("Jurisdiction & Title", tbl_header), Paragraph("Existing Prior Art Disclosure", tbl_header), Paragraph("Technical Distinction of AFAS", tbl_header), Paragraph("Novelty Implication", tbl_header)],
        [
            Paragraph("GB2304211A / GB2304211B", tbl_cell_bold),
            Paragraph("UK (Expired)<br/>User-level process-scheduler", tbl_cell),
            Paragraph("User-level scheduler that adjusts process priorities dynamically to control execution.", tbl_cell),
            Paragraph("AFAS implements an auditable multi-attribute score combining bounded aging with decayed share penalty.", tbl_cell),
            Paragraph("User-level scheduling and dynamic priority are established; cannot claim broad novelty.", tbl_cell)
        ],
        [
            Paragraph("US6668269B1", tbl_cell_bold),
            Paragraph("US (Expired)<br/>Process scheduler with changeable priorities", tbl_cell),
            Paragraph("Operating system task scheduler calculating dynamic execution priorities.", tbl_cell),
            Paragraph("AFAS incorporates a hard ceiling on aging boost (50 units) and decoupled audit logging.", tbl_cell),
            Paragraph("Limits broad claims on priority modulation; novelty restricted to specific bounding functions.", tbl_cell)
        ],
        [
            Paragraph("US8881161B1", tbl_cell_bold),
            Paragraph("US (Active)<br/>Hardware task manager CPU offload", tbl_cell),
            Paragraph("Hardware-accelerated queue manager offloading scheduling decisions from CPU.", tbl_cell),
            Paragraph("AFAS is a pure software discrete-event simulator without hardware offload coprocessors.", tbl_cell),
            Paragraph("Distinct architectural tier; hardware claims do not read on AFAS software.", tbl_cell)
        ],
        [
            Paragraph("US8434086B2", tbl_cell_bold),
            Paragraph("US (Active)<br/>Adaptive partitioning of process threads", tbl_cell),
            Paragraph("Guarantees CPU time reservations across partitions with adaptive budget borrowing.", tbl_cell),
            Paragraph("AFAS evaluates an explainable per-task score rather than reserving partition budgets.", tbl_cell),
            Paragraph("Different scheduling paradigm; AFAS avoids real-time budget guarantee claims.", tbl_cell)
        ]
    ]
    t_pat = Table(pat_data, colWidths=[80, 85, 120, 120, 110])
    t_pat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f2b5c')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(TableBlock(t_pat, "Table 12: Prior-art claim mapping against relevant granted patents."))

    story.append(H2("12.2 Status of Patent-Hypothesis Evidence Checklist"))
    pat_check_data = [
        [Paragraph("Evidence Requirement (Review 1 Section 18.1)", tbl_header), Paragraph("Status Post-Review 2", tbl_header), Paragraph("Empirical Finding / Current Posture", tbl_header)],
        [Paragraph("1. Exact algorithm & tie-breaking rules", tbl_cell_bold), Paragraph("Completed", tbl_cell), Paragraph("Documented in Section 2 & 3; verified through 12 passing unit tests.", tbl_cell)],
        [Paragraph("2. Reproducible experimental data against baselines", tbl_cell_bold), Paragraph("Completed", tbl_cell), Paragraph("200 runs across 5 workloads x 5 seeds; results exported to results_all_runs.csv.", tbl_cell)],
        [Paragraph("3. Measurable improvement without unacceptable regressions", tbl_cell_bold), Paragraph("Partial (Weakened)", tbl_cell_bold), Paragraph("Aging provides 59% max wait reduction, but share penalty is ineffective. Round Robin still wins on tail wait and Jain index.", tbl_cell)],
        [Paragraph("4. Detailed claim chart against prior-art patents", tbl_cell_bold), Paragraph("In Progress", tbl_cell), Paragraph("Prior art mapped in Table 12; formal claim charting deferred until share term is redesigned.", tbl_cell)],
        [Paragraph("5. Official Indian Patent Register search (InPASS)", tbl_cell_bold), Paragraph("Pending", tbl_cell), Paragraph("Requires searching official Indian and WIPO PATENTSCOPE registers before any filing.", tbl_cell)]
    ]
    t_pat_chk = Table(pat_check_data, colWidths=[140, 75, 300])
    t_pat_chk.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f2b5c')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(TableBlock(t_pat_chk, "Table 13: Updated patent evidence checklist reflecting empirical reality."))
    story.append(PageBreak())

    # ================= PAGE 13: THREATS, PLAN, CONCLUSION & REFERENCES =================
    story.append(H1("13. Threats to Validity and Updated Limitations"))
    threat_data = [
        [Paragraph("Threat / Limitation", tbl_header), Paragraph("Nature of Threat", tbl_header), Paragraph("Observed Impact on Study", tbl_header), Paragraph("Mitigation Implemented / Planned", tbl_header)],
        [Paragraph("Synthetic Workloads", tbl_cell_bold), Paragraph("External Validity", tbl_cell), Paragraph("Synthetic arrival processes may not capture real production server traffic patterns.", tbl_cell), Paragraph("Defined 5 distinct structural workloads covering varied load factors; adding public trace in Review 3.", tbl_cell)],
        [Paragraph("Five Random Seeds", tbl_cell_bold), Paragraph("Statistical Validity", tbl_cell), Paragraph("Small seed count limits confidence intervals for differences smaller than 2%.", tbl_cell), Paragraph("Conducted paired win counts (Table 7); expanding to 30 seeds with bootstrap intervals in Review 3.", tbl_cell)],
        [Paragraph("Fixed Starvation Threshold", tbl_cell_bold), Paragraph("Construct Validity", tbl_cell), Paragraph("Fixed threshold of 40 units flags long jobs prematurely in heavy queues.", tbl_cell), Paragraph("Evaluated warnings alongside Maximum Ready-Queue Wait Gap to provide dual-perspective analysis.", tbl_cell)],
        [Paragraph("Single-Core Model", tbl_cell_bold), Paragraph("Ecological Validity", tbl_cell), Paragraph("Omits multicore load balancing, cache locality, and processor affinity.", tbl_cell), Paragraph("Documented explicitly as single-CPU scope; multicore model designated as future research.", tbl_cell)]
    ]
    t_threat = Table(threat_data, colWidths=[90, 80, 165, 180])
    t_threat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f2b5c')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(TableBlock(t_threat, "Table 14: Threats to validity, limitations, and planned mitigations."))

    story.append(H1("14. Plan for Review 3 / Final Submission"))
    plan_data = [
        [Paragraph("Item / Work Package", tbl_header), Paragraph("Target Objective for Review 3 / Final Evaluation", tbl_header)],
        [Paragraph("Redesign Share Penalty Term", tbl_cell_bold), Paragraph("Reformulate C_i(t) relative to weighted fair share rather than absolute service decay; retain only if ablation confirms gains.", tbl_cell)],
        [Paragraph("Expanded Statistical Rigor", tbl_cell_bold), Paragraph("Scale experiments from 5 to 30 seeds per workload; report 95% bootstrap confidence intervals and p-value significance tests.", tbl_cell)],
        [Paragraph("Workload Realism & I/O Bursts", tbl_cell_bold), Paragraph("Incorporate multi-phase CPU-I/O blocking workloads and inject burst-estimation errors for SJF/SRTF evaluation.", tbl_cell)],
        [Paragraph("Interactive Browser GUI", tbl_cell_bold), Paragraph("Deliver a web-based dashboard for interactive process entry, live Gantt timeline playback, and CSV export.", tbl_cell)],
        [Paragraph("Optimized Dispatch Queue", tbl_cell_bold), Paragraph("Implement a bucketed priority queue with lazy score invalidation to eliminate O(N^2) decision overhead.", tbl_cell)],
        [Paragraph("Official Patent Register Search", tbl_cell_bold), Paragraph("Conduct comprehensive patent searches in InPASS (India), WIPO PATENTSCOPE, and Espacenet before final defense.", tbl_cell)]
    ]
    t_plan = Table(plan_data, colWidths=[130, 385])
    t_plan.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f2b5c')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(TableBlock(t_plan, "Table 15: Planned work packages and deliverables for Review 3."))

    story.append(H1("15. Conclusion"))
    concl_text = (
        "Review 2 successfully demonstrates that the Adaptive Fairness-Aware CPU Scheduling Simulator is a fully functional, "
        "rigorously verified software prototype rather than an abstract concept. "
        "The simulator reliably executes five standard operating system policies alongside the proposed AFAS mechanism across 25 workload instances. "
        "Our empirical evaluation yields clear, honest conclusions: AFAS achieves a <b>59% reduction in maximum wait gap</b> and lowers p95 response time "
        "from 158.7 to 52.5 compared to static Priority scheduling, while delivering average latency competitive with Round Robin. "
        "However, AFAS does not dominate all baselines: Round Robin provides superior tail bounding and higher Jain fairness, "
        "while SRTF delivers lower average waiting time at the expense of severe starvation. "
        "Furthermore, our ablation study produced an essential negative finding: the waiting-age boost drives virtually all tail-latency gains, "
        "whereas the recent-CPU-share penalty showed no measurable effect under current decay parameters. "
        "These transparent findings position AFAS as an effective, inspectable trade-off policy. "
        "Review 3 will refine the mathematical model, expand statistical testing to 30 seeds, and deliver the final user-facing interface."
    )
    story.append(P(concl_text))

    story.append(H1("16. Updated References (Common Item 12)"))
    refs_all = [
        "[1] T. E. Anderson et al., 'Scheduler Activations: Effective Kernel Support for User-Level Parallelism,' <i>ACM TOCS</i>, 10(1):53–79, 1992.",
        "[2] C. A. Waldspurger & W. E. Weihl, 'Lottery Scheduling: Flexible Proportional-Share Resource Management,' in <i>USENIX OSDI</i>, 1994.",
        "[3] C. A. Waldspurger & W. E. Weihl, 'Stride Scheduling: Deterministic Proportional-Share Management,' MIT/LCS/TM-528, 1995.",
        "[4] G. Banga, P. Druschel, & J. C. Mogul, 'Resource Containers: A New Facility for Resource Management,' in <i>OSDI</i>, pp. 45–58, 1999.",
        "[5] B. Gamsa et al., 'Tornado: Maximizing Locality and Concurrency in a Shared Memory OS,' in <i>OSDI</i>, pp. 87–100, 1999.",
        "[6] C. S. Wong et al., 'Towards Achieving Fairness in the Linux Scheduler,' <i>ACM SIGOPS OSR</i>, 42(5):34–43, 2008.",
        "[7] C. S. Wong et al., 'Fairness & Interactive Performance of O(1) and CFS Schedulers,' in <i>IEEE ITSim</i>, 2008.",
        "[8] T. Li et al., 'OS Scheduling for Asymmetric Multi-Core Architectures (AMPS),' in <i>ACM/IEEE SC</i>, 2007.",
        "[9] J. Lelli et al., 'Deadline Scheduling in the Linux Kernel,' <i>Software: Practice & Experience</i>, 46(6):821–839, 2016.",
        "[10] E. Asyabi et al., 'CTS: CPU Scheduler to Mitigate Tail Latency,' <i>J. Parallel & Distributed Computing</i>, 131:156–169, 2019.",
        "[11] K. Patil, N. Dhotre, & B. Shankar, 'Fairness and Performance Analysis of CFS,' <i>IJCTA</i>, 9(15):7183–7190, 2016.",
        "[12] K. E. Jbara, 'Visual Tool to Improve Teaching of CPU Scheduling Algorithms,' in <i>IEEE AEECT</i>, 2017.",
        "[13] S. Imai & T. Takeichi, 'Development of Adobe Flash Based CPU Scheduling Simulator,' in <i>IEEE INCoS</i>, 2015.",
        "[14] M. A. Putri, 'Aplikasi Simulasi Algoritma Penjadwalan Sistem Operasi,' <i>Jurnal Teknologi Informasi</i>, 5(1):45–52, 2021.",
        "[15] M. Yoon et al., 'Worst Case Response Time Analysis for CFS in Linux Systems,' <i>Real-Time Systems</i>, 61(1):112–138, 2025.",
        "[16] R. Jain, D. Chiu, & W. Hawe, 'A Quantitative Measure of Fairness for Resource Allocation,' DEC TR-301, 1984.",
        "[17] A. Silberschatz, P. B. Galvin, & G. Gagne, <i>Operating System Concepts</i>, 10th ed., Wiley, 2018.",
        "[P1] Fujitsu Ltd., 'User-level process-scheduler,' UK Patent GB2304211A/B, 1997. &nbsp;&nbsp; [P2] Fujitsu Ltd., US6668269B1, 2003.",
        "[P3] Ampere Computing, 'Hardware-enabled task manager,' US8881161B1, 2014. &nbsp;&nbsp; [P4] Dell Products LP, US12277439B2, 2025.",
        "[P5] BlackBerry QNX, 'Process scheduler employing adaptive partitioning,' US Patent US8434086B2, 2013."
    ]
    for r in refs_all: story.append(P(r))
    story.append(PageBreak())

    # ================= PAGE 14: APPENDIX A (W1-W4) =================
    story.append(H1("Appendix A: Comprehensive Per-Workload Benchmark Tables"))
    story.append(P("The following tables report the exact empirical metrics for each workload family, averaged across all five pseudo-random seeds:"))
    
    def make_per_workload_table(title, rows):
        t_data = [[
            Paragraph("Policy", tbl_header), Paragraph("Avg WT", tbl_header), Paragraph("Avg RT", tbl_header),
            Paragraph("Med RT", tbl_header), Paragraph("p95 RT", tbl_header), Paragraph("Max Wait", tbl_header),
            Paragraph("Ctx Sw.", tbl_header), Paragraph("Util.", tbl_header), Paragraph("Jain", tbl_header),
            Paragraph("Warn.", tbl_header)
        ]]
        for r in rows:
            t_data.append([
                Paragraph(r[0], tbl_cell_bold if "AFAS" in r[0] else tbl_cell),
                Paragraph(str(r[1]), tbl_cell), Paragraph(str(r[2]), tbl_cell), Paragraph(str(r[3]), tbl_cell),
                Paragraph(str(r[4]), tbl_cell), Paragraph(str(r[5]), tbl_cell), Paragraph(str(r[6]), tbl_cell),
                Paragraph(str(r[7]), tbl_cell), Paragraph(str(r[8]), tbl_cell), Paragraph(str(r[9]), tbl_cell)
            ])
        t_obj = Table(t_data, colWidths=[85, 45, 45, 45, 45, 50, 45, 40, 40, 45])
        t_obj.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f2b5c')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 1.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
        ]))
        return KeepTogether([H2(title), t_obj, Spacer(1, 3)])

    w1_rows = [
        ["FCFS", "0.2", "0.2", "0.0", "1.0", "1.2", "19.0", "0.89", "1.00", "0.0"],
        ["SJF", "0.2", "0.2", "0.0", "1.0", "1.2", "19.0", "0.89", "1.00", "0.0"],
        ["SRTF", "0.2", "0.2", "0.0", "1.0", "1.2", "19.0", "0.89", "1.00", "0.0"],
        ["RR (q=4)", "0.5", "0.1", "0.0", "0.8", "2.0", "21.8", "0.89", "0.99", "0.0"],
        ["Priority", "0.2", "0.2", "0.0", "1.0", "1.2", "19.0", "0.89", "1.00", "0.0"],
        ["AFAS (q=4)", "0.5", "0.2", "0.0", "0.8", "4.2", "19.6", "0.89", "0.99", "0.0"],
        ["AFAS no-aging", "0.6", "0.2", "0.0", "0.8", "7.2", "19.6", "0.89", "0.99", "0.0"],
        ["AFAS no-share", "0.5", "0.2", "0.0", "0.8", "4.2", "19.8", "0.89", "0.99", "0.0"]
    ]
    story.append(make_per_workload_table("Workload W1: Uniform Batch (Offered Load: 0.89)", w1_rows))

    w2_rows = [
        ["FCFS", "93.9", "93.9", "97.7", "185.4", "195.6", "19.0", "0.99", "0.40", "13.0"],
        ["SJF", "46.2", "46.2", "25.1", "152.0", "195.0", "19.0", "0.99", "0.59", "6.6"],
        ["SRTF", "36.5", "33.2", "2.4", "144.8", "195.0", "22.6", "0.99", "0.78", "5.2"],
        ["RR (q=4)", "77.8", "18.8", "18.6", "40.0", "42.6", "72.6", "0.99", "0.52", "4.6"],
        ["Priority", "105.3", "105.3", "108.0", "205.4", "230.4", "19.0", "0.99", "0.38", "14.0"],
        ["AFAS (q=4)", "70.1", "17.4", "13.5", "40.6", "66.6", "69.4", "0.99", "0.55", "4.2"],
        ["AFAS no-aging", "66.2", "45.4", "14.9", "150.4", "187.6", "60.2", "0.99", "0.57", "7.2"],
        ["AFAS no-share", "70.5", "18.3", "13.7", "41.2", "65.0", "69.2", "0.99", "0.55", "5.2"]
    ]
    story.append(make_per_workload_table("Workload W2: Mixed Bursts (Offered Load: 4.70)", w2_rows))

    w3_rows = [
        ["FCFS", "83.2", "83.2", "95.9", "115.2", "118.0", "23.0", "1.00", "0.35", "20.4"],
        ["SJF", "49.1", "49.1", "16.9", "173.0", "188.4", "23.0", "1.00", "0.63", "7.8"],
        ["SRTF", "47.3", "44.4", "8.7", "173.0", "188.4", "23.8", "1.00", "0.67", "7.6"],
        ["RR (q=4)", "118.1", "38.7", "42.0", "68.8", "74.4", "61.4", "1.00", "0.88", "39.4"],
        ["Priority", "52.8", "52.8", "15.4", "178.6", "191.6", "23.0", "1.00", "0.60", "8.8"],
        ["AFAS (q=4)", "65.5", "36.2", "14.9", "138.8", "144.4", "59.8", "1.00", "0.60", "6.6"],
        ["AFAS no-aging", "62.2", "39.4", "3.9", "160.6", "174.8", "55.0", "1.00", "0.56", "10.0"],
        ["AFAS no-share", "65.0", "37.4", "15.7", "142.0", "145.2", "59.4", "1.00", "0.59", "6.8"]
    ]
    story.append(make_per_workload_table("Workload W3: Priority Skew (Offered Load: 2.50)", w3_rows))

    w4_rows = [
        ["FCFS", "51.0", "51.0", "50.6", "94.0", "102.6", "20.0", "1.00", "0.51", "12.8"],
        ["SJF", "39.4", "39.4", "24.8", "123.4", "159.4", "20.0", "1.00", "0.69", "5.8"],
        ["SRTF", "39.0", "37.7", "23.4", "123.4", "159.4", "21.8", "1.00", "0.67", "5.8"],
        ["RR (q=4)", "75.6", "25.0", "26.2", "45.4", "50.8", "55.4", "1.00", "0.71", "11.2"],
        ["Priority", "53.6", "53.6", "31.4", "167.8", "176.8", "20.0", "1.00", "0.56", "8.2"],
        ["AFAS (q=4)", "76.7", "27.1", "25.0", "57.4", "98.6", "54.6", "1.00", "0.59", "12.0"],
        ["AFAS no-aging", "60.8", "46.3", "30.8", "154.4", "183.2", "38.8", "1.00", "0.52", "8.8"],
        ["AFAS no-share", "75.5", "27.8", "26.2", "58.6", "97.4", "54.2", "1.00", "0.57", "11.2"]
    ]
    story.append(make_per_workload_table("Workload W4: Burst Arrivals (Offered Load: 2.40)", w4_rows))
    story.append(PageBreak())

    # ================= PAGE 15: APPENDIX A (W5) & APPENDIX B =================
    w5_rows = [
        ["FCFS", "167.5", "167.5", "184.2", "216.8", "216.8", "14.0", "1.00", "0.22", "13.8"],
        ["SJF", "49.9", "49.9", "39.0", "188.8", "188.8", "14.0", "1.00", "0.50", "6.4"],
        ["SRTF", "24.0", "17.3", "0.0", "173.4", "188.6", "21.2", "1.00", "0.89", "2.0"],
        ["RR (q=4)", "56.1", "13.9", "14.8", "25.4", "26.4", "72.8", "1.00", "0.79", "0.0"],
        ["Priority", "169.7", "169.7", "186.8", "240.8", "240.8", "14.0", "1.00", "0.22", "13.8"],
        ["AFAS (q=4)", "48.6", "10.0", "9.2", "24.8", "27.0", "70.0", "1.00", "0.74", "0.0"],
        ["AFAS no-aging", "42.3", "16.9", "1.8", "111.4", "140.2", "55.6", "1.00", "0.72", "3.2"],
        ["AFAS no-share", "51.4", "12.3", "11.8", "25.4", "26.6", "69.0", "1.00", "0.74", "0.0"]
    ]
    story.append(make_per_workload_table("Workload W5: Share Imbalance (Offered Load: 3.00)", w5_rows))
    story.append(Spacer(1, 4))

    story.append(H1("Appendix B: How to Reproduce"))
    story.append(P("The entire experimental benchmark is fully reproducible with fixed random seeds (1 to 5). Commands:"))
    repo_box = """
    # 1. Clone repository and install dependencies
    git clone https://github.com/alokmaan/afas-simulator.git && cd afas-simulator
    pip install -r requirements.txt   # Requires python 3.10+, numpy, matplotlib, pytest, reportlab

    # 2. Run automated verification test suite (12 tests)
    pytest -v test_sim.py

    # 3. Execute all 200 simulation runs across 5 workloads and 5 seeds
    python3 experiments.py            # Generates results_all_runs.csv and results.json

    # 4. Re-compile all 8 high-resolution publication figures
    python3 charts.py                 # Generates fig_1 through fig_8 in ./figures/

    # 5. Build this comprehensive Review 2 PDF report
    python3 generate_review2_pdf.py   # Compiles complete PDF document
    """
    story.append(Table([[Paragraph(repo_box, code_block_style)]], colWidths=[515], style=[
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#94a3b8')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4)
    ]))

    doc.build(story, canvasmaker=ReviewCanvas)
    print(f"Successfully generated final PDF: {pdf_filename}")

if __name__ == "__main__":
    build_pdf()
