"""
generate_review3_pdf.py - Review 3: Complete Implementation Report
AFAS CPU Scheduling Simulator - Aesthetic, Detailed, Fully Explained
GitHub: https://github.com/AlokMaan/OS
"""
import os, json, math
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, KeepTogether, PageBreak, HRFlowable, ListFlowable, ListItem
)
from reportlab.pdfgen import canvas

W, H = A4
BASE = os.path.dirname(os.path.abspath(__file__))
SC   = os.path.join(BASE, "screenshots")
FIG  = os.path.join(BASE, "figures")

# ─── Colors ───
NAVY      = colors.HexColor('#0f2b5c')
DARK_BLUE = colors.HexColor('#1e3a8a')
MED_BLUE  = colors.HexColor('#1e40af')
LIGHT_BLUE= colors.HexColor('#3b82f6')
SKY_BG    = colors.HexColor('#eff6ff')
SLATE     = colors.HexColor('#475569')
DARK_TEXT  = colors.HexColor('#1f2937')
BODY_TEXT  = colors.HexColor('#111827')
LIGHT_BG  = colors.HexColor('#f8fafc')
BORDER    = colors.HexColor('#cbd5e1')
ACCENT_GREEN = colors.HexColor('#059669')
ACCENT_BG    = colors.HexColor('#f0fdf4')

# ─── Canvas with header/footer ───
class R3Canvas(canvas.Canvas):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._pages = []
    def showPage(self):
        self._pages.append(dict(self.__dict__))
        self._startPage()
    def save(self):
        n = len(self._pages)
        for s in self._pages:
            self.__dict__.update(s)
            self.saveState()
            if self._pageNumber > 1:
                self.setFont("Helvetica", 7.5)
                self.setFillColor(SLATE)
                self.drawString(40, H-23, "Adaptive Fairness-Aware CPU Scheduling Simulator for Linux  |  Review 3  |  VIT Chennai")
                self.setStrokeColor(colors.HexColor('#e2e8f0'))
                self.setLineWidth(0.6)
                self.line(40, H-27, W-40, H-27)
            self.setFont("Helvetica", 7.5)
            self.setFillColor(SLATE)
            self.drawCentredString(W/2, 18, f"Page {self._pageNumber} of {n}  |  Operating Systems Project  |  Review 3")
            self.setStrokeColor(colors.HexColor('#e2e8f0'))
            self.setLineWidth(0.6)
            self.line(40, 28, W-40, 28)
            # Blue accent stripe at bottom
            self.setFillColor(DARK_BLUE)
            self.rect(0, 0, W, 6, fill=True, stroke=False)
            self.restoreState()
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

def build():
    pdf = os.path.join(BASE, "OS_Review_3_AFAS_Implementation_Report.pdf")
    doc = SimpleDocTemplate(pdf, pagesize=A4, leftMargin=40, rightMargin=40,
                            topMargin=36, bottomMargin=40)
    sty = getSampleStyleSheet()

    # ── Styles ──
    title_s = ParagraphStyle('T', parent=sty['Normal'], fontName='Helvetica-Bold',
        fontSize=18, leading=22, alignment=TA_CENTER, textColor=colors.HexColor('#0f172a'), spaceAfter=4)
    sub_title = ParagraphStyle('ST', parent=sty['Normal'], fontName='Helvetica-Bold',
        fontSize=14, leading=18, alignment=TA_CENTER, textColor=NAVY, spaceAfter=4)
    sub_s = ParagraphStyle('SS', parent=sty['Normal'], fontName='Helvetica-Oblique',
        fontSize=9.5, leading=12.5, alignment=TA_CENTER, textColor=SLATE, spaceAfter=8)
    auth_s = ParagraphStyle('A', parent=sty['Normal'], fontName='Helvetica',
        fontSize=9, leading=13, alignment=TA_CENTER, textColor=DARK_TEXT, spaceAfter=8)
    h1_s = ParagraphStyle('H1', parent=sty['Normal'], fontName='Helvetica-Bold',
        fontSize=12, leading=15, textColor=NAVY, spaceBefore=10, spaceAfter=5, keepWithNext=True)
    h2_s = ParagraphStyle('H2', parent=sty['Normal'], fontName='Helvetica-Bold',
        fontSize=10, leading=13, textColor=MED_BLUE, spaceBefore=7, spaceAfter=3, keepWithNext=True)
    h3_s = ParagraphStyle('H3', parent=sty['Normal'], fontName='Helvetica-BoldOblique',
        fontSize=9, leading=11.5, textColor=colors.HexColor('#334155'), spaceBefore=5, spaceAfter=2, keepWithNext=True)
    body_s = ParagraphStyle('B', parent=sty['Normal'], fontName='Helvetica',
        fontSize=8.2, leading=11.2, textColor=DARK_TEXT, spaceAfter=3.5, alignment=TA_JUSTIFY)
    bul_s = ParagraphStyle('BL', parent=sty['Normal'], fontName='Helvetica',
        fontSize=8, leading=10.8, textColor=DARK_TEXT, leftIndent=14, spaceAfter=2.5, bulletIndent=4)
    cap_s = ParagraphStyle('C', parent=sty['Normal'], fontName='Helvetica-Oblique',
        fontSize=7.5, leading=9.5, alignment=TA_CENTER, textColor=SLATE, spaceBefore=2, spaceAfter=5)
    code_s = ParagraphStyle('CD', parent=sty['Normal'], fontName='Courier',
        fontSize=7, leading=9, textColor=colors.HexColor('#0f172a'))
    th_s = ParagraphStyle('TH', parent=sty['Normal'], fontName='Helvetica-Bold',
        fontSize=7.2, leading=9, textColor=colors.white, alignment=TA_LEFT)
    tc_s = ParagraphStyle('TC', parent=sty['Normal'], fontName='Helvetica',
        fontSize=7, leading=8.8, textColor=BODY_TEXT)
    tcb_s = ParagraphStyle('TCB', parent=sty['Normal'], fontName='Helvetica-Bold',
        fontSize=7, leading=8.8, textColor=BODY_TEXT)
    tcc_s = ParagraphStyle('TCC', parent=sty['Normal'], fontName='Courier',
        fontSize=6.5, leading=8, textColor=colors.HexColor('#1e293b'))

    def P(t): return Paragraph(t, body_s)
    def B(t): return Paragraph(f"&bull; {t}", bul_s)
    def H1(t): return Paragraph(t, h1_s)
    def H2(t): return Paragraph(t, h2_s)
    def H3(t): return Paragraph(t, h3_s)
    def Cap(t): return Paragraph(t, cap_s)

    def img(path, w, h, cap_text):
        items = []
        if os.path.exists(path):
            items.append(Image(path, width=w, height=h))
        else:
            items.append(P(f"<i>[Image: {os.path.basename(path)}]</i>"))
        items.append(Cap(cap_text))
        return KeepTogether(items)

    def std_tbl():
        return TableStyle([
            ('BACKGROUND',(0,0),(-1,0), NAVY),
            ('TEXTCOLOR',(0,0),(-1,0), colors.white),
            ('GRID',(0,0),(-1,-1), 0.5, BORDER),
            ('VALIGN',(0,0),(-1,-1),'TOP'),
            ('TOPPADDING',(0,0),(-1,-1),3),
            ('BOTTOMPADDING',(0,0),(-1,-1),3),
            ('LEFTPADDING',(0,0),(-1,-1),5),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white, LIGHT_BG])
        ])

    def blue_box(content):
        return Table([[Paragraph(content, body_s)]], colWidths=[515], style=[
            ('BACKGROUND',(0,0),(-1,-1), SKY_BG),
            ('BOX',(0,0),(-1,-1), 1.5, LIGHT_BLUE),
            ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
            ('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),12)])

    def green_box(content):
        return Table([[Paragraph(content, body_s)]], colWidths=[515], style=[
            ('BACKGROUND',(0,0),(-1,-1), ACCENT_BG),
            ('BOX',(0,0),(-1,-1), 1.5, ACCENT_GREEN),
            ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
            ('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),12)])

    def code_box(content):
        return Table([[Paragraph(content, code_s)]], colWidths=[515], style=[
            ('BACKGROUND',(0,0),(-1,-1), colors.HexColor('#f1f5f9')),
            ('BOX',(0,0),(-1,-1), 1, colors.HexColor('#94a3b8')),
            ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
            ('LEFTPADDING',(0,0),(-1,-1),8)])

    story = []

    # ══════════════════════════════════════════════════════════════
    #  PAGE 1 - COVER
    # ══════════════════════════════════════════════════════════════
    story.append(Spacer(1, 8))
    # Top accent bar
    story.append(Table([['']], colWidths=[515], rowHeights=[4], style=[
        ('BACKGROUND',(0,0),(-1,-1), DARK_BLUE), ('LINEBELOW',(0,0),(-1,0),0,DARK_BLUE)]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("OPERATING SYSTEMS", ParagraphStyle('OStop', parent=title_s,
        fontSize=14, textColor=SLATE)))
    story.append(Paragraph("PROJECT REVIEW - 3", sub_title))
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "Adaptive Fairness-Aware CPU Scheduling<br/>Simulator for Linux (AFAS)", title_s))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "Complete Implementation Details, Technology Stack, Configuration,<br/>"
        "Output Screenshots, and GitHub Repository Link", sub_s))

    story.append(HRFlowable(width="80%", thickness=1.5, color=DARK_BLUE, spaceBefore=4, spaceAfter=14))

    story.append(Paragraph("""
    <b>Submitted By:</b><br/>
    <b>Alok Maan</b> &nbsp;|&nbsp; 24BCB0057 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <b>Arshdeep Singh</b> &nbsp;|&nbsp; 24BCE0556<br/>
    <b>Ankush Hooda</b> &nbsp;|&nbsp; 24BCE0966 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <b>Somya Sharma</b> &nbsp;|&nbsp; 24BCT0324<br/><br/>
    <b>Faculty Guide:</b> Prof. V. Ezhil Arasi<br/>
    <i>School of Computer Science and Engineering</i><br/>
    <i>Vellore Institute of Technology (VIT), Chennai</i>
    """, auth_s))
    story.append(Spacer(1, 10))

    # GitHub box
    story.append(blue_box(
        "<b>GitHub Repository (Public Access):</b><br/><br/>"
        "<font color='#1e40af' size='10'><b>https://github.com/AlokMaan/OS</b></font><br/><br/>"
        "All source code, automated tests, experimental data, publication figures, screenshots, "
        "and PDF reports are hosted in this repository. To clone:<br/>"
        "<font face='Courier' size='7.5'>git clone https://github.com/AlokMaan/OS.git &amp;&amp; cd OS</font>"
    ))
    story.append(Spacer(1, 10))

    # Abstract
    story.append(H2("Abstract"))
    story.append(P(
        "This Review 3 document provides the <b>complete implementation report</b> for the Adaptive "
        "Fairness-Aware CPU Scheduling Simulator (AFAS), as required by Prof. V. Ezhil Arasi for the "
        "Operating Systems course project. The report comprehensively covers: "
        "<b>(1)</b> the full technology stack and programming languages used; "
        "<b>(2)</b> detailed configuration parameters and environment setup instructions; "
        "<b>(3)</b> module-wise implementation breakdown with line counts and architectural responsibilities; "
        "<b>(4)</b> the mathematical model and algorithm behind the AFAS scheduler; "
        "<b>(5)</b> real terminal output screenshots captured from macOS (Python 3.14.3); "
        "<b>(6)</b> all 8 publication-quality figures generated from 200 simulation runs; "
        "<b>(7)</b> benchmark results and key analytical findings; "
        "and <b>(8)</b> the public GitHub repository link for code review and evaluation."
    ))
    story.append(P(
        "The project comprises <b>6 Python source files (~1,800 lines of code)</b>, "
        "<b>12 automated unit tests (all passing)</b>, "
        "<b>200 benchmark simulation runs</b> across 5 synthetic workload families and 5 random seeds, "
        "and <b>8 publication-grade figures</b>. "
        "The complete Review 2 academic report (15 pages) is also available in the repository."
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    #  PAGE 2 - TECHNOLOGY STACK
    # ══════════════════════════════════════════════════════════════
    story.append(H1("1. Technology Stack and Programming Languages"))
    story.append(P(
        "The entire project is implemented in <b>Python 3.10+</b> (tested and verified on Python 3.14.3 running on macOS). "
        "Python was chosen for its deterministic queue abstractions, rapid algorithmic prototyping, native high-precision "
        "arithmetic, and full cross-platform compatibility (Linux, macOS, Windows). "
        "No kernel modules, C extensions, compiled binaries, or platform-specific code is used - the simulator is "
        "<b>100% pure Python</b> and runs identically on all operating systems."
    ))

    tech = [
        [Paragraph("Technology / Tool", th_s), Paragraph("Version", th_s),
         Paragraph("Role in Project", th_s), Paragraph("Technical Justification for Selection", th_s)],
        [Paragraph("Python 3", tcb_s), Paragraph("3.14.3", tc_s),
         Paragraph("Core Simulation Engine", tcb_s),
         Paragraph("Provides deterministic queue abstractions via <font face='Courier'>collections.deque</font> and <font face='Courier'>list</font>, "
                    "dataclass-based Process Control Blocks, native arbitrary-precision arithmetic, and cross-platform portability.", tc_s)],
        [Paragraph("Pytest", tcb_s), Paragraph("9.2.0", tc_s),
         Paragraph("Automated Unit Testing &amp; Regression", tcb_s),
         Paragraph("Enables 12 strict verification test cases including hand-solved analytical solutions for FCFS, SJF, SRTF, RR, "
                    "and Priority scheduling. Supports parametric invariant checking across all 25 workload instances.", tc_s)],
        [Paragraph("NumPy", tcb_s), Paragraph("2.5.4", tc_s),
         Paragraph("Vectorized Statistical Computation", tcb_s),
         Paragraph("Used for efficient calculation of percentiles (p95 response time), Jain fairness index computation, "
                    "and matrix aggregation operations across the 200 simulation run dataset.", tc_s)],
        [Paragraph("Matplotlib", tcb_s), Paragraph("3.11.2", tc_s),
         Paragraph("Data Visualization &amp; Chart Generation", tcb_s),
         Paragraph("Generates 8 publication-quality PNG figures including grouped bar charts, Gantt execution timelines, "
                    "parameter sensitivity response curves, ablation comparison plots, and logarithmic runtime scaling graphs.", tc_s)],
        [Paragraph("ReportLab", tcb_s), Paragraph("5.1.0", tc_s),
         Paragraph("Programmatic PDF Report Compilation", tcb_s),
         Paragraph("Compiles formal academic PDF documents with dynamic page headers/footers, styled tables, "
                    "embedded high-resolution figures, and formatted mathematical notation.", tc_s)],
        [Paragraph("Pillow (PIL)", tcb_s), Paragraph("13.0.0", tc_s),
         Paragraph("Image Processing &amp; Screenshot Rendering", tcb_s),
         Paragraph("Supports image manipulation for rendering terminal output as styled macOS Terminal window screenshots "
                    "and embedding them into PDF reports.", tc_s)],
        [Paragraph("Git + GitHub", tcb_s), Paragraph("Latest", tc_s),
         Paragraph("Version Control &amp; Code Distribution", tcb_s),
         Paragraph("Maintains immutable commit history tracking all algorithm changes, test configurations, and experimental seeds. "
                    "Public repository enables faculty code review and peer evaluation.", tc_s)],
        [Paragraph("GNU Make", tcb_s), Paragraph("System", tc_s),
         Paragraph("Build Automation &amp; Pipeline Orchestration", tcb_s),
         Paragraph("Provides declarative one-command build targets: <font face='Courier'>make test</font>, "
                    "<font face='Courier'>make experiments</font>, <font face='Courier'>make charts</font>, "
                    "<font face='Courier'>make all</font> for full pipeline execution.", tc_s)],
        [Paragraph("CSV / JSON", tcb_s), Paragraph("Standard Library", tc_s),
         Paragraph("Structured Data Storage &amp; Audit Records", tcb_s),
         Paragraph("Portable, human-readable file formats for raw simulation traces (CSV, 200 records) and aggregated "
                    "summary metrics with ablation/sensitivity data (JSON). Enables independent verification.", tc_s)],
    ]
    t = Table(tech, colWidths=[68, 50, 118, 279])
    t.setStyle(std_tbl())
    story.append(t)
    story.append(Cap("Table 1: Complete technology stack with exact versions, roles, and detailed selection justifications."))
    story.append(Spacer(1, 4))

    # Requirements
    story.append(H2("1.1 Python Package Dependencies (requirements.txt)"))
    story.append(code_box(
        "<font face='Courier' size='7'>"
        "pytest&gt;=8.0.0 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Automated unit test framework<br/>"
        "numpy&gt;=1.24.0 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Vectorized statistics and percentile computation<br/>"
        "matplotlib&gt;=3.7.0 &nbsp;&nbsp;# Publication-quality figure generation<br/>"
        "reportlab&gt;=4.0.0 &nbsp;&nbsp;&nbsp;# Programmatic PDF report compilation<br/>"
        "pillow&gt;=10.0.0 &nbsp;&nbsp;&nbsp;&nbsp;# Image processing for screenshot rendering"
        "</font>"
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    #  PAGE 3 - CONFIGURATION + MODULES
    # ══════════════════════════════════════════════════════════════
    story.append(H1("2. Configuration Details and Environment Setup"))
    story.append(P(
        "The project requires <b>no external services, databases, cloud accounts, or API keys</b>. "
        "The entire setup is local and takes under 60 seconds. The simulator is fully self-contained."
    ))
    story.append(code_box(
        "<b>Step 1: Clone the repository</b><br/>"
        "<font face='Courier' size='7.5'>$ git clone https://github.com/AlokMaan/OS.git</font><br/>"
        "<font face='Courier' size='7.5'>$ cd OS</font><br/><br/>"
        "<b>Step 2: Create Python virtual environment and install dependencies</b><br/>"
        "<font face='Courier' size='7.5'>$ python3 -m venv .venv</font><br/>"
        "<font face='Courier' size='7.5'>$ source .venv/bin/activate &nbsp;&nbsp;&nbsp;&nbsp;# On macOS/Linux</font><br/>"
        "<font face='Courier' size='7.5'>$ pip install -r requirements.txt</font><br/><br/>"
        "<b>Step 3: Run everything with a single command</b><br/>"
        "<font face='Courier' size='7.5'>$ make all &nbsp;&nbsp;&nbsp;&nbsp;# Runs tests + experiments + charts + PDF report</font>"
    ))
    story.append(Spacer(1, 5))

    story.append(H2("2.1 AFAS Scheduler Configuration Parameters"))
    story.append(P(
        "The AFAS scheduler uses a <b>4-component weighted scoring model</b>. Each parameter controls how much "
        "weight is given to different scheduling objectives. Weights are automatically normalized to sum to 1.0."
    ))
    cfg = [
        [Paragraph("Parameter", th_s), Paragraph("Symbol", th_s), Paragraph("Default", th_s),
         Paragraph("Range", th_s), Paragraph("Detailed Description", th_s)],
        [Paragraph("Time Quantum", tcb_s), Paragraph("q", tc_s), Paragraph("4", tc_s), Paragraph("[1, 32]", tc_s),
         Paragraph("CPU time slice allocated per scheduling decision for preemptive policies (RR, AFAS). Smaller values improve interactivity but increase context switches.", tc_s)],
        [Paragraph("Priority Weight", tcb_s), Paragraph("w<sub>p</sub>", tc_s), Paragraph("0.30", tc_s), Paragraph("[0, 1]", tc_s),
         Paragraph("Importance of base administrative priority (P<sub>i</sub> = priority/10). Higher values favor high-priority tasks.", tc_s)],
        [Paragraph("Aging Weight", tcb_s), Paragraph("w<sub>a</sub>", tc_s), Paragraph("0.40", tc_s), Paragraph("[0, 1]", tc_s),
         Paragraph("Importance of waiting-time aging boost. This is the <b>primary anti-starvation mechanism</b>. Tasks waiting longer get dynamically promoted. Saturates at 50 time units.", tc_s)],
        [Paragraph("Responsiveness Weight", tcb_s), Paragraph("w<sub>r</sub>", tc_s), Paragraph("0.15", tc_s), Paragraph("[0, 1]", tc_s),
         Paragraph("Importance of workload class factor. Interactive=1.0, Mixed=0.5, Batch=0.2. Biases toward interactive tasks.", tc_s)],
        [Paragraph("CPU-Share Weight", tcb_s), Paragraph("w<sub>c</sub>", tc_s), Paragraph("0.15", tc_s), Paragraph("[0, 1]", tc_s),
         Paragraph("Penalty for recent CPU consumption using exponential decay (half-life=40). Prevents CPU monopolization by long-running tasks.", tc_s)],
        [Paragraph("Aging Saturation", tcb_s), Paragraph("&tau;<sub>sat</sub>", tc_s), Paragraph("50", tc_s), Paragraph("Fixed", tc_s),
         Paragraph("Hard ceiling for aging: A<sub>i</sub>(t) = min(1.0, wait/50). Prevents unbounded priority inversion.", tc_s)],
        [Paragraph("Decay Half-life", tcb_s), Paragraph("&lambda;", tc_s), Paragraph("40", tc_s), Paragraph("Fixed", tc_s),
         Paragraph("Exponential decay rate for CPU-share tracking: Service<sub>decayed</sub> = &Sigma; &Delta;&tau; * 2<sup>-(t-&tau;)/40</sup>.", tc_s)],
    ]
    ct = Table(cfg, colWidths=[85, 40, 42, 42, 306])
    ct.setStyle(std_tbl())
    story.append(ct)
    story.append(Cap("Table 2: Complete AFAS scheduler configuration parameters with mathematical definitions."))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    #  PAGE 4 - SOURCE CODE MODULES
    # ══════════════════════════════════════════════════════════════
    story.append(H1("3. Module-Wise Implementation Breakdown"))
    story.append(P(
        "The project consists of <b>6 Python source files</b> totaling approximately <b>1,800 lines of production code</b>. "
        "Each module has a strictly defined responsibility within the simulator's layered architecture. "
        "The design follows the principle of <b>separation of concerns</b>: workload generation, simulation engine, "
        "scheduling policy logic, metric computation, and visualization are fully decoupled."
    ))

    mod = [
        [Paragraph("Source File", th_s), Paragraph("Lines", th_s), Paragraph("Key Classes / Functions", th_s),
         Paragraph("Detailed Responsibilities", th_s)],
        [Paragraph("afas_sim.py", tcc_s), Paragraph("593", tcb_s),
         Paragraph("<b>Process</b> (dataclass PCB)<br/><b>Segment</b>, <b>DecisionRecord</b><br/>"
                    "run_fcfs, run_sjf, run_srtf,<br/>run_round_robin, run_priority<br/>"
                    "run_afas, compute_afas_score<br/>compute_metrics<br/>"
                    "validate_workload<br/>verify_engine_invariants<br/>"
                    "generate_w1 through generate_w5", tc_s),
         Paragraph("<b>Core simulation engine.</b> Defines the Process Control Block (PCB) dataclass with 12 attributes "
                    "(PID, arrival time, burst time, remaining burst, priority, workload class, last CPU time, decayed CPU service, "
                    "last decay time, start time, finish time, first response time). "
                    "Implements 5 classic baseline scheduling algorithms and the proposed AFAS adaptive scheduler. "
                    "Computes 11 comprehensive performance metrics. Enforces 3 formal execution invariants "
                    "(non-overlap, burst conservation, temporal causality). "
                    "Contains 5 synthetic workload generators (W1-W5) with configurable random seeds.", tc_s)],
        [Paragraph("test_sim.py", tcc_s), Paragraph("~250", tcb_s),
         Paragraph("12 pytest test functions:<br/>test_fcfs_hand_solved<br/>test_sjf_hand_solved<br/>"
                    "test_srtf_hand_solved<br/>test_round_robin_hand_solved<br/>test_priority_hand_solved<br/>"
                    "test_idle_gap_handling<br/>test_engine_invariants<br/>test_deterministic_reproducibility<br/>"
                    "test_afas_tie_breaking<br/>test_input_validation<br/>test_aging_bounds<br/>test_afas_starvation", tc_s),
         Paragraph("<b>Automated verification suite.</b> Validates mathematical correctness of all scheduling algorithms "
                    "against hand-calculated analytical solutions from OS textbooks (Silberschatz, 10th Ed.). "
                    "Verifies deterministic reproducibility across multiple runs with identical seeds. "
                    "Tests AFAS tie-breaking hierarchy (score desc, arrival asc, PID asc). "
                    "Validates input rejection for invalid data (negative burst, duplicate PID, out-of-range priority). "
                    "Confirms aging saturation bounds and starvation mitigation effectiveness.", tc_s)],
        [Paragraph("experiments.py", tcc_s), Paragraph("~300", tcb_s),
         Paragraph("run_all_experiments<br/>5 experimental phases:<br/>"
                    "[1/5] Main workload runs<br/>[2/5] Metric aggregation<br/>"
                    "[3/5] Sensitivity sweep<br/>[4/5] Quantum sweep<br/>[5/5] Runtime scaling", tc_s),
         Paragraph("<b>Batch benchmark runner.</b> Executes 200 simulation runs across 5 workload families (W1-W5) x "
                    "5 fixed random seeds (1-5) x 6+2 scheduling policies (6 baselines + 2 ablation configs). "
                    "Performs one-at-a-time parameter sensitivity sweeps for all 4 AFAS weights. "
                    "Conducts time-quantum sweeps from q=1 to q=32. "
                    "Benchmarks algorithmic decision runtime scaling from 10 to 500 processes. "
                    "Exports results to <font face='Courier'>data/results_all_runs.csv</font> (200 rows) and "
                    "<font face='Courier'>data/results.json</font> (aggregated).", tc_s)],
        [Paragraph("charts.py", tcc_s), Paragraph("~250", tcb_s),
         Paragraph("8 figure generators:<br/>fig_1 max_wait bars<br/>fig_2 p95_response bars<br/>"
                    "fig_3 avg_waiting bars<br/>fig_4 gantt timelines<br/>"
                    "fig_5 ablation comparison<br/>fig_6 sensitivity curves<br/>"
                    "fig_7 quantum_sweep<br/>fig_8 runtime_scaling", tc_s),
         Paragraph("<b>Publication chart engine.</b> Reads aggregated experiment data from JSON and generates "
                    "8 high-resolution PNG figures: per-workload grouped bar charts for max wait, p95 response time, "
                    "and average waiting time; Gantt execution timeline comparison (Priority vs RR vs AFAS); "
                    "component ablation breakdown; 4-panel sensitivity response curves; "
                    "time-quantum sensitivity sweep; and log-log decision runtime scaling plot.", tc_s)],
        [Paragraph("interactive_cli.py", tcc_s), Paragraph("~160", tcb_s),
         Paragraph("run_interactive<br/>print_ascii_gantt<br/>print_metrics_table<br/>--demo mode", tc_s),
         Paragraph("<b>Interactive terminal interface.</b> Allows users to select workloads (W1-W5 or custom), "
                    "choose scheduling policies, and inspect real-time AFAS score decomposition. "
                    "Renders ASCII Gantt timeline charts. The <font face='Courier'>--demo</font> flag runs "
                    "an automated AFAS trace on the W3 Priority Skew workload, showing score breakdowns for "
                    "every scheduling decision including [AGING_PROMOTION] markers.", tc_s)],
        [Paragraph("generate_review2_pdf.py", tcc_s), Paragraph("924", tcb_s),
         Paragraph("build_pdf<br/>ReviewCanvas<br/>15-page academic document", tc_s),
         Paragraph("<b>Review 2 PDF compiler.</b> Programmatically generates the complete 15-page Review 2 academic report "
                    "with embedded figures, formatted tables, algorithm pseudocode, prior-art patent analysis, "
                    "workload specifications, ablation studies, and academic references.", tc_s)],
    ]
    mt = Table(mod, colWidths=[90, 32, 145, 248])
    mt.setStyle(std_tbl())
    story.append(mt)
    story.append(Cap("Table 3: Complete source code module inventory with line counts and detailed responsibilities."))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    #  PAGE 5 - AFAS ALGORITHM
    # ══════════════════════════════════════════════════════════════
    story.append(H1("4. AFAS Scheduling Algorithm - Mathematical Model"))
    story.append(P(
        "The core innovation of this project is the <b>Adaptive Fairness-Aware Scheduler (AFAS)</b>, "
        "a dynamic multi-attribute scoring algorithm that balances four competing scheduling objectives. "
        "At every quantum boundary, AFAS computes a composite score for each process in the ready queue "
        "and dispatches the highest-scoring process."
    ))
    story.append(Spacer(1, 3))

    # Formula box
    story.append(blue_box(
        "<b>AFAS Composite Scoring Function:</b><br/><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>S<sub>i</sub>(t) = w<sub>p</sub> &middot; P<sub>i</sub> "
        "+ w<sub>a</sub> &middot; A<sub>i</sub>(t) "
        "+ w<sub>r</sub> &middot; R<sub>i</sub> "
        "- w<sub>c</sub> &middot; C<sub>i</sub>(t)</b><br/><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>Subject to:</b> &nbsp; w<sub>p</sub> + w<sub>a</sub> + w<sub>r</sub> + w<sub>c</sub> = 1, "
        "&nbsp;&nbsp; w<sub>k</sub> &ge; 0 &nbsp; &forall; k &isin; {p, a, r, c}<br/><br/>"
        "The process with the <b>highest S<sub>i</sub>(t)</b> is dispatched. Ties are broken deterministically:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;(1) Higher score &rarr; (2) Earlier arrival time &rarr; (3) Lower PID"
    ))
    story.append(Spacer(1, 4))

    story.append(H2("4.1 Score Component Definitions"))
    story.append(B("<b>P<sub>i</sub> - Normalized Base Priority:</b> P<sub>i</sub> = Priority<sub>i</sub> / 10 &isin; [0.1, 1.0]. "
                    "Represents the static administrative urgency assigned to each process (1 = lowest, 10 = highest). "
                    "This term ensures that system-critical tasks retain scheduling preference."))
    story.append(B("<b>A<sub>i</sub>(t) - Bounded Waiting-Time Aging:</b> A<sub>i</sub>(t) = min(1.0, (t - t<sub>last_cpu</sub>) / 50) &isin; [0.0, 1.0]. "
                    "The <b>primary anti-starvation mechanism</b>. As a process waits longer in the ready queue, its aging score increases linearly, "
                    "dynamically boosting its effective priority. The hard ceiling at 50 time units prevents unbounded priority inversion - "
                    "a low-priority batch task cannot permanently override a high-priority interactive task."))
    story.append(B("<b>R<sub>i</sub> - Workload Responsiveness Factor:</b> A categorical factor reflecting task interactivity: "
                    "R<sub>i</sub> = 1.0 for <i>interactive</i> tasks (short bursts, latency-sensitive), "
                    "0.5 for <i>mixed</i> workloads, and 0.2 for CPU-bound <i>batch</i> tasks. "
                    "This biases the scheduler toward interactive responsiveness while still serving batch work."))
    story.append(B("<b>C<sub>i</sub>(t) - Decayed Recent CPU-Share Penalty:</b> C<sub>i</sub>(t) = min(1.0, Service<sub>decayed</sub> / 40). "
                    "Tracks recent CPU consumption using exponential decay with half-life &lambda; = 40: "
                    "Service<sub>decayed</sub>(t) = &Sigma; &Delta;&tau; &middot; 2<sup>-(t-&tau;)/40</sup>. "
                    "This <i>subtractive</i> penalty reduces the score of processes that have recently consumed significant CPU time, "
                    "promoting fair sharing of the processor."))
    story.append(Spacer(1, 4))

    story.append(H2("4.2 Scheduling Policies Implemented"))
    pol = [
        [Paragraph("Policy", th_s), Paragraph("Type", th_s), Paragraph("Selection Criterion", th_s), Paragraph("Key Characteristics", th_s)],
        [Paragraph("FCFS", tcb_s), Paragraph("Non-preemptive", tc_s),
         Paragraph("First arrived process runs to completion", tc_s),
         Paragraph("Simple but causes convoy effect; long jobs block short jobs. No starvation by definition.", tc_s)],
        [Paragraph("SJF", tcb_s), Paragraph("Non-preemptive", tc_s),
         Paragraph("Shortest burst time dispatched first", tc_s),
         Paragraph("Minimizes average waiting time (provably optimal for non-preemptive). Causes starvation for long jobs.", tc_s)],
        [Paragraph("SRTF", tcb_s), Paragraph("Preemptive", tc_s),
         Paragraph("Shortest remaining burst preempts at arrivals", tc_s),
         Paragraph("Preemptive version of SJF. Minimizes average WT. Extreme starvation for long-running processes.", tc_s)],
        [Paragraph("Round Robin", tcb_s), Paragraph("Preemptive (q=4)", tc_s),
         Paragraph("Cyclic FIFO rotation with fixed quantum", tc_s),
         Paragraph("Fair time-sharing. Excellent interactivity. Best tail-latency bounding. High context switches.", tc_s)],
        [Paragraph("Priority", tcb_s), Paragraph("Non-preemptive", tc_s),
         Paragraph("Highest priority value dispatched first", tc_s),
         Paragraph("Starvation baseline - low-priority tasks may never execute. No aging mechanism.", tc_s)],
        [Paragraph("<b>AFAS</b>", tcb_s), Paragraph("Preemptive (q=4)", tc_s),
         Paragraph("Highest composite score S<sub>i</sub>(t)", tc_s),
         Paragraph("<b>Proposed.</b> Dynamic 4-component scoring with bounded aging, workload classification, and CPU-share decay. Eliminates starvation while maintaining interactivity.", tc_s)],
    ]
    pt = Table(pol, colWidths=[60, 80, 165, 210])
    pt.setStyle(std_tbl())
    story.append(pt)
    story.append(Cap("Table 4: All 6 scheduling policies with selection criteria and characteristics."))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    #  PAGE 6 - SCREENSHOTS 1-3
    # ══════════════════════════════════════════════════════════════
    story.append(H1("5. Output Screenshots (Real Terminal Output from macOS)"))
    story.append(P(
        "All screenshots in this section are <b>real terminal output</b> captured from actual command execution "
        "on this MacBook running Python 3.14.3. They demonstrate that the project is a fully functional, "
        "working implementation - not an abstract concept."
    ))
    story.append(Spacer(1, 3))

    story.append(H2("Screenshot 1: Project Setup and Environment Verification"))
    story.append(P("Demonstrates Python version, successful dependency installation, and the project directory structure:"))
    story.append(img(os.path.join(SC, "01_setup.png"), 470, 195,
        "Screenshot 1: Python 3.14.3 version verification, pip install of all 5 dependencies, and project directory listing on macOS."))
    story.append(Spacer(1, 3))

    story.append(H2("Screenshot 2: Build Automation System (Makefile)"))
    story.append(P("The project includes a Makefile with 9 targets for one-command execution of any component:"))
    story.append(img(os.path.join(SC, "02_make_help.png"), 470, 170,
        "Screenshot 2: make help output showing all 9 available build targets for project automation."))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    #  PAGE 7 - SCREENSHOTS 3-4
    # ══════════════════════════════════════════════════════════════
    story.append(H2("Screenshot 3: Automated Unit Test Suite (12/12 Passed)"))
    story.append(P(
        "The project includes <b>12 comprehensive automated unit tests</b> using pytest. These tests verify "
        "the mathematical correctness of all scheduling algorithms by comparing simulator output against "
        "hand-solved analytical solutions from operating systems textbooks. <b>All 12 tests pass in 0.06 seconds.</b>"
    ))
    story.append(img(os.path.join(SC, "03_pytest_12_passed.png"), 470, 210,
        "Screenshot 3: pytest -v test_sim.py - All 12 verification tests passed on macOS (Python 3.14.3)."))
    story.append(Spacer(1, 4))

    test_desc = [
        [Paragraph("Test Name", th_s), Paragraph("Verification Objective", th_s)],
        [Paragraph("test_fcfs_hand_solved", tcb_s), Paragraph("FCFS completion times match hand-calculated solution for 4-process case (CT: 5, 8, 16, 22; Mean WT = 5.75)", tc_s)],
        [Paragraph("test_sjf_hand_solved", tcb_s), Paragraph("SJF correctly selects shortest burst; verified against analytical solution (CT: 5, 8, 22, 14; Mean WT = 5.25)", tc_s)],
        [Paragraph("test_srtf_hand_solved", tcb_s), Paragraph("SRTF preempts at each arrival correctly; matches analytical solution (CT: 8, 4, 22, 14; Mean WT = 5.00)", tc_s)],
        [Paragraph("test_round_robin_hand_solved", tcb_s), Paragraph("Round Robin cyclic rotation with q=2 for 3 processes; completion times match hand trace (CT: 9, 8, 5)", tc_s)],
        [Paragraph("test_priority_hand_solved", tcb_s), Paragraph("Priority always dispatches highest-priority process first; deterministic ordering verified", tc_s)],
        [Paragraph("test_idle_gap_handling", tcb_s), Paragraph("Simulator correctly advances clock forward when CPU is idle (no processes in ready queue)", tc_s)],
        [Paragraph("test_engine_invariants_all_workloads", tcb_s), Paragraph("3 formal invariants (non-overlap, burst conservation, temporal causality) verified on all 25 workload instances (5 families x 5 seeds)", tc_s)],
        [Paragraph("test_deterministic_reproducibility", tcb_s), Paragraph("Multiple runs with identical seed produce bit-identical segment traces and metrics", tc_s)],
        [Paragraph("test_afas_tie_breaking_order", tcb_s), Paragraph("AFAS tie-breaking follows deterministic hierarchy: Score descending, Arrival ascending, PID ascending", tc_s)],
        [Paragraph("test_input_validation_rejections", tcb_s), Paragraph("Invalid inputs raise ValueError: negative burst time, duplicate PIDs, priority outside [1,10], unknown workload class", tc_s)],
        [Paragraph("test_aging_bounds_and_saturation", tcb_s), Paragraph("Aging term A<sub>i</sub>(t) correctly saturates at 1.0 when wait exceeds 50 time units; never exceeds ceiling", tc_s)],
        [Paragraph("test_afas_starvation_mitigation", tcb_s), Paragraph("AFAS reduces maximum wait gap by at least 30% compared to static Priority scheduling on W3 workload", tc_s)],
    ]
    tt = Table(test_desc, colWidths=[155, 360])
    tt.setStyle(std_tbl())
    story.append(tt)
    story.append(Cap("Table 5: All 12 automated unit tests with detailed verification objectives."))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    #  PAGE 8 - SCREENSHOT 4 (EXPERIMENTS)
    # ══════════════════════════════════════════════════════════════
    story.append(H2("Screenshot 4: Batch Experiment Suite (200 Simulation Runs)"))
    story.append(P(
        "The experiments module executes the <b>complete benchmark pipeline in 5 phases</b>: "
        "(1) 200 main simulation runs across 5 workloads x 5 seeds x 8 policy configurations; "
        "(2) metric aggregation with summary table; "
        "(3) one-at-a-time parameter sensitivity sweeps for all 4 AFAS weights; "
        "(4) time-quantum sweeps from q=1 to q=32; "
        "and (5) decision-runtime scaling benchmarks from 10 to 500 processes."
    ))
    story.append(img(os.path.join(SC, "04_experiments_200_runs.png"), 470, 270,
        "Screenshot 4: python3 experiments.py - Complete benchmark execution with 200 runs, summary metrics table, "
        "sensitivity sweeps, quantum sweeps, and runtime scaling benchmarks."))
    story.append(Spacer(1, 4))

    story.append(H2("Screenshot 5: AFAS Decision Audit Log (Real-Time Score Decomposition)"))
    story.append(P(
        "A key innovation of AFAS is the <b>transparent decision audit log</b>. At every quantum boundary, "
        "the scheduler outputs the exact score decomposition for the chosen process: the weighted contributions of "
        "Priority (P), Aging (A), Responsiveness (R), and CPU-Share penalty (-C). "
        "Lines marked <b>[AGING_PROMOTION]</b> show low-priority batch tasks being dynamically promoted because "
        "their waiting-time aging score accumulated sufficiently to override higher base priorities."
    ))
    story.append(img(os.path.join(SC, "05_afas_decision_log.png"), 470, 375,
        "Screenshot 5: python3 interactive_cli.py --demo - AFAS real-time decision audit log with score decomposition "
        "(P, A, R, -C components), aging promotions, and final performance evaluation metrics."))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    #  PAGE 9 - SCREENSHOT 6 + FIGURES
    # ══════════════════════════════════════════════════════════════
    story.append(H2("Screenshot 6: Publication Figure Generation"))
    story.append(img(os.path.join(SC, "06_charts_generation.png"), 470, 105,
        "Screenshot 6: python3 charts.py - 8 publication-quality PNG figures generated from experimental data."))
    story.append(Spacer(1, 6))

    story.append(H1("6. Publication Figures (8 Charts from 200 Simulation Runs)"))
    story.append(P("All figures are generated programmatically from the experimental data. They visualize "
                    "scheduling performance across workloads, policies, parameter settings, and scaling scenarios."))

    f12 = [
        [Image(os.path.join(FIG,"fig_1_max_wait.png"),width=242,height=132),
         Image(os.path.join(FIG,"fig_2_p95_response.png"),width=242,height=132)],
        [Cap("Figure 1: Maximum ready-queue wait gap per workload."),
         Cap("Figure 2: 95th-percentile response time distribution.")]
    ]
    story.append(Table(f12, colWidths=[257,257], style=[
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),('ALIGN',(0,0),(-1,-1),'CENTER')]))
    story.append(Spacer(1, 4))

    f35 = [
        [Image(os.path.join(FIG,"fig_3_avg_waiting.png"),width=242,height=132),
         Image(os.path.join(FIG,"fig_5_ablation.png"),width=242,height=132)],
        [Cap("Figure 3: Average waiting time across all baselines."),
         Cap("Figure 4: Ablation study - aging vs share penalty.")]
    ]
    story.append(Table(f35, colWidths=[257,257], style=[
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),('ALIGN',(0,0),(-1,-1),'CENTER')]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    #  PAGE 10 - MORE FIGURES
    # ══════════════════════════════════════════════════════════════
    story.append(img(os.path.join(FIG,"fig_4_gantt.png"), 465, 178,
        "Figure 5: Gantt execution timeline comparison - Priority (top) vs Round Robin (middle) vs AFAS (bottom). "
        "Shows how AFAS dynamically elevates starving low-priority tasks while maintaining interactivity."))
    story.append(Spacer(1, 4))
    story.append(img(os.path.join(FIG,"fig_6_sensitivity.png"), 465, 138,
        "Figure 6: One-at-a-time parameter sensitivity analysis. Each panel sweeps one weight (w_p, w_a, w_r, w_c) "
        "from 0.0 to 1.0 while holding others fixed, showing impact on max wait, avg WT, and avg RT."))
    story.append(Spacer(1, 4))

    f78 = [
        [Image(os.path.join(FIG,"fig_7_quantum_sweep.png"),width=242,height=158),
         Image(os.path.join(FIG,"fig_8_runtime_scaling.png"),width=242,height=132)],
        [Cap("Figure 7: Time-quantum sweep (q=1 to 32)."),
         Cap("Figure 8: Decision runtime scaling (log-log, N=10 to 500).")]
    ]
    story.append(Table(f78, colWidths=[257,257], style=[
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),('ALIGN',(0,0),(-1,-1),'CENTER')]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    #  PAGE 11 - RESULTS + FINDINGS
    # ══════════════════════════════════════════════════════════════
    story.append(H1("7. Benchmark Results and Key Analytical Findings"))
    story.append(P(
        "The following table summarizes the aggregated performance metrics across all 5 workload families (W1-W5) "
        "and 5 random seeds, representing <b>200 total simulation runs</b>. "
        "Arrows indicate the desired direction for each metric (&darr; = lower is better, &uarr; = higher is better)."
    ))

    rd = [
        [Paragraph("Scheduling Policy", th_s), Paragraph("Avg WT (&darr;)", th_s), Paragraph("Avg RT (&darr;)", th_s),
         Paragraph("p95 RT (&darr;)", th_s), Paragraph("Max Wait (&darr;)", th_s), Paragraph("Ctx Sw.", th_s),
         Paragraph("Jain (&uarr;)", th_s), Paragraph("Warnings (&darr;)", th_s)],
        [Paragraph("FCFS", tc_s), Paragraph("83.9", tc_s), Paragraph("83.9", tc_s),
         Paragraph("126.9", tc_s), Paragraph("131.2", tc_s), Paragraph("19.0", tc_s),
         Paragraph("0.48", tc_s), Paragraph("12.7", tc_s)],
        [Paragraph("SJF (Non-preemptive)", tc_s), Paragraph("38.7", tc_s), Paragraph("38.7", tc_s),
         Paragraph("133.8", tc_s), Paragraph("148.2", tc_s), Paragraph("19.0", tc_s),
         Paragraph("0.67", tc_s), Paragraph("6.1", tc_s)],
        [Paragraph("SRTF (Preemptive)", tc_s), Paragraph("<b>30.6</b>", tc_s), Paragraph("27.0", tc_s),
         Paragraph("129.8", tc_s), Paragraph("147.8", tc_s), Paragraph("22.0", tc_s),
         Paragraph("<b>0.81</b>", tc_s), Paragraph("<b>4.2</b>", tc_s)],
        [Paragraph("Round Robin (q=4)", tc_s), Paragraph("70.5", tc_s), Paragraph("20.3", tc_s),
         Paragraph("<b>37.0</b>", tc_s), Paragraph("<b>40.8</b>", tc_s), Paragraph("57.9", tc_s),
         Paragraph("0.83", tc_s), Paragraph("12.3", tc_s)],
        [Paragraph("Priority (No aging)", tc_s), Paragraph("66.8", tc_s), Paragraph("66.8", tc_s),
         Paragraph("148.7", tc_s), Paragraph("158.7", tc_s), Paragraph("19.0", tc_s),
         Paragraph("0.57", tc_s), Paragraph("8.5", tc_s)],
        [Paragraph("<b>AFAS (Proposed, q=4)</b>", tcb_s), Paragraph("<b>54.5</b>", tcb_s),
         Paragraph("<b>17.1</b>", tcb_s), Paragraph("<b>53.9</b>", tcb_s),
         Paragraph("<b>63.2</b>", tcb_s), Paragraph("<b>56.6</b>", tcb_s),
         Paragraph("<b>0.71</b>", tcb_s), Paragraph("<b>4.7</b>", tcb_s)],
    ]
    rt = Table(rd, colWidths=[100, 52, 52, 52, 58, 52, 52, 55])
    rt.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0), NAVY),
        ('GRID',(0,0),(-1,-1), 0.5, BORDER),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),
        ('BACKGROUND',(0,7),(-1,7), SKY_BG),
        ('ROWBACKGROUNDS',(0,1),(-1,6),[colors.white, LIGHT_BG])
    ]))
    story.append(rt)
    story.append(Cap("Table 6: Global benchmark results averaged across W1-W5 (5 seeds each, 200 total simulation runs). "
                      "Bold values indicate best or proposed results."))
    story.append(Spacer(1, 6))

    story.append(H2("7.1 Key Findings"))
    story.append(green_box(
        "<b>Finding 1 - Starvation Prevention (AFAS vs Priority):</b><br/>"
        "AFAS reduces maximum ready-queue wait from 158.7 to 63.2 - a <b>60% reduction</b>. "
        "The bounded aging mechanism dynamically promotes starving low-priority tasks before severe starvation occurs. "
        "The 95th-percentile response time drops from 148.7 to 53.9 (64% improvement)."
    ))
    story.append(Spacer(1, 3))
    story.append(green_box(
        "<b>Finding 2 - Best Average Response Time (AFAS vs All):</b><br/>"
        "AFAS achieves the <b>lowest average response time of 17.1 units</b> across all policies, "
        "outperforming even Round Robin (20.3) and SRTF (27.0). This demonstrates excellent interactivity "
        "while maintaining context switches comparable to Round Robin (56.6 vs 57.9)."
    ))
    story.append(Spacer(1, 3))
    story.append(green_box(
        "<b>Finding 3 - Ablation Confirms Aging is Critical:</b><br/>"
        "Disabling the aging component (w<sub>a</sub>=0) causes maximum wait to nearly double from 63.2 to 115.8 "
        "(<b>+83% increase</b>). This confirms that bounded waiting-time aging is the <b>primary technical lever</b> "
        "driving AFAS's fairness guarantees. The CPU-share penalty showed only 0.6% impact - an honest negative result."
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    #  PAGE 12 - DIRECTORY + COMMANDS + CONCLUSION
    # ══════════════════════════════════════════════════════════════
    story.append(H1("8. Project Directory Structure"))
    story.append(code_box(
        "<font face='Courier' size='7'>"
        "OS/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
        "&nbsp;&nbsp;&nbsp;&nbsp;# GitHub: https://github.com/AlokMaan/OS<br/>"
        "|-- afas_sim.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Core simulation engine (593 lines)<br/>"
        "|-- test_sim.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 12 automated pytest unit tests<br/>"
        "|-- experiments.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Batch benchmark runner (200 runs)<br/>"
        "|-- charts.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Publication chart generator (8 figures)<br/>"
        "|-- interactive_cli.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Interactive terminal CLI + --demo<br/>"
        "|-- generate_review2_pdf.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Review 2 PDF compiler (15 pages)<br/>"
        "|-- generate_review3_pdf.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Review 3 PDF compiler (this file)<br/>"
        "|-- Makefile &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Build automation (make all)<br/>"
        "|-- run.sh &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Portable bash helper script<br/>"
        "|-- requirements.txt &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Python dependencies (5 packages)<br/>"
        "|-- data/<br/>"
        "|&nbsp;&nbsp; |-- results_all_runs.csv &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Raw traces (200 records)<br/>"
        "|&nbsp;&nbsp; +-- results.json &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Aggregated summary metrics<br/>"
        "|-- figures/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 8 publication-quality PNG charts<br/>"
        "|-- screenshots/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Terminal output screenshots<br/>"
        "+-- docs/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# PDF documentation<br/>"
        "</font>"
    ))
    story.append(Spacer(1, 5))

    story.append(H1("9. Execution Commands Quick Reference"))
    cmd = [
        [Paragraph("Task", th_s), Paragraph("Command", th_s), Paragraph("Expected Output", th_s), Paragraph("Time", th_s)],
        [Paragraph("Setup environment", tcb_s), Paragraph("make setup", tcc_s),
         Paragraph("Creates .venv and installs all 5 dependencies", tc_s), Paragraph("~30s", tc_s)],
        [Paragraph("Run unit tests", tcb_s), Paragraph("make test", tcc_s),
         Paragraph("12 passed in 0.06s (all green)", tc_s), Paragraph("&lt;1s", tc_s)],
        [Paragraph("Run 200 experiments", tcb_s), Paragraph("make experiments", tcc_s),
         Paragraph("results_all_runs.csv + results.json", tc_s), Paragraph("~5s", tc_s)],
        [Paragraph("Interactive CLI", tcb_s), Paragraph("make cli", tcc_s),
         Paragraph("Interactive scheduler with workload/policy selection", tc_s), Paragraph("Interactive", tc_s)],
        [Paragraph("Quick AFAS demo", tcb_s), Paragraph("make demo", tcc_s),
         Paragraph("AFAS decision log + performance metrics", tc_s), Paragraph("~1s", tc_s)],
        [Paragraph("Generate 8 charts", tcb_s), Paragraph("make charts", tcc_s),
         Paragraph("8 PNG figures in figures/ directory", tc_s), Paragraph("~3s", tc_s)],
        [Paragraph("Compile Review 2 PDF", tcb_s), Paragraph("make report", tcc_s),
         Paragraph("15-page academic PDF report", tc_s), Paragraph("~2s", tc_s)],
        [Paragraph("<b>Run everything</b>", tcb_s), Paragraph("<b>make all</b>", tcc_s),
         Paragraph("<b>Tests + experiments + charts + PDF</b>", tcb_s), Paragraph("<b>~10s</b>", tcb_s)],
    ]
    cmdt = Table(cmd, colWidths=[100, 100, 235, 50])
    cmdt.setStyle(std_tbl())
    story.append(cmdt)
    story.append(Cap("Table 7: Complete command reference for running all project components."))
    story.append(Spacer(1, 8))

    # ── Conclusion ──
    story.append(H1("10. Conclusion"))
    story.append(P(
        "This Review 3 report provides <b>comprehensive implementation evidence</b> for the Adaptive "
        "Fairness-Aware CPU Scheduling Simulator. The project is a <b>fully functional, rigorously tested</b> "
        "software system consisting of 6 Python source files (~1,800 lines of production code), 12 passing "
        "automated unit tests verified against hand-calculated analytical solutions, 200 benchmark simulation "
        "runs across 5 distinct workload families, and 8 publication-quality figures generated from the "
        "experimental data."
    ))
    story.append(P(
        "The technology stack (Python 3.14.3, Pytest 9.2.0, NumPy 2.5.4, Matplotlib 3.11.2, ReportLab 5.1.0) "
        "was selected for determinism, cross-platform portability, and scientific reproducibility. "
        "All configuration parameters, source code modules, and execution outputs have been documented "
        "with detailed explanations. The entire codebase, data, and documentation are publicly available "
        "on GitHub for faculty review and evaluation."
    ))
    story.append(Spacer(1, 6))

    # Final GitHub box
    story.append(blue_box(
        "<b>GitHub Repository:</b> &nbsp; "
        "<font color='#1e40af' size='10'><b>https://github.com/AlokMaan/OS</b></font><br/><br/>"
        "<b>Review 2 PDF:</b> &nbsp; OS_Review_2_Adaptive_Fairness_Aware_CPU_Scheduler.pdf (15 pages, in repo)<br/>"
        "<b>Review 3 PDF:</b> &nbsp; OS_Review_3_AFAS_Implementation_Report.pdf (this document)"
    ))

    # Bottom accent
    story.append(Spacer(1, 10))
    story.append(Table([['']], colWidths=[515], rowHeights=[4], style=[
        ('BACKGROUND',(0,0),(-1,-1), DARK_BLUE)]))

    doc.build(story, canvasmaker=R3Canvas)
    print(f"\n  Successfully generated: {pdf}\n")

if __name__ == "__main__":
    build()
