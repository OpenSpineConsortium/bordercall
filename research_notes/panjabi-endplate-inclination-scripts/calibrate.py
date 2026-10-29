"""Panjabi's end-plate inclinations set beside Tan 2004's, region by region.

The thoracic rows of Panjabi (1991t Table 3, p. 892) are not in dispute, so their gap from
Tan's magnitudes says how far two honest same-definition series sit apart; the disputed row
(1991c Table 2 p. 863 = 1992 Table 2 p. 301) is then set beside Tan's cervical and lumbar
magnitudes. Values typed from the page images; Tan from its text layer (pp. 140-141).
"""
import math

ROW_U = [2.7, 3.5, 1.7, 4.7, 2.2]
ROW_L = [4.0, 2.1, 2.7, 2.7, 1.8]
P_T_U = [1.8, 1.7, 2.4, 1.5, 2.1, 2.1, 1.6, 1.3, 0.9, 0.5, 2.3, 2.2]
P_T_L = [3.9, 1.9, 2.1, 2.3, 2.0, 1.8, 2.2, 2.3, 1.2, 1.2, 2.2, 1.8]
TAN = {
    "C": ([5.0, 5.2, 7.1, 5.8, 5.8], [3.3, 3.5, 2.7, 4.2, 5.1]),
    "T": ([7.2, 3.9, 3.2, 1.5, 1.4, 1.0, 2.1, 2.2, 1.6, 1.4, 3.4, 4.5],
          [-2.9, -3.0, -1.8, -4.1, -2.6, -3.8, -3.2, -2.2, -2.6, -3.0, -3.2, -3.1]),
    "L": ([1.8, 3.4, 1.9, 3.7, 6.9], [-2.6, -1.1, 1.8, 3.2, 10.5]),
}


def gaps(p, t):
    return [round(a - abs(b), 2) for a, b in zip(p, t)]


def summary(name, d):
    rms = math.sqrt(sum(x * x for x in d) / len(d))
    print("%-22s gaps %s  mean %+.2f  rms %.2f  max|gap| %.1f" % (name, d, sum(d) / len(d), rms, max(map(abs, d))))


summary("thoracic upper", gaps(P_T_U, TAN["T"][0]))
summary("thoracic lower", gaps(P_T_L, TAN["T"][1]))
summary("thoracic T2-T12 upper", gaps(P_T_U[1:], TAN["T"][0][1:]))
summary("row as C3-C7 upper", gaps(ROW_U, TAN["C"][0]))
summary("row as C3-C7 lower", gaps(ROW_L, TAN["C"][1]))
summary("row as L1-L5 upper", gaps(ROW_U, TAN["L"][0]))
summary("row as L1-L5 lower", gaps(ROW_L, TAN["L"][1]))
summary("row as L1-L4 upper", gaps(ROW_U[:4], TAN["L"][0][:4]))
summary("row as L1-L4 lower", gaps(ROW_L[:4], TAN["L"][1][:4]))
# the plates' sum (Panjabi's thoracic wedge) beside Tan's signed difference, lower minus upper
pt = [u + l for u, l in zip(P_T_U, P_T_L)]
tt = [l - u for u, l in zip(*TAN["T"])]
print("thoracic EPIt (sum)", pt, "mean %.2f" % (sum(pt) / 12))
print("Tan thoracic lower-upper", [round(x, 1) for x in tt], "mean %.2f" % (sum(tt) / 12))
