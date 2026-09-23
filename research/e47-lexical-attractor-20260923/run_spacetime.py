#!/usr/bin/env python3
"""Run all four attachment sections using the surveyed repository dependency.

Only the engine search path and output directory are relocated. Original
attachment and repository engine bytes remain archived under sources/.
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
os.environ.setdefault('MPLBACKEND','Agg')
from pathlib import Path
ROOT=Path(__file__).resolve().parent
source=ROOT/'sources/e47_spacetime_execute.py'
code=source.read_text()
old_engine='/home/workdir/.grok/skills/eidolon-propulsion/scripts'
old_output='/home/workdir/artifacts'
assert code.count(old_engine)==1 and code.count(old_output)==1
code=code.replace(old_engine,str(ROOT/'sources')).replace(old_output,str(ROOT/'results/spacetime'))
exec(compile(code,str(source),'exec'),{'__name__':'__main__','__file__':str(source)})
