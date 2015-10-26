#!/usr/bin/env python

"""
Read an incoming MARC21 file and output CSV-delimited summary
data about the subject tags for later analysis.
"""

import argparse
import codecs
import csv

from pymarc import XmlHandler, parse_xml


class ExtractXmlHandler(XmlHandler):
    """Stream-oriented record handler."""

    def __init__(self, writer):
        XmlHandler.__init__(self)
        self._writer = writer

    def process_record(self, record):
        # In our data set, our records had their 001s replaced with
        # OCLC numbers; our local identifiers were stashed in 951$a.
        # But some records lack a 951$a, so skip them for now.  The
        # count of those is very small.
        try:
            d = {'bibid': record['951']['a']}
        except:
            return
        # Otherwise, extract a row with local id, tag, indicators,
        # subfields present, and $2 for each subject, e.g.:
        #   2127216,650,1,7,a2,gtt
        #   3211132,650, ,7,ax2,ram
        #   3234100,651, ,7,a20,fast
        for subj in record.subjects():
            d['tag'] = subj.tag
            d['i1'] = subj.indicators[0]
            d['i2'] = subj.indicators[1]
            d['subfields'] = ''.join(subj.subfields[::2])
            if '2' in d['subfields']:
                idx = subj.subfields.index('2')
                d['sf2'] = subj.subfields[idx + 1]
            else:
                d['sf2'] = ''
            self._writer.writerow(d)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('input_file', help='path to input file')
    p.add_argument('output_file', help='path to output file')
    return p.parse_args()


if __name__ == '__main__':
    args = parse_args()
    fieldnames = ['bibid', 'tag', 'i1', 'i2', 'subfields', 'sf2']
    with codecs.open(args.output_file, 'wb', 'utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        # writer.writeheader()
        reader = parse_xml(args.input_file, ExtractXmlHandler(writer))
