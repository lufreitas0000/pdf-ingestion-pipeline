import os
import glob
import re

tex_files = sorted(glob.glob('data/07_final_tex/*.tex'))

preamble = r"""\documentclass[11pt,twoside,openright]{book}
\usepackage[utf8]{inputenc}
\usepackage{amsmath,amssymb,amsfonts,amsthm}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{geometry}
\geometry{a4paper, margin=1in}

\newcommand{\bra}[1]{\langle #1 |}
\newcommand{\ket}[1]{| #1 \rangle}
\newcommand{\braket}[2]{\langle #1 | #2 \rangle}
\newcommand{\ev}[1]{\langle #1 \rangle}
\newcommand{\tr}{\operatorname{Tr}}
\newcommand{\slashed}[1]{#1\!\!\!/}

\title{Lectures on Quantum Mechanics\\ \large Modernized Edition}
\author{Gordon Baym \\ \small Recompiled by Agentic Pipeline}
\date{\today}

\begin{document}
\maketitle
\tableofcontents

"""

with open('main.tex', 'w') as f:
    f.write(preamble)
    
    for tex in tex_files:
        basename = os.path.basename(tex)
        
        if "_00_" in basename:
            # e.g., 01_00_PHOTON_POLARIZATION.tex -> Photon Polarization
            title = basename.split("_00_")[-1].replace(".tex", "").replace("_", " ").title()
            f.write(f"\\chapter{{{title}}}\n")
        elif "Chapter_7" in basename:
            f.write(f"\\chapter{{The Hydrogen Atom}}\n")
            
        f.write(f"\\input{{{tex}}}\n")

    f.write("\n\\end{document}\n")

