# eBCSgen

eBSCgen is a tool for development and analysis of models written in Biochemical Space Language (BCSL). The tool is deployed online as a part of [BioDivine](https://biodivine-vm.fi.muni.cz/galaxy/) toolset. 

For more information about the tool, see Wiki.

---

If you want to run the tool locally, make sure you have `Python 3+` installed with the following packages: `pandas`, `numpy`, `scipy`, `lark`, `lark-parser`, `sympy`, `itertools`, `collections`, `requests` (all installable using `pip`).

To test the tool, run `python3 Testing/main.py` in the main directory.

> In some older Python versions the test is not working, run `python3 -m unittest discover -s Testing -p 'test_*.py'` instead.
