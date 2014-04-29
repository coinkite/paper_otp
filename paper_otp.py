#!/usr/bin/env python
#
# Copyright (c) 2014 by Coinkite Inc.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# 
# 
# Original Author: Peter D. Gray (@dochex)
#
# Manage a single-page PDF containing single-use numeric tokens. The tokens
# are generated using the RFC6238 algorithm with the X/Y coordinate as
# the interval number. The "secret" seed values used here are base32-encoded
# strings of length 16.
#
# When deploying this, it's important to never use the same code twice. It's 
# probably best to pick randomly from the set of codes you've never asked for.
# 

import os, random
from onetimepass import get_hotp
import pdb

# Card is a 10x10 grid, A1 is top left corner, B1 is next etc to K0 at bottom right
X_COORDS = 'ABCDEFGHJK'
NUM_CODES = 100


def xy_to_num(xy):
    "convert A5 into number from zero to NUM_CODES"
    assert len(xy) == 2, xy
    x,y = xy

    x = x.upper()
    y = int(y)

    assert x in X_COORDS, x
    assert 0 <= y <= 9, y

    return X_COORDS.find(x) + (((10 + y - 1) % 10)*10)

def num_to_xy(num):
    assert 0 <= num < NUM_CODES, num
    x = X_COORDS[num % 10]
    return '%s%d' % (x, ((num/10)+1) % 10)

def calc_values(secret):
    return [get_hotp(secret, i, as_string=True) for i in range(NUM_CODES)]

def valid_guess_xy(secret, coord, guess):
    # test if correct answer given
    num = xy_to_num(coord)
    return get_hotp(secret, num) == int(guess)

def text_version(secret):
    values = calc_values(secret)
    
    rv = []
    rv.append('    ' + ''.join(['   %s   ' % X_COORDS[x] for x in range(10)]))

    for y in range(10):
        l = '  %d  ' % ((y+1)%10)
        for x in range(10):
            l += values[x+(10*y)] + ' '
        rv.append(l)

    return rv

def modulate(values):
    # for each string of values (a list), split into two areas; always 3 + 3 digits
    a,b = [], []
    for v in values:
        here = random.sample(range(6), 3)
        a.append(''.join([(' ' if n not in here else i) for n,i in enumerate(v)]))
        b.append(''.join([(' ' if n in here else i) for n,i in enumerate(v)]))

    return a, b
    
def genpdf(pdf_file, secret, example=False):
    # Make a PDF file containing the key
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import cm, inch
    from reportlab.lib.enums import TA_CENTER

    if 0:
        # This works fine, but could not find a BOLD, fixed-width, 7-segment display font that 
        # was free for commerical.
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        font_file = os.path.realpath(__file__+'/../numbers-font.ttf')
        pdfmetrics.registerFont(TTFont("Numbers", font_file))  

    # split into top and bottom halfs of numbers
    values = calc_values(secret) if not example else (['123123'] * NUM_CODES)
    valuesT, valuesB = modulate(values)

    style = TableStyle([    # (col,row) here
                # center all cells
                ('ALIGN', (0,0), (10,10), 'CENTER'),
                ('VALIGN', (0,0), (10,10), 'MIDDLE'),
                ('INNERGRID', (0,0), (10,10), 1, (0,0,0)),
                # larger headers
                ('FONTNAME', (0,0), (10,0), 'Helvetica-Bold'),
                ('FONTNAME', (0,0), (0,10), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (10,0), 18),
                ('FONTSIZE', (0,0), (0,10), 18),
                ('LEADING', (0,0), (10,0), 18+2),
                ('LEADING', (0,0), (0,10), 18+2),

                # fine tune positiing of header line
                ('BOTTOMPADDING', (0,0), (10,0), 8),
                # .. left edge
                ('TOPPADDING', (0,0), (0,10), 1),
                ('BOTTOMPADDING', (0,0), (0,10), 4),

                # codes in fixed-width font
                ('FONTNAME', (1,1), (10,10), 'Courier-Bold'),
                #('FONTNAME', (1,1), (10,10), 'Numbers'),
            ])

    # This table will draw upside down and mirrow imaged
    class MirrorTable(Table):
        def draw(self):
            c = self.canv
            c.rotate(180)
            c.scale(-1, 1)
            c.translate(0, -self._height)
            Table.draw(self)

    # fold here line
    txt = ('-  '*20) + '    fold    ' + ('  -' *20)
    fold = Paragraph(txt, ParagraphStyle('style-name',
                fontName = 'Helvetica', alignment=TA_CENTER,
                spaceBefore = 0.15*inch,
                spaceAfter = 0.15*inch,
            ))

    doc = SimpleDocTemplate(pdf_file)

    hdr = [' '] + [X_COORDS[x] for x in range(10)]
    rowsT, rowsB = [hdr], [hdr]

    for y in range(10):
        rowsT.append([str((y+1) % 10)] + [valuesT[i] for i in range((y*10), (y*10)+10)])
        rowsB.append([str((y+1) % 10)] + [valuesB[i] for i in range((y*10), (y*10)+10)])

    table = Table(rowsT, style=style)
    table2 = MirrorTable(rowsB, style=style)

    elements = []
    elements.append(table)
    elements.append(fold)
    elements.append(table2)
    doc.build(elements) 

def selftest():
    for i in range(NUM_CODES):
        xy = num_to_xy(i)
        assert xy_to_num(xy) == i, (xy, i, xy_to_num(xy))

    #print calc_values('a'*16)
    print '\n'.join(text_version('a'*16))

if __name__ == "__main__":
    selftest()
    genpdf(file('test.pdf', 'w'), 'a'*16, example=False)

# EOF 
