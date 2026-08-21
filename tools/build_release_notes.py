"""Canonical releases/release_notes/<v>.md -> documentation-repo PDF.

Only transform: strip internal SR-####: / (PR #####): bullet prefixes,
per documentation-repo precedent 684de47. Nothing added or reworded.
Usage: build_notes.py <src_md_dir> <dest_dir> <version>...
"""
import os, re, sys, html
from reportlab import rl_config
# Deterministic output: fixes /CreationDate, /ModDate and the trailer /ID so the
# same release notes always produce byte-identical PDFs and can be re-verified.
rl_config.invariant = 1
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph

TITLE = ParagraphStyle('t', fontName='Times-Bold', fontSize=24, leading=28,
                       alignment=TA_LEFT, spaceAfter=20, leftIndent=42)
META  = ParagraphStyle('m', fontName='Times-Roman', fontSize=11, leading=14, spaceAfter=12)
BODY  = ParagraphStyle('b', fontName='Times-Roman', fontSize=11, leading=14, spaceAfter=11)
HEAD  = ParagraphStyle('h', fontName='Times-Bold', fontSize=15.5, leading=19,
                       spaceBefore=14, spaceAfter=7)
BUL   = ParagraphStyle('u', fontName='Times-Roman', fontSize=10.5, leading=13.2,
                       leftIndent=15, firstLineIndent=-11, spaceAfter=2.5)
PREFIX = re.compile(r'^- (?:SR-\d+|\(PR #\d+\)):\s*')
INTRO1 = ("If you are not currently running SimpleRisk, please download the application and follow "
          "the installation instructions for your preferred method.")
INTRO2 = ("If you are running a previous release, navigate to <b>Configure &#8594; Register &amp; "
          "Upgrade</b> and click <b>Upgrade the Application</b>. This process upgrades both the "
          "application and the database to the latest release.")

def inline(s):
    s = s.replace('`', '')
    parts = [html.escape(p, quote=False) for p in s.split('**')]
    return ''.join(('<b>%s</b>' % p) if i % 2 else p for i, p in enumerate(parts))

def build(src, dest, version):
    raw = open(os.path.join(src, version + '.md'), encoding='utf-8').read().splitlines()
    path = os.path.join(dest, 'SimpleRisk Release Notes %s.pdf' % version)
    doc = SimpleDocTemplate(path, pagesize=letter,
                            leftMargin=1.15*inch, rightMargin=1.05*inch,
                            topMargin=1.5*inch, bottomMargin=1.0*inch,
                            title='SimpleRisk Release Notes %s' % version,
                            author='SimpleRisk', subject='SimpleRisk Release Notes')
    flow = [Paragraph('SimpleRisk Release Notes', TITLE),
            Paragraph('<b>Version:</b> %s' % version, META),
            Paragraph(INTRO1, BODY), Paragraph(INTRO2, BODY)]
    buls = stripped = 0
    for ln in (l.rstrip() for l in raw):
        if not ln or ln.startswith('# '):
            continue
        if ln.startswith('## '):
            flow.append(Paragraph(inline(ln[3:].strip()), HEAD))
        elif ln.startswith('- '):
            new = PREFIX.sub('- ', ln)
            if new != ln:
                stripped += 1
                b = new[2:]
                new = '- ' + (b[0].upper() + b[1:] if b and b[0].islower() else b)
            flow.append(Paragraph('&bull;&nbsp;&nbsp;' + inline(new[2:].strip()), BUL))
            buls += 1
    doc.build(flow)
    print('  %s : %d bullets, %d prefixes stripped, %d bytes'
          % (version, buls, stripped, os.path.getsize(path)))

if __name__ == '__main__':
    src, dest, versions = sys.argv[1], sys.argv[2], sys.argv[3:]
    for v in versions:
        build(src, dest, v)
