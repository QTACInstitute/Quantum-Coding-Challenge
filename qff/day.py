"""The shared storyline of the day: the stop map (section 0) and the text blocks every notebook repeats.

show_day(stop, challenge) draws section 0.  The other functions return Markdown strings for the shared cells
(header, sections 0, 5, 6, glossary, optional IBM cell); tools/nbkit.py puts them into notebooks.
"""
from html import escape

STOPS = [
    {"n": 1, "ar": "المصدر", "en": "Source"},
    {"n": 2, "ar": "الطريق", "en": "Move"},
    {"n": 3, "ar": "المخزن", "en": "Store"},
    {"n": 4, "ar": "استخدام الطاقة", "en": "Use"},
]

CHALLENGES = [
    {"n": 1, "stop": 1, "label": "Seismic imaging · Hadamard edge detection"},
    {"n": 2, "stop": 1, "label": "Wind farm layout · VQE"},
    {"n": 3, "stop": 2, "label": "Grid sensor placement · QAOA"},
    {"n": 4, "stop": 2, "label": "LNG ship routing · QAOA"},
    {"n": 5, "stop": 2, "label": "Unit commitment · Grover adaptive search"},
    {"n": 6, "stop": 3, "label": "Battery chemistry · VQE"},
    {"n": 7, "stop": 3, "label": "Hydrogen catalyst · QPE"},
    {"n": 8, "stop": 3, "label": "Carbon-capture material · QPE"},
    {"n": 9, "stop": 4, "label": "Desalination scheduling · Grover adaptive search"},
    {"n": 10, "stop": 4, "label": "EV fleet (V2G) · quantum kernel"},
]

HEADINGS = [
    "## 0 · The journey so far — رحلة الكم",
    "## 1 · This stop — هذه المحطة",
    "## 2 · Made small — المسألة مصغَّرة",
    "## 3 · The algorithm — الخوارزمية",
    "## 4 · Compare — المقارنة",
    "## 5 · Build the explainer — ابنوا المنتَج",
    "## 6 · Pitch — العرض",
]

FONT = '"IBM Plex Sans", "IBM Plex Sans Arabic", "Noto Sans Arabic", "Segoe UI", Tahoma, sans-serif'
BLUE, RED, GREY = "#0F62FE", "#FA4D56", "#697077"


def _circle(c, lit, mine):
    """One small numbered circle for challenge c (ring if it is this team's challenge)."""
    ring = f"box-shadow:0 0 0 2px {RED};" if mine else ""
    bg, fg, bd = (("#fff", BLUE, "#fff") if lit else ("#fff", "#161616", "#C6C6C6"))
    return (f'<span style="display:inline-block;width:24px;height:24px;line-height:24px;border-radius:50%;'
            f'background:{bg};color:{fg};border:1px solid {bd};font-size:12px;text-align:center;margin:2px;{ring}">{c["n"]}</span>')


def _stop_box(stop, lit_stop, challenge):
    """One rounded box of the stop map."""
    lit = stop["n"] == lit_stop
    bg, fg, bd = (BLUE, "#fff", BLUE) if lit else ("#F4F4F4", "#161616", "#C6C6C6")
    sub = "#E0E0E0" if lit else GREY
    circles = "".join(_circle(c, lit, c["n"] == challenge) for c in CHALLENGES if c["stop"] == stop["n"])
    return (f'<div style="flex:1;min-width:120px;background:{bg};color:{fg};border:1px solid {bd};border-radius:12px;'
            f'padding:10px 8px;text-align:center">'
            f'<div dir="rtl" style="font-size:22px;line-height:1.3">{escape(stop["ar"])}</div>'
            f'<div style="font-size:13px;color:{sub}">{escape(stop["en"])}</div><div style="margin-top:6px">{circles}</div></div>')


def _list_item(c, challenge):
    """One line of the ten-challenge list; the team's own line is bold."""
    text = f'{c["n"]} {escape(c["label"])}'
    return f'<li style="margin:2px 0;{"font-weight:700;" if c["n"] == challenge else ""}list-style:none">{text}</li>'


def show_day(stop=None, challenge=None):
    """Draw the four-stop map with `stop` (1-4) lit and `challenge` (1-10) ringed. Returns IPython HTML.

    Example: qff.day.show_day(stop=2, challenge=5).  With no arguments nothing is lit (used for the README picture).
    """
    from IPython.display import HTML
    arrow = f'<div style="align-self:center;color:{GREY};font-size:20px;padding:0 4px">&#8594;</div>'
    row = arrow.join(_stop_box(s, stop, challenge) for s in STOPS)
    half = (len(CHALLENGES) + 1) // 2
    cols = "".join(f'<ul style="flex:1;margin:0;padding:0 8px">{"".join(_list_item(c, challenge) for c in part)}</ul>'
                   for part in (CHALLENGES[:half], CHALLENGES[half:]))
    html = (f'<div style="direction:ltr;max-width:900px;font-family:{FONT};color:#161616">'
            f'<div style="display:flex;gap:2px">{row}</div>'
            f'<div style="display:flex;margin-top:14px;font-size:14px">{cols}</div></div>')
    return HTML(html)


SETUP_CODE = '''# Setup: run me first. On Colab this clones the repo and installs the pinned packages (about 1 minute).
import sys, os, subprocess
if "google.colab" in sys.modules and not os.path.exists("Quantum-Coding-Challenge"):
    subprocess.run(["git", "clone", "-q", "https://github.com/QTACInstitute/Quantum-Coding-Challenge.git"], check=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", "Quantum-Coding-Challenge/requirements.txt"], check=True)
ROOT = "Quantum-Coding-Challenge" if os.path.exists("Quantum-Coding-Challenge/qff") else ".."
sys.path.insert(0, ROOT)
import warnings; warnings.filterwarnings("ignore")
import numpy as np, matplotlib.pyplot as plt
import qff
SEED = qff.SEED            # 2026
DATA = os.path.join(ROOT, "data")'''

HEADER_MD = '''# {n} · {title}
### {ar} · {stop_en} — رحلة الكم من مصدر الطاقة إلى الاستدامة · Quantum Journey from Energy Source to Sustainability
*Quantum Computing Challenge 2026, Riyadh · Team {n} · Prepared by Ahmed Elghadban, Quantumy*<br><sub>Reviewed by Ola Tarig</sub>

| | |
|---|---|
| Use case | {use_case} |
| Algorithm | {algorithm} |
| Toy size | {qubits} qubits, runs in under {minutes} min on a laptop |
| Day 1 | read sections 0–2 |
| Day 2 | sections 3–6, build, pitch |'''

SECTION0_MD = '''## 0 · The journey so far — رحلة الكم
**«من المصدر إلى استخدام الطاقة»** · From the wellspring to the lamp

Before you switch on a lamp tonight, energy will have made one journey. It is found, it is moved, it is stored, and then it is used. Ten teams follow that journey today. Each team owns one moment of it, and each moment has a problem that is hard for ordinary computers at full scale.

1. **المصدر · Source.** Find the energy and decide where to harvest it: read the rock under the ground, place the turbines in the wind.
2. **الطريق · Move.** Get it across the country: watch the grid, route the ships, decide which power stations run.
3. **المخزن · Store.** Keep it for later, and keep carbon out of the air: batteries, hydrogen, capture materials. This is chemistry.
4. **استخدام الطاقة · Use.** Spend it well: make fresh water, charge and discharge a fleet of cars.

Your notebook is one chapter. The cell below lights your stop and lists all ten chapters so you can see who comes before and after you. When you pitch, start by saying where in the journey you are.

One rule for the whole challenge: **be honest about what is real.** As of November 2026 nobody has shown a quantum computer beating the best classical method on any of these ten problems. Your job is to explain the problem, show the idea on a small example, and say clearly what the small example does and does not prove.'''

SECTION5_MD = '''## 5 · Build the explainer — ابنوا المنتَج
How you are scored depends on how you take part. Read your category below.

### A) In-person attendees: group effort
Your team builds **one product** together that teaches a visitor your use case and your algorithm. It is **50% of your score**. This category is a **group effort**: the whole team plans, builds, tests and presents the product together. The product does not have to be in Arabic.

**Your audience:** a first-year university student who has never seen a qubit. They have three minutes.

**Your product must answer four questions, in this order:**
1. What is the problem, and who has it? {use_case}
2. Why is it hard when it gets big? {counting_fact}
3. What does the quantum algorithm do differently? {single_idea}
4. How real is it today? (Use your section 4 results and the honesty statement.)

**Pick any format, except a PowerPoint presentation (.pptx).** It can be an interactive demo, an interactive website, a YouTube video, a small app, a game, or an interactive notebook, as long as it does not take more than 5 minutes.

**Three ideas that fit this stop** (take one, change it, or ignore them):
{ideas}

**Use from this notebook:** {reuse}

Qiskit integration and code is a separate 10%: keep your completed notebook tidy and show one cell of it.

**Time plan for the 2 h 20 build window:** 20 min agree the story and format · 70 min build · 20 min test on someone outside the team · 30 min rehearse the pitch.

### B) Online attendees: coding
The coding is worth **100 points**. You work **individually** and solve **one challenge**.'''

SECTION6_MD = '''## 6 · Pitch — العرض
You have **5 minutes** for your pitch and 3 minutes for questions from the judges. Presentation is 40% of your score.

| Minutes | What | Who |
|---|---|---|
| 0–0.5 | Where we are in the journey: stop, use case, one sentence | 1 speaker |
| 0.5–1.5 | The problem and why it is hard at scale | |
| 1.5–3 | The algorithm, with your toy example and one notebook cell | |
| 3–4 | Live demo of your product | |
| 4–5 | How real is it: your result against the classical baseline | |
| 5-8 | Questions | all |

**Questions you should expect**
1. Did the quantum method beat the classical one? (Answer honestly: {honest})
2. What happens when the problem is 100 times bigger?
3. Why this algorithm and not another?
4. {qa}
5. {qb}

**Checklist before you walk up**
- [ ] The notebook runs top to bottom and the self-checks pass
- [ ] Every number on screen comes from your notebook or from a named source
- [ ] You say what the toy does not show
- [ ] You finish the talk in 5 minutes on a timer

**Arabic is optional.** If you want to build or present your product in Arabic, use Quantabic for the terms: start with the glossary cell at the end of section 3, which follows Quantabic's terms. If a term is not in the glossary, check quantabic.com, and if it is not there either, give the English in brackets the first time. Keep gate letters, kets and symbols in Latin (H, |0⟩, θ). The words are yours: mentors can check your physics, but they will not write your Arabic.'''

GLOSSARY_COMMON = [
    ("Qubit", "كيوبت", "G"), ("Superposition", "التراكب", "G"), ("Entanglement", "التشابك", "G"),
    ("Measurement", "القياس", "G"), ("Amplitude", "السعة", "G"), ("Phase", "الطور", "U"),
    ("Quantum circuit", "الدائرة الكمومية", "U"), ("Quantum gate", "البوابة الكمومية", "U"),
    ("Hadamard gate", "بوابة هادامارد", "G"), ("Quantum algorithm", "خوارزمية كمومية", "U"),
    ("Quantum simulator", "المحاكي الكمومي", "I"), ("Classical bit", "البت الكلاسيكي", "I"),
    ("Quantum speedup (quadratic / exponential)", "تسريع تربيعي / أسي", "U"),
]

# Proposed (tier I) renderings from plan section 2.8; notebooks pick the ones they need with glossary_rows(...).
GLOSSARY_BANK = {
    "Hamiltonian": ("مؤثر هاملتون (الهاملتوني)", "G"), "ground state": ("الحالة الأرضية", "I"),
    "expectation value": ("القيمة المتوقعة", "I"), "cost function": ("دالة التكلفة", "I"),
    "optimization": ("التحسين (الأمثَلة)", "I"), "ansatz": ("الافتراض المبدئي (ansatz)", "G"),
    "oracle": ("العرّاف (oracle)", "I"), "VQE": ("محلّل القيم الذاتية الكمومي التغايري (VQE)", "G"),
    "QAOA": ("خوارزمية الأمثلة الكمومية التقريبية (QAOA)", "G"), "Grover's algorithm": ("خوارزمية جروفر", "G"),
    "amplitude amplification": ("تضخيم السعة", "I"), "quantum kernel": ("النواة الكمية", "G"),
    "feature map": ("خريطة السمات", "I"), "support vector machine": ("آلة المتجهات الداعمة", "I"),
    "interference": ("التداخل", "G"), "noise": ("الضوضاء", "G"), "shots": ("عدد مرات التشغيل (shots)", "I"),
    "fault-tolerant": ("التسامح مع الخطأ", "G"),
}

GLOSSARY_INTRO = ('**Glossary — المصطلحات.** Tier G = Quantabic headword, U = used consistently on Quantabic, '
                  'I = proposed here and not yet checked against quantabic.com. Where Quantabic has a term, we use it.')

IBM_MD = '''### Optional: how this would go to a real IBM Quantum computer
This is a sketch and has not been checked against the current IBM documentation. Nothing here runs in this notebook.

```python
# Not run here. Needs: pip install qiskit-ibm-runtime, and an IBM Quantum account saved on your own machine.
# from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
# from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
# service = QiskitRuntimeService()                      # reads credentials saved earlier; never paste a token in a notebook
# backend = service.least_busy(operational=True, simulator=False)
# isa = generate_preset_pass_manager(optimization_level=3, backend=backend).run(circuit)
# job = Sampler(mode=backend).run([isa], shots=4096)
```

The next cell does the offline part: it transpiles your circuit for a *pretend* device on this computer and reports its size. Nothing is sent to IBM Quantum.'''

IBM_PREVIEW_CODE = '''preview = qff.quantum.device_preview(circuit)      # `circuit` = the main circuit of this notebook; runs locally
print(f"depth {preview['depth']}, two-qubit gates {preview['two_qubit_gates']}")'''


# ---------------------------------------------------------------------------------------------------------------------
# Functions used by tools/nbkit.py and the build scripts
# ---------------------------------------------------------------------------------------------------------------------
def header_md(n, title, ar, stop_en, use_case, algorithm, qubits, minutes):
    """Title block and summary table at the top of a notebook."""
    return HEADER_MD.format(n=n, title=title, ar=ar, stop_en=stop_en, use_case=use_case,
                            algorithm=algorithm, qubits=qubits, minutes=minutes)


def section0_md():
    """The shared 'day so far' text."""
    return SECTION0_MD


def section0_code(stop, challenge):
    """Code for the stop-map cell: lights `stop` and rings `challenge`."""
    return (f"from qff.day import show_day\n"
            f"show_day(stop={stop}, challenge={challenge})")


def section5_md(use_case, counting_fact, single_idea, ideas, reuse):
    """Section 5 with the bracketed parts filled in. `ideas` may be a list of strings or one preformatted string."""
    if not isinstance(ideas, str):
        ideas = "\n".join(f"{i}. {t}" for i, t in enumerate(ideas, 1))
    return SECTION5_MD.format(use_case=use_case, counting_fact=counting_fact,
                              single_idea=single_idea, ideas=ideas, reuse=reuse)


def section6_md(honest, qa, qb):
    """Section 6 with the bracketed parts filled in."""
    return SECTION6_MD.format(honest=honest, qa=qa, qb=qb)


def glossary_rows(extra=()):
    """The common glossary rows plus extra terms.

    Each item in `extra` is either an English name found in GLOSSARY_BANK, or a ready-made (english, arabic, tier) tuple.
    A term whose English name is already in the table is skipped, so nothing appears twice.
    """
    rows = list(GLOSSARY_COMMON)
    seen = {r[0].lower() for r in rows}
    for t in extra:
        if isinstance(t, tuple):
            en, ar, tier = t
        else:
            en = t
            ar, tier = GLOSSARY_BANK[t]
        if en.lower() not in seen:
            rows.append((en, ar, tier))
            seen.add(en.lower())
    return rows


def glossary_md(extra=()):
    """The glossary cell as a Markdown table."""
    lines = [GLOSSARY_INTRO, "", "| English | العربية | Tier |", "|---|---|---|"]
    lines += [f"| {en} | {ar} | {tier} |" for en, ar, tier in glossary_rows(extra)]
    return "\n".join(lines)


def ibm_md():
    """The optional IBM cell text (nbkit reads IBM_MD directly; kept for convenience)."""
    return IBM_MD