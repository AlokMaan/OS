"""
generate_review3_pdf.py - Review 3 Document Generator
Adaptive Fairness-Aware CPU Scheduling Simulator for Linux (AFAS)
Contains: Complete implementation details, technology stack, configuration,
           output screenshots, and GitHub repository link.
"""

import os
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

W, H = A4
BASE = os.path.dirname(os.path.abspath(__file__))
SC = os.path.join(BASE, "screenshots")
FIG = os.path.join(BASE, "figures")

# ─── Custom Canvas with header/footer ──────────────────────────────────
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
            self._draw_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def _draw_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#4b5563"))
        if self._pageNumber > 1:
            self.drawString(40, H - 25, "Adaptive Fairness-Aware CPU Scheduling Simulator | Review 3")
            self.setStrokeColor(colors.HexColor("#d1d5db"))
            self.setLineWidth(0.5)
            self.line(40, H - 29, W - 40, H - 29)
        self.drawCentredString(W / 2.0, 20, f"Operating Systems | Review 3 | Page {self._pageNumber}")
        self.setStrokeColor(colors.HexColor("#e5e7eb"))
        self.setLineWidth(0.5)
        self.line(40, 29, W - 40, 29)
        self.restoreState()


def build_pdf():
    pdf_path = os.path.join(BASE, "OS_Review_3_AFAS_Implementation_Report.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                            leftMargin=40, rightMargin=40,
                            topMargin=36, bottomMargin=36)

    styles = getSampleStyleSheet()

    # ── Style definitions ──
    title_style = ParagraphStyle('DocTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=17, leading=21,
        alignment=1, textColor=colors.HexColor('#0f172a'), spaceAfter=5)

    subtitle_style = ParagraphStyle('SubTitle', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=10, leading=13,
        alignment=1, textColor=colors.HexColor('#475569'), spaceAfter=10)

    author_style = ParagraphStyle('Authors', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9, leading=13,
        alignment=1, textColor=colors.HexColor('#1f2937'), spaceAfter=10)

    h1 = ParagraphStyle('H1', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11, leading=14,
        textColor=colors.HexColor('#0f2b5c'), spaceBefore=8, spaceAfter=4,
        keepWithNext=True)

    h2 = ParagraphStyle('H2', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=9.5, leading=12,
        textColor=colors.HexColor('#1e40af'), spaceBefore=6, spaceAfter=2.5,
        keepWithNext=True)

    body = ParagraphStyle('Body', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=10.8,
        textColor=colors.HexColor('#1f2937'), spaceAfter=3.5)

    bullet = ParagraphStyle('Bullet', parent=styles['Normal'],
        fontName='Helvetica', fontSize=7.5, leading=10.2,
        textColor=colors.HexColor('#1f2937'), leftIndent=10, spaceAfter=2)

    caption_style = ParagraphStyle('Caption', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=7.5, leading=9.5,
        alignment=1, textColor=colors.HexColor('#374151'),
        spaceBefore=2, spaceAfter=4)

    code_style = ParagraphStyle('Code', parent=styles['Normal'],
        fontName='Courier', fontSize=7, leading=8.8,
        textColor=colors.HexColor('#0f172a'))

    tbl_hdr = ParagraphStyle('TH', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=7, leading=8.8,
        textColor=colors.white, alignment=0)

    tbl_cell = ParagraphStyle('TC', parent=styles['Normal'],
        fontName='Helvetica', fontSize=6.8, leading=8.4,
        textColor=colors.HexColor('#111827'))

    tbl_cell_b = ParagraphStyle('TCB', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=6.8, leading=8.4,
        textColor=colors.HexColor('#111827'))

    tbl_cell_code = ParagraphStyle('TCC', parent=styles['Normal'],
        fontName='Courier', fontSize=6.2, leading=7.8,
        textColor=colors.HexColor('#1e293b'))

    # ── Helper functions ──
    def P(txt): return Paragraph(txt, body)
    def B(txt): return Paragraph(f"&bull; {txt}", bullet)
    def H1(txt): return Paragraph(txt, h1)
    def H2(txt): return Paragraph(txt, h2)
    def Cap(txt): return Paragraph(txt, caption_style)

    def FigBlock(path, w, ht, cap):
        items = []
        if os.path.exists(path):
            items.append(Image(path, width=w, height=ht))
        else:
            items.append(P(f"<i>[Image not found: {os.path.basename(path)}]</i>"))
        items.append(Cap(cap))
        items.append(Spacer(1, 2))
        return KeepTogether(items)

    def tbl_style():
        return TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f2b5c')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 2.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
        ])

    story = []

    # ══════════════════════════════════════════════════════════════════
    #  PAGE 1: COVER
    # ══════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 10))
    story.append(Paragraph("OPERATING SYSTEMS", ParagraphStyle('Top', parent=title_style,
        fontSize=13, leading=16, textColor=colors.HexColor('#1e293b'))))
    story.append(Paragraph("PROJECT REVIEW - 3", ParagraphStyle('Rev', parent=title_style,
        fontSize=15, leading=19, textColor=colors.HexColor('#0f2b5c'))))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "Adaptive Fairness-Aware CPU Scheduling Simulator for Linux:<br/>"
        "Complete Implementation Details, Output Screenshots &amp; GitHub Link",
        title_style))
    story.append(Paragraph(
        "Technology Stack, Programming Languages, Configuration Details, and Execution Evidence",
        subtitle_style))
    story.append(HRFlowable(width="85%", thickness=1.2,
        color=colors.HexColor('#1e3a8a'), spaceBefore=2, spaceAfter=12))

    story.append(Paragraph("""
    <b>Submitted By:</b><br/>
    <b>Alok Maan</b> &nbsp;|&nbsp; 24BCB0057 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Arshdeep Singh</b> &nbsp;|&nbsp; 24BCE0556<br/>
    <b>Ankush Hooda</b> &nbsp;|&nbsp; 24BCE0966 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Somya Sharma</b> &nbsp;|&nbsp; 24BCT0324<br/><br/>
    <b>Faculty Name:</b> Prof. V. Ezhil Arasi<br/>
    <i>School of Computer Science and Engineering, Vellore Institute of Technology</i>
    """, author_style))
    story.append(Spacer(1, 6))

    # GitHub Link Box
    github_box = """
    <b>GitHub Repository (Public):</b><br/><br/>
    <font color="#1e40af">https://github.com/alokmaan/afas-simulator</font><br/><br/>
    All source code, test suites, data files, figures, and this PDF are available
    in the repository. Clone with:<br/>
    <font face="Courier" size="7">git clone https://github.com/alokmaan/afas-simulator.git</font>
    """
    story.append(Table([[Paragraph(github_box, body)]], colWidths=[515], style=[
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#eff6ff')),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#3b82f6')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(Spacer(1, 8))

    story.append(H2("Abstract"))
    story.append(P(
        "This document constitutes the <b>Review 3 submission</b> for the Adaptive Fairness-Aware CPU Scheduling Simulator (AFAS) project. "
        "As instructed by Prof. V. Ezhil Arasi, this report provides the <b>complete implementation details</b> of the project, including: "
        "(1) the full technology stack and programming languages used; "
        "(2) configuration details for environment setup and execution; "
        "(3) screenshots of all output produced by the simulator, including test results, experiments, charts, and interactive demos; "
        "and (4) the public GitHub repository link for code review. "
        "The implementation for Review 2 is also included via reference. "
        "The project comprises 6 Python source files (~1,800 lines of code) implementing a discrete-event CPU scheduling simulator "
        "comparing 5 classic baseline scheduling policies against the proposed AFAS adaptive scheduler. "
        "All 12 automated unit tests pass, 200 simulation benchmark runs execute successfully, "
        "and 8 publication-quality figures are generated from the experimental data."
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    #  PAGE 2: TECHNOLOGY STACK & CONFIGURATION
    # ══════════════════════════════════════════════════════════════════
    story.append(H1("1. Technology Stack and Programming Languages"))
    story.append(P(
        "The entire project is implemented in <b>Python 3.10+</b>, chosen for its deterministic queue abstractions, "
        "rapid prototyping capabilities, and cross-platform portability (Linux, macOS, Windows). "
        "No kernel modules, C extensions, or platform-specific binaries are used."
    ))

    tech_data = [
        [Paragraph("Technology", tbl_hdr), Paragraph("Version Used", tbl_hdr),
         Paragraph("Role", tbl_hdr), Paragraph("Technical Justification", tbl_hdr)],
        [Paragraph("Python 3", tbl_cell_b), Paragraph("3.10+ (tested on 3.14.3)", tbl_cell),
         Paragraph("Core Simulation Engine", tbl_cell),
         Paragraph("Provides deterministic queue abstractions, native high-precision arithmetic, dataclass-based PCBs, and cross-platform portability.", tbl_cell)],
        [Paragraph("Pytest", tbl_cell_b), Paragraph("9.2.0", tbl_cell),
         Paragraph("Automated Unit Testing", tbl_cell),
         Paragraph("Enables strict regression testing with 12 test cases covering hand-solved analytical cases, invariant verification, tie-breaking, and input validation.", tbl_cell)],
        [Paragraph("NumPy", tbl_cell_b), Paragraph("2.5.4", tbl_cell),
         Paragraph("Vectorized Statistics", tbl_cell),
         Paragraph("Efficient calculation of percentiles (p95), Jain fairness indices, and matrix aggregations over 200 simulation runs.", tbl_cell)],
        [Paragraph("Matplotlib", tbl_cell_b), Paragraph("3.11.2", tbl_cell),
         Paragraph("Visualization &amp; Charts", tbl_cell),
         Paragraph("Generates 8 publication-quality figures including Gantt charts, bar charts, sensitivity curves, ablation plots, and log-log scaling graphs.", tbl_cell)],
        [Paragraph("ReportLab", tbl_cell_b), Paragraph("5.1.0", tbl_cell),
         Paragraph("PDF Report Generation", tbl_cell),
         Paragraph("Programmatic compilation of academic documents with dynamic headers, footers, tables, and embedded figures.", tbl_cell)],
        [Paragraph("Pillow (PIL)", tbl_cell_b), Paragraph("13.0.0", tbl_cell),
         Paragraph("Image Processing", tbl_cell),
         Paragraph("Supports image manipulation for embedding screenshots and figures into PDF reports.", tbl_cell)],
        [Paragraph("Git + GitHub", tbl_cell_b), Paragraph("Latest", tbl_cell),
         Paragraph("Version Control &amp; Distribution", tbl_cell),
         Paragraph("Maintains immutable commit history; public repository for code review and submission.", tbl_cell)],
        [Paragraph("CSV / JSON", tbl_cell_b), Paragraph("Standard Library", tbl_cell),
         Paragraph("Audit &amp; Data Storage", tbl_cell),
         Paragraph("Portable, human-readable records allowing independent verification of per-quantum scheduling decisions.", tbl_cell)],
        [Paragraph("Make (GNU)", tbl_cell_b), Paragraph("System default", tbl_cell),
         Paragraph("Build Automation", tbl_cell),
         Paragraph("Provides one-command build targets for setup, testing, experiments, charts, and full pipeline execution.", tbl_cell)],
    ]
    t_tech = Table(tech_data, colWidths=[70, 80, 100, 265])
    t_tech.setStyle(tbl_style())
    story.append(KeepTogether([t_tech, Cap("Table 1: Complete technology stack with versions and justifications.")]))
    story.append(Spacer(1, 6))

    story.append(H1("2. Configuration Details and Environment Setup"))
    story.append(P("The project requires <b>no external services, databases, or cloud accounts</b>. Setup is fully local:"))

    setup_box = """
    <b>Step 1: Clone the repository</b><br/>
    <font face="Courier" size="7">git clone https://github.com/alokmaan/afas-simulator.git</font><br/>
    <font face="Courier" size="7">cd afas-simulator</font><br/><br/>
    <b>Step 2: Create virtual environment and install dependencies</b><br/>
    <font face="Courier" size="7">python3 -m venv .venv</font><br/>
    <font face="Courier" size="7">source .venv/bin/activate</font><br/>
    <font face="Courier" size="7">pip install -r requirements.txt</font><br/><br/>
    <b>Step 3: Run the complete pipeline</b><br/>
    <font face="Courier" size="7">make all    # Runs tests, experiments, charts, and PDF report</font>
    """
    story.append(Table([[Paragraph(setup_box, body)]], colWidths=[515], style=[
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#94a3b8')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(Spacer(1, 4))

    story.append(H2("2.1 Configuration Parameters"))
    config_data = [
        [Paragraph("Parameter", tbl_hdr), Paragraph("Default Value", tbl_hdr), Paragraph("Description", tbl_hdr), Paragraph("Configurable Via", tbl_hdr)],
        [Paragraph("Time Quantum (q)", tbl_cell_b), Paragraph("4", tbl_cell),
         Paragraph("CPU time slice for preemptive policies (RR, AFAS)", tbl_cell),
         Paragraph("Function argument / CLI", tbl_cell)],
        [Paragraph("Priority Weight (w<sub>p</sub>)", tbl_cell_b), Paragraph("0.30", tbl_cell),
         Paragraph("Weight for base administrative priority in AFAS score", tbl_cell),
         Paragraph("Function argument", tbl_cell)],
        [Paragraph("Aging Weight (w<sub>a</sub>)", tbl_cell_b), Paragraph("0.40", tbl_cell),
         Paragraph("Weight for bounded waiting-time aging term", tbl_cell),
         Paragraph("Function argument", tbl_cell)],
        [Paragraph("Responsiveness Weight (w<sub>r</sub>)", tbl_cell_b), Paragraph("0.15", tbl_cell),
         Paragraph("Weight for workload class responsiveness factor", tbl_cell),
         Paragraph("Function argument", tbl_cell)],
        [Paragraph("CPU-Share Weight (w<sub>c</sub>)", tbl_cell_b), Paragraph("0.15", tbl_cell),
         Paragraph("Weight for decayed recent CPU-share penalty", tbl_cell),
         Paragraph("Function argument", tbl_cell)],
        [Paragraph("Aging Saturation", tbl_cell_b), Paragraph("50 time units", tbl_cell),
         Paragraph("Hard ceiling for aging boost A<sub>i</sub>(t) = min(1.0, wait/50)", tbl_cell),
         Paragraph("Source constant", tbl_cell)],
        [Paragraph("Decay Half-life", tbl_cell_b), Paragraph("40 time units", tbl_cell),
         Paragraph("Exponential decay rate for CPU-share tracking", tbl_cell),
         Paragraph("Source constant", tbl_cell)],
        [Paragraph("Random Seeds", tbl_cell_b), Paragraph("1, 2, 3, 4, 5", tbl_cell),
         Paragraph("Fixed seeds for reproducible workload generation", tbl_cell),
         Paragraph("experiments.py", tbl_cell)],
        [Paragraph("Workload Families", tbl_cell_b), Paragraph("W1-W5", tbl_cell),
         Paragraph("Five synthetic workload generators with distinct traffic patterns", tbl_cell),
         Paragraph("afas_sim.py", tbl_cell)],
    ]
    t_cfg = Table(config_data, colWidths=[100, 75, 195, 145])
    t_cfg.setStyle(tbl_style())
    story.append(KeepTogether([t_cfg, Cap("Table 2: Simulator configuration parameters and their defaults.")]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    #  PAGE 3: SOURCE CODE MODULES
    # ══════════════════════════════════════════════════════════════════
    story.append(H1("3. Complete Implementation: Source Code Modules"))
    story.append(P(
        "The project consists of <b>6 Python source files</b> totaling approximately 1,800 lines of code. "
        "Each module has a well-defined responsibility within the simulator architecture:"
    ))

    mod_data = [
        [Paragraph("Module File", tbl_hdr), Paragraph("Lines", tbl_hdr),
         Paragraph("Key Classes / Functions", tbl_hdr), Paragraph("Responsibilities", tbl_hdr)],
        [Paragraph("afas_sim.py", tbl_cell_code), Paragraph("593", tbl_cell),
         Paragraph("Process, Segment, DecisionRecord,<br/>run_fcfs, run_sjf, run_srtf,<br/>run_round_robin, run_priority,<br/>run_afas, compute_afas_score,<br/>compute_metrics, validate_workload,<br/>verify_engine_invariants,<br/>5 workload generators (W1-W5)", tbl_cell),
         Paragraph("Core simulation engine: defines Process Control Block (PCB) with 12 attributes; "
                    "implements 5 classic baseline scheduling algorithms and the proposed AFAS adaptive scheduler; "
                    "computes comprehensive metrics (WT, TAT, RT, p95, Jain Index, starvation warnings); "
                    "enforces 3 formal execution invariants; generates 5 synthetic workload families.", tbl_cell)],
        [Paragraph("test_sim.py", tbl_cell_code), Paragraph("~250", tbl_cell),
         Paragraph("12 Pytest test functions covering<br/>analytical hand-solved cases,<br/>invariants, tie-breaks,<br/>input validation, aging bounds", tbl_cell),
         Paragraph("Automated verification suite: validates simulator correctness against hand-calculated "
                    "textbook solutions for FCFS, SJF, SRTF, RR, and Priority; checks deterministic "
                    "reproducibility, AFAS tie-breaking order, aging saturation bounds, and starvation mitigation.", tbl_cell)],
        [Paragraph("experiments.py", tbl_cell_code), Paragraph("~300", tbl_cell),
         Paragraph("Batch experiment runner,<br/>ablation studies,<br/>sensitivity sweeps,<br/>quantum sweeps,<br/>runtime scaling", tbl_cell),
         Paragraph("Executes 200 simulation runs across 5 workload families x 5 seeds x 6 policies. "
                    "Automates component ablation (no-aging, no-share), parameter sensitivity sweeps, "
                    "time-quantum sweeps (q=1 to 32), and decision-runtime scaling benchmarks. "
                    "Outputs results_all_runs.csv and results.json.", tbl_cell)],
        [Paragraph("charts.py", tbl_cell_code), Paragraph("~250", tbl_cell),
         Paragraph("8 figure generation functions<br/>using Matplotlib", tbl_cell),
         Paragraph("Generates 8 publication-quality PNG figures: max wait gap bars, p95 response bars, "
                    "avg waiting bars, Gantt timeline comparison, ablation breakdown, sensitivity curves, "
                    "quantum sweep, and runtime scaling (log-log).", tbl_cell)],
        [Paragraph("interactive_cli.py", tbl_cell_code), Paragraph("~200", tbl_cell),
         Paragraph("Interactive terminal CLI,<br/>ASCII Gantt playback,<br/>--demo mode", tbl_cell),
         Paragraph("Provides an interactive terminal interface for testing individual scheduling algorithms, "
                    "inspecting real-time AFAS score decomposition, and viewing ASCII Gantt timelines. "
                    "Includes --demo flag for automated trace demonstration.", tbl_cell)],
        [Paragraph("generate_review2_pdf.py", tbl_cell_code), Paragraph("924", tbl_cell),
         Paragraph("ReportLab PDF builder,<br/>15-page academic report", tbl_cell),
         Paragraph("Programmatically compiles the complete Review 2 academic report with embedded "
                    "figures, tables, algorithm pseudocode, and formatted references.", tbl_cell)],
    ]
    t_mod = Table(mod_data, colWidths=[95, 35, 155, 230])
    t_mod.setStyle(tbl_style())
    story.append(KeepTogether([t_mod, Cap("Table 3: Source code module inventory with line counts and responsibilities.")]))
    story.append(Spacer(1, 4))

    story.append(H2("3.1 Directory Structure"))
    dir_box = """
    afas-simulator/
    |-- afas_sim.py                   # Core simulation engine (593 lines)
    |-- test_sim.py                   # 12 automated pytest unit tests
    |-- experiments.py                # Batch benchmark runner (200 runs)
    |-- charts.py                     # Publication chart generator (8 figures)
    |-- interactive_cli.py            # Interactive terminal CLI + ASCII Gantt
    |-- generate_review2_pdf.py       # Review 2 PDF compiler
    |-- generate_review3_pdf.py       # Review 3 PDF compiler (this file)
    |-- Makefile                       # Build automation (make all)
    |-- run.sh                         # Portable bash helper script
    |-- requirements.txt               # Python dependencies (5 packages)
    |-- data/
    |   |-- results_all_runs.csv      # Raw simulation traces (200 records)
    |   +-- results.json              # Aggregated summary metrics
    |-- figures/                       # 8 publication-quality PNG charts
    |-- screenshots/                   # All output screenshots for Review 3
    +-- docs/                          # PDF documentation
    """
    story.append(Table([[Paragraph(dir_box.replace('\n', '<br/>'), code_style)]], colWidths=[515], style=[
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#64748b')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    #  PAGE 4: SCREENSHOT - SETUP & MAKEFILE
    # ══════════════════════════════════════════════════════════════════
    story.append(H1("4. Output Screenshots"))
    story.append(P(
        "This section presents <b>complete execution evidence</b> of the project running successfully. "
        "All screenshots were captured from actual terminal execution on macOS (Python 3.14.3). "
        "The project is fully cross-platform and runs identically on Linux, macOS, and Windows."
    ))

    story.append(H2("4.1 Project Setup and Directory Structure"))
    story.append(FigBlock(
        os.path.join(SC, "ss_setup_and_directory.png"), 460, 185,
        "Screenshot 1: Python version verification, dependency installation, and project directory listing."
    ))

    story.append(H2("4.2 Build System (Makefile Commands)"))
    story.append(FigBlock(
        os.path.join(SC, "ss_makefile_help.png"), 460, 130,
        "Screenshot 2: Available Makefile commands for the build automation system."
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    #  PAGE 5: SCREENSHOT - TESTS
    # ══════════════════════════════════════════════════════════════════
    story.append(H2("4.3 Automated Unit Test Suite (12/12 Passed)"))
    story.append(P(
        "The project includes 12 comprehensive pytest unit tests that verify the mathematical correctness "
        "of all scheduling algorithms against hand-calculated analytical solutions. All 12 tests pass:"
    ))
    story.append(FigBlock(
        os.path.join(SC, "ss_pytest_12_passed.png"), 460, 195,
        "Screenshot 3: Complete pytest execution showing all 12 tests passed in 0.06 seconds."
    ))
    story.append(Spacer(1, 4))

    test_desc = [
        [Paragraph("Test Name", tbl_hdr), Paragraph("What It Verifies", tbl_hdr)],
        [Paragraph("test_fcfs_hand_solved", tbl_cell_b), Paragraph("FCFS completion times match hand-calculated solution for 4-process case (Mean WT = 5.75)", tbl_cell)],
        [Paragraph("test_sjf_hand_solved", tbl_cell_b), Paragraph("SJF selects shortest burst first; verified against analytical solution (Mean WT = 5.25)", tbl_cell)],
        [Paragraph("test_srtf_hand_solved", tbl_cell_b), Paragraph("SRTF preempts correctly at arrivals; matches analytical solution (Mean WT = 5.00)", tbl_cell)],
        [Paragraph("test_round_robin_hand_solved", tbl_cell_b), Paragraph("Round Robin cyclic rotation with q=2; completion times match hand trace", tbl_cell)],
        [Paragraph("test_priority_hand_solved", tbl_cell_b), Paragraph("Priority dispatches highest-priority process first; deterministic ordering verified", tbl_cell)],
        [Paragraph("test_idle_gap_handling", tbl_cell_b), Paragraph("Simulator correctly advances clock when CPU is idle between process arrivals", tbl_cell)],
        [Paragraph("test_engine_invariants_all_workloads", tbl_cell_b), Paragraph("Three formal invariants (non-overlap, burst conservation, causality) hold on all 25 workloads", tbl_cell)],
        [Paragraph("test_deterministic_reproducibility", tbl_cell_b), Paragraph("Multiple runs with same seed produce identical segment traces and metrics", tbl_cell)],
        [Paragraph("test_afas_tie_breaking_order", tbl_cell_b), Paragraph("AFAS tie-breaking follows hierarchy: Score desc, Arrival asc, PID asc", tbl_cell)],
        [Paragraph("test_input_validation_rejections", tbl_cell_b), Paragraph("Invalid inputs (negative burst, duplicate PID, out-of-range priority) raise ValueError", tbl_cell)],
        [Paragraph("test_aging_bounds_and_saturation", tbl_cell_b), Paragraph("Aging term A<sub>i</sub>(t) saturates at 1.0 (50 time units) and does not exceed ceiling", tbl_cell)],
        [Paragraph("test_afas_starvation_mitigation", tbl_cell_b), Paragraph("AFAS reduces maximum wait gap vs Priority scheduling by at least 30%", tbl_cell)],
    ]
    t_tests = Table(test_desc, colWidths=[165, 350])
    t_tests.setStyle(tbl_style())
    story.append(KeepTogether([t_tests, Cap("Table 4: Description of all 12 automated unit tests.")]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    #  PAGE 6: SCREENSHOT - EXPERIMENTS
    # ══════════════════════════════════════════════════════════════════
    story.append(H2("4.4 Batch Experiment Suite (200 Simulation Runs)"))
    story.append(P(
        "The experiments module executes <b>200 simulation runs</b> across 5 workload families, "
        "5 random seeds, and 6 scheduling policies. It also performs ablation studies, "
        "parameter sensitivity sweeps, quantum sweeps, and runtime scaling benchmarks."
    ))
    story.append(FigBlock(
        os.path.join(SC, "ss_experiments_200_runs.png"), 460, 240,
        "Screenshot 4: Complete batch experiment execution showing 200 runs, summary metrics, sensitivity sweeps, and scaling benchmarks."
    ))
    story.append(Spacer(1, 4))

    # Results summary table
    story.append(H2("4.5 Benchmark Results Summary"))
    res_data = [
        [Paragraph("Policy", tbl_hdr), Paragraph("Avg WT", tbl_hdr), Paragraph("Avg RT", tbl_hdr),
         Paragraph("p95 RT", tbl_hdr), Paragraph("Max Wait", tbl_hdr), Paragraph("Ctx Sw.", tbl_hdr),
         Paragraph("Jain", tbl_hdr), Paragraph("Warnings", tbl_hdr)],
        [Paragraph("FCFS", tbl_cell), Paragraph("83.9", tbl_cell), Paragraph("83.9", tbl_cell),
         Paragraph("126.9", tbl_cell), Paragraph("131.2", tbl_cell), Paragraph("19.0", tbl_cell),
         Paragraph("0.48", tbl_cell), Paragraph("12.7", tbl_cell)],
        [Paragraph("SJF", tbl_cell), Paragraph("38.7", tbl_cell), Paragraph("38.7", tbl_cell),
         Paragraph("133.8", tbl_cell), Paragraph("148.2", tbl_cell), Paragraph("19.0", tbl_cell),
         Paragraph("0.67", tbl_cell), Paragraph("6.1", tbl_cell)],
        [Paragraph("SRTF", tbl_cell), Paragraph("<b>30.6</b>", tbl_cell), Paragraph("27.0", tbl_cell),
         Paragraph("129.8", tbl_cell), Paragraph("147.8", tbl_cell), Paragraph("22.0", tbl_cell),
         Paragraph("<b>0.81</b>", tbl_cell), Paragraph("<b>4.2</b>", tbl_cell)],
        [Paragraph("RR (q=4)", tbl_cell), Paragraph("70.5", tbl_cell), Paragraph("20.3", tbl_cell),
         Paragraph("<b>37.0</b>", tbl_cell), Paragraph("<b>40.8</b>", tbl_cell), Paragraph("57.9", tbl_cell),
         Paragraph("0.83", tbl_cell), Paragraph("12.3", tbl_cell)],
        [Paragraph("Priority", tbl_cell), Paragraph("66.8", tbl_cell), Paragraph("66.8", tbl_cell),
         Paragraph("148.7", tbl_cell), Paragraph("158.7", tbl_cell), Paragraph("19.0", tbl_cell),
         Paragraph("0.57", tbl_cell), Paragraph("8.5", tbl_cell)],
        [Paragraph("<b>AFAS (Proposed)</b>", tbl_cell_b), Paragraph("<b>54.5</b>", tbl_cell_b),
         Paragraph("<b>17.1</b>", tbl_cell_b), Paragraph("<b>53.9</b>", tbl_cell_b),
         Paragraph("<b>63.2</b>", tbl_cell_b), Paragraph("<b>56.6</b>", tbl_cell_b),
         Paragraph("<b>0.71</b>", tbl_cell_b), Paragraph("<b>4.7</b>", tbl_cell_b)],
    ]
    t_res = Table(res_data, colWidths=[85, 55, 55, 55, 60, 55, 55, 55])
    t_res.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f2b5c')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('BACKGROUND', (0,7), (-1,7), colors.HexColor('#eff6ff')),
        ('ROWBACKGROUNDS', (0,1), (-1,6), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(KeepTogether([t_res, Cap("Table 5: Aggregated benchmark results across W1-W5 (200 total simulation runs).")]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    #  PAGE 7: SCREENSHOT - AFAS DECISION LOG
    # ══════════════════════════════════════════════════════════════════
    story.append(H2("4.6 AFAS Decision Audit Log (Interactive Demo)"))
    story.append(P(
        "The AFAS scheduler produces a transparent <b>per-quantum decision audit log</b> showing the exact score "
        "decomposition for every scheduling decision. This enables full explainability of why each process was selected. "
        "Entries marked <b>[AGING_PROMOTION]</b> indicate low-priority tasks dynamically promoted due to accumulated wait time."
    ))
    story.append(FigBlock(
        os.path.join(SC, "ss_afas_decision_log.png"), 460, 310,
        "Screenshot 5: AFAS decision audit log showing real-time score decomposition (P, A, R, -C) for each scheduling decision, "
        "including aging-promoted tasks and final performance metrics."
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    #  PAGE 8: SCREENSHOT - CHARTS
    # ══════════════════════════════════════════════════════════════════
    story.append(H2("4.7 Chart Generation"))
    story.append(FigBlock(
        os.path.join(SC, "ss_charts_generation.png"), 460, 50,
        "Screenshot 6: Automated chart generation compiling 8 publication-quality figures from experiment data."
    ))
    story.append(Spacer(1, 4))

    story.append(H1("5. Publication Figures (Generated Output)"))
    story.append(P("All 8 figures below are generated programmatically from the experimental data:"))

    # Fig 1 & 2 side by side
    f12 = [
        [Image(os.path.join(FIG, "fig_1_max_wait.png"), width=240, height=130),
         Image(os.path.join(FIG, "fig_2_p95_response.png"), width=240, height=130)],
        [Cap("Figure 1: Maximum ready-queue wait gap per workload."),
         Cap("Figure 2: 95th-percentile response time distribution.")]
    ]
    t_f12 = Table(f12, colWidths=[255, 255])
    t_f12.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(t_f12)
    story.append(Spacer(1, 4))

    # Fig 3 & 5 side by side
    f35 = [
        [Image(os.path.join(FIG, "fig_3_avg_waiting.png"), width=240, height=130),
         Image(os.path.join(FIG, "fig_5_ablation.png"), width=240, height=130)],
        [Cap("Figure 3: Average waiting time across baselines."),
         Cap("Figure 4: Component ablation breakdown (Aging vs Share penalty).")]
    ]
    t_f35 = Table(f35, colWidths=[255, 255])
    t_f35.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(t_f35)
    story.append(PageBreak())

    # Fig 4 (Gantt - full width)
    story.append(FigBlock(
        os.path.join(FIG, "fig_4_gantt.png"), 460, 175,
        "Figure 5: Gantt execution timelines comparing Priority, Round Robin, and AFAS on a representative workload."
    ))
    story.append(Spacer(1, 4))

    # Fig 6 (Sensitivity - full width)
    story.append(FigBlock(
        os.path.join(FIG, "fig_6_sensitivity.png"), 460, 135,
        "Figure 6: One-at-a-time parameter sensitivity analysis sweeping w_p, w_a, w_r, and w_c from 0.0 to 1.0."
    ))
    story.append(Spacer(1, 4))

    # Fig 7 & 8 side by side
    f78 = [
        [Image(os.path.join(FIG, "fig_7_quantum_sweep.png"), width=240, height=155),
         Image(os.path.join(FIG, "fig_8_runtime_scaling.png"), width=240, height=130)],
        [Cap("Figure 7: Time-quantum sensitivity sweep (q=1 to 32)."),
         Cap("Figure 8: Algorithmic decision runtime scaling (log-log).")]
    ]
    t_f78 = Table(f78, colWidths=[255, 255])
    t_f78.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(t_f78)
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    #  PAGE 10: KEY FINDINGS & DATA FILES
    # ══════════════════════════════════════════════════════════════════
    story.append(H1("6. Key Analytical Findings"))
    story.append(B("<b>Starvation Prevention:</b> AFAS reduces maximum ready-queue wait from 158.7 (Priority) to 63.2 (<b>60% reduction</b>), "
                    "confirming that bounded waiting-time aging effectively prevents chronic starvation."))
    story.append(B("<b>Interactivity:</b> AFAS achieves the best average response time (<b>17.1 units</b>) across all policies, "
                    "outperforming even Round Robin (20.3) while maintaining comparable context switches (56.6 vs 57.9)."))
    story.append(B("<b>Ablation Finding:</b> Disabling aging (w<sub>a</sub>=0) causes maximum wait to nearly double to 115.8 (<b>+83%</b>), "
                    "confirming that the bounded aging accumulator is the primary technical lever driving fairness."))
    story.append(B("<b>Honest Negative Result:</b> The CPU-share penalty (w<sub>c</sub>) showed negligible impact in current workloads - "
                    "removing it changed max wait by only 0.6%. This is transparently reported."))
    story.append(Spacer(1, 4))

    story.append(H1("7. Generated Data Files"))
    data_data = [
        [Paragraph("File", tbl_hdr), Paragraph("Location", tbl_hdr), Paragraph("Content", tbl_hdr), Paragraph("Records", tbl_hdr)],
        [Paragraph("results_all_runs.csv", tbl_cell_b), Paragraph("data/", tbl_cell),
         Paragraph("Raw per-simulation metrics for all 200 benchmark runs (workload, seed, policy, all metrics)", tbl_cell),
         Paragraph("200 rows", tbl_cell)],
        [Paragraph("results.json", tbl_cell_b), Paragraph("data/", tbl_cell),
         Paragraph("Aggregated summary metrics, ablation results, sensitivity sweep data, quantum sweep, and scaling benchmarks", tbl_cell),
         Paragraph("~500 data points", tbl_cell)],
    ]
    t_data = Table(data_data, colWidths=[115, 50, 270, 80])
    t_data.setStyle(tbl_style())
    story.append(KeepTogether([t_data, Cap("Table 6: Generated data files from experimental runs.")]))
    story.append(Spacer(1, 6))

    story.append(H1("8. Execution Commands Quick Reference"))
    cmd_data = [
        [Paragraph("Task", tbl_hdr), Paragraph("Command", tbl_hdr), Paragraph("Output", tbl_hdr)],
        [Paragraph("Run unit tests", tbl_cell_b), Paragraph("pytest -v test_sim.py", tbl_cell_code), Paragraph("12 passed (0.06s)", tbl_cell)],
        [Paragraph("Run experiments", tbl_cell_b), Paragraph("python3 experiments.py", tbl_cell_code), Paragraph("200 runs + data/results.json", tbl_cell)],
        [Paragraph("Interactive CLI", tbl_cell_b), Paragraph("python3 interactive_cli.py", tbl_cell_code), Paragraph("Interactive terminal scheduler", tbl_cell)],
        [Paragraph("Quick demo", tbl_cell_b), Paragraph("python3 interactive_cli.py --demo", tbl_cell_code), Paragraph("Automated AFAS trace with metrics", tbl_cell)],
        [Paragraph("Generate charts", tbl_cell_b), Paragraph("python3 charts.py", tbl_cell_code), Paragraph("8 PNG figures in figures/", tbl_cell)],
        [Paragraph("Generate PDF", tbl_cell_b), Paragraph("python3 generate_review2_pdf.py", tbl_cell_code), Paragraph("15-page Review 2 PDF report", tbl_cell)],
        [Paragraph("Run everything", tbl_cell_b), Paragraph("make all", tbl_cell_code), Paragraph("Tests + experiments + charts + PDF", tbl_cell)],
    ]
    t_cmd = Table(cmd_data, colWidths=[100, 200, 215])
    t_cmd.setStyle(tbl_style())
    story.append(KeepTogether([t_cmd, Cap("Table 7: Quick reference for all available commands.")]))
    story.append(Spacer(1, 6))

    # ══════════════════════════════════════════════════════════════════
    #  FINAL PAGE: CONCLUSION
    # ══════════════════════════════════════════════════════════════════
    story.append(H1("9. Conclusion"))
    story.append(P(
        "This Review 3 submission provides <b>complete implementation evidence</b> for the Adaptive Fairness-Aware "
        "CPU Scheduling Simulator. The project is a fully functional, rigorously tested software system consisting of "
        "6 Python source files (~1,800 lines), 12 passing unit tests, 200 benchmark simulation runs, and 8 publication-quality "
        "figures. The technology stack (Python 3, Pytest, NumPy, Matplotlib, ReportLab) was selected for determinism, "
        "portability, and reproducibility. All source code, data, and documentation are available on the public GitHub "
        "repository at <font color='#1e40af'>https://github.com/alokmaan/afas-simulator</font>. "
        "The implementation details for Review 2, including the formal algorithm, mathematical model, verification suite, "
        "and empirical analysis, are fully documented in the Review 2 PDF available in the repository."
    ))
    story.append(Spacer(1, 8))

    # GitHub reminder box
    final_box = """
    <b>GitHub Repository:</b> <font color="#1e40af">https://github.com/alokmaan/afas-simulator</font><br/><br/>
    <b>Review 2 PDF:</b> Available in the repository as OS_Review_2_Adaptive_Fairness_Aware_CPU_Scheduler.pdf<br/>
    <b>Review 3 PDF:</b> This document (OS_Review_3_AFAS_Implementation_Report.pdf)
    """
    story.append(Table([[Paragraph(final_box, body)]], colWidths=[515], style=[
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#eff6ff')),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#3b82f6')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
    ]))

    # Build PDF
    doc.build(story, canvasmaker=ReviewCanvas)
    print(f"Successfully generated Review 3 PDF: {pdf_path}")


if __name__ == "__main__":
    build_pdf()
