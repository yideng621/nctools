#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Converts lines and arcs from a DXF file and prints them.
#
# Copyright © 2011,2012 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# $Date$
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

import sys 
import os.path
import cairo
import dxfgeom

__proginfo__ = ('dxf2pdf [ver. ' + '$Revision$'[11:-2] +
                '] ('+'$Date$'[7:-2]+')')

def outname(inname):
    """Creates the name of the output filename based on the input filename.

    :inname: name + path of the input file
    :returns: output file name.
    """
    rv = os.path.splitext(os.path.basename(inname))[0]
    if rv.startswith('.') or rv.isspace():
        raise ValueError("Invalid file name!")
    return rv + '_dxf.pdf'


def main(argv):
    """Main program for the readdxf utility.
    
    :argv: command line arguments
    """
    if len(argv) == 1:
        print __proginfo__
        print "Usage: {} dxf-file(s)".format(sys.argv[0])
        exit(1)
    del argv[0]
    for f in argv:
        try:
            ofn = outname(f)
            entities = dxfgeom.fromfile(f)
        except ValueError as e:
            print e
            fns = "Cannot construct output filename. Skipping file '{}'."
            print fns.format(f)
            continue
        except IOError as e:
            print e
            print "Cannot open the file '{}'. Skipping it.".format(f)
            continue
        # Output
        bb = entities[0].getbb()
        for e in entities:
            bb = dxfgeom.merge_bb(bb, e.getbb())
        # bb = xmin, ymin, xmax, ymax
        w = bb[2] - bb[0] + 20
        h = bb[3] - bb[1] + 20
        xf = cairo.Matrix(xx=1.0, yy=-1.0, y0=h)
        out = cairo.PDFSurface(ofn, w, h)
        ctx = cairo.Context(out)
        ctx.set_matrix(xf)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_line_width(0.5)
        # Plot a grid in red
        ctx.save()
        ctx.new_path()
        for x in xrange(100, int(w), 100):
            ctx.move_to(x, 0)
            ctx.line_to(x, h)
        for y in xrange(int(h)-100, 0, -100):
            ctx.move_to(0, y)
            ctx.line_to(w, y)
        ctx.close_path()
        ctx.set_line_width(0.25)
        ctx.set_source_rgb(1, 0, 0)
        ctx.stroke()
        ctx.restore()
        # plot the lines and arcs
        ctx.translate(10-bb[0], 10-bb[1])
        ctx.new_path()
        # draw the arcs first, or the last arc will have an artefact
        # because of the ctx.close_path() that is called after it.
        arcs = [e for e in entities if isinstance(e, dxfgeom.Arc)]
        for a in arcs:
            p = a.pdfdata()
            ctx.new_sub_path()
            ctx.arc(*p)
        lines = [e for e in entities if isinstance(e, dxfgeom.Line)]
        for l in lines:
            s, e = l.pdfdata()
            ctx.move_to(*s)
            ctx.line_to(*e)
        ctx.close_path()
        ctx.stroke()
        out.show_page()
        out.finish()


if __name__ == '__main__':
    main(sys.argv)

