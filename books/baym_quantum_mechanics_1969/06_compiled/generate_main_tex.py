#!/usr/bin/env python3
"""Generates the master baym_qm_1969.tex from all .tex chunks."""
import os
import glob

BOOK_ROOT = os.path.join(os.path.dirname(__file__), '..')  # books/baym_qm.../
TEX_DIR   = os.path.join(BOOK_ROOT, '04_final_tex')
FIG_DIR   = os.path.join(BOOK_ROOT, '05_figures')
OUT_TEX   = os.path.join(BOOK_ROOT, '06_compiled', 'baym_qm_1969.tex')

tex_files = sorted(glob.glob(os.path.join(TEX_DIR, '*.tex')))

preamble = r"""\documentclass[11pt,twoside,openright]{book}
\usepackage[utf8]{inputenc}
\usepackage{amsmath,amssymb,amsfonts,amsthm}
\usepackage{graphicx}
\usepackage[hidelinks]{hyperref}
\usepackage{geometry}
\usepackage{url}
\geometry{a4paper, margin=1in}
\graphicspath{{../05_figures/raw/}{../05_figures/enhanced/}}

% --- Canonical Notation Macros (from config/macros.tex) ---
\newcommand{\ket}[1]{|#1\rangle}
\newcommand{\bra}[1]{\langle #1|}
\newcommand{\braket}[2]{\langle #1|#2\rangle}
\newcommand{\ev}[2][]{\langle #1|#2|#1\rangle}
\newcommand{\comm}[2]{[#1,\,#2]}
\newcommand{\acomm}[2]{\{#1,\,#2\}}
\newcommand{\dd}{\mathrm{d}}
\newcommand{\ii}{\mathrm{i}}
\newcommand{\ee}{\mathrm{e}}
\newcommand{\tr}{\operatorname{Tr}}
\newcommand{\slashed}[1]{#1\!\!\!/}
\newcommand{\abs}[1]{\left|#1\right|}
\newcommand{\norm}[1]{\left\|#1\right\|}
% Operator hat shorthand
\newcommand{\op}[1]{\hat{#1}}

\title{\textbf{Lectures on Quantum Mechanics}\\[0.5em]
       \large Modernized Digital Edition}
\author{Gordon Baym\\[0.3em]
        \small Original: W.A.\ Benjamin, 1969 (3rd printing, 1974)\\
        \small Recompiled by Agentic Ingestion Pipeline, 2026}
\date{}

\begin{document}
\frontmatter
\maketitle
\tableofcontents
\mainmatter

"""

FRONTMATTER_FILES = [
    '00_05_PREFACE.tex',
]

# Chapters: detect by _00_ chunk
chapter_defs = {
    '01': 'Photon Polarization',
    '02': 'Neutral K Mesons',
    '03': 'The Motion of Particles in Quantum Mechanics',
    '04': 'Potential Problems, Mostly in One Dimension',
    '05': 'Equations of Motion for Operators',
    '06': 'Orbital Angular Momentum and Central Potentials',
    '07': 'The Hydrogen Atom',
    '08': 'Cooper Pairs',
    '09': 'Potential Scattering',
    '10': 'Coulomb Scattering',
    '11': 'Stationary State Perturbation Theory',
    '12': 'Time-Dependent Perturbation Theory',
    '13': 'Interaction of Radiation with Matter',
    '14': r'Spin $\tfrac{1}{2}$',
    '15': 'Addition of Angular Momenta',
    '16': 'Isotopic Spin',
    '17': 'Rotations and Tensor Operators',
    '18': 'Identical Particles',
    '19': 'Second Quantization',
    '20': 'Atoms',
    '21': 'Molecules',
    '22': r'Relativistic Spin-Zero Particles: Klein--Gordon Equation',
    '23': r'Relativistic Spin-$\tfrac{1}{2}$ Particles: Dirac Equation',
}

# Exclude artifact/duplicate/corrupt files
EXCLUDE = {
    '00_01_LECTURES_ON_QUANTUM_MECHANICS.tex',
    '00_02_LECTURES_ON_QUANTUM_MECHANICS.tex',
    '00_03_LECTURE_NOTES_AND_SUPPLEMENTS_IN_PHYSICS.tex',
    '00_04_LECTURES_ON_QUANTUM_MECHANICS.tex',
    '00_06_CONTENTS.tex',
    '00_07_CONTENTS_ix.tex',
    '23_01_CONTENTS_xi.tex',       # publisher page artifact
    '22_00_Relativistic_Spin_Zero_Particles.tex',   # duplicate overview
    '23_00_Relativistic_Spin_Vz_Particles_Dirac_Equation_534.tex',  # duplicate
    '06_08_Chapter_7.tex',         # empty chapter-start artifact
}

with open(OUT_TEX, 'w') as f:
    f.write(preamble)

    # Frontmatter
    f.write('\\chapter*{Preface}\n')
    f.write('\\addcontentsline{toc}{chapter}{Preface}\n')
    preface = os.path.join(TEX_DIR, '00_05_PREFACE.tex')
    if os.path.exists(preface):
        f.write(f'\\input{{{preface}}}\n\n')

    last_chapter = None
    for tex in tex_files:
        basename = os.path.basename(tex)
        if basename in EXCLUDE:
            continue

        # Detect chapter prefix
        prefix = basename[:2]
        if prefix.isdigit() and prefix != '00':
            if prefix != last_chapter:
                chap_title = chapter_defs.get(prefix, f'Chapter {int(prefix)}')
                f.write(f'\\chapter{{{chap_title}}}\n')
                last_chapter = prefix

            # Skip _00_ intro files (already inserted by chapter command)
            if '_00_' in basename:
                continue

        f.write(f'\\input{{{tex}}}\n')

    f.write('\n\\backmatter\n')
    f.write('\\input{' + os.path.join(TEX_DIR, '23_12_INDEX.tex') + '}\n')
    f.write('\n\\end{document}\n')

print(f"Generated: {OUT_TEX}")
