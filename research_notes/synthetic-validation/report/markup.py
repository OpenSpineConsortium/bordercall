"""The markdown helpers the two report pages share: inline marks, the README's blocks and a
figure's caption. Nothing here computes a number."""
import html
import os
import re

NOTE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    return s


def blocks(body):
    """The README's markdown for the two prose sections kept: paragraphs, lists and code; a marked
    table is left out, since the tables live in the README."""
    out, para, lst, code = [], [], [], None
    skip = False

    def flush_para():
        if para:
            out.append("<p>%s</p>" % inline(" ".join(x.strip() for x in para)))
            para.clear()

    def flush_list():
        if lst:
            tag = "ol" if lst[0][0] == "ol" else "ul"
            out.append("<%s>%s</%s>" % (tag, "".join("<li>%s</li>" % inline(t) for _, t in lst), tag))
            lst.clear()

    for l in body.split("\n"):
        if code is not None:
            if l.startswith("```"):
                out.append("<pre><code>%s</code></pre>" % html.escape("\n".join(code)))
                code = None
            else:
                code.append(l)
            continue
        if l.startswith("<!-- table"):
            flush_para(); flush_list(); skip = True; continue
        if l.startswith("<!-- end"):
            skip = False; continue
        if skip:
            continue
        if l.startswith("```"):
            flush_para(); flush_list(); code = []; continue
        if not l.strip():
            flush_para(); flush_list(); continue
        m = re.match(r"^(\d+)\.\s+(.*)$", l)
        b = re.match(r"^-\s+(.*)$", l)
        if m:
            flush_para(); lst.append(("ol", m.group(2))); continue
        if b:
            flush_para(); lst.append(("ul", b.group(1))); continue
        if lst and l.startswith("  "):
            lst[-1] = (lst[-1][0], lst[-1][1] + " " + l.strip()); continue
        para.append(l)
    flush_para(); flush_list()
    return "\n".join(out)


def caption(name):
    return open(os.path.join(NOTE, "figures", name + ".caption.txt")).read().strip()
