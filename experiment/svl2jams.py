#!/usr/bin/env python
"""
Converts an svl file into a JAMS annotation
"""

__author__      = "Oriol Nieto"
__copyright__   = "Copyright 2014, Music and Audio Research Lab (MARL)"
__license__     = "GPL"
__version__     = "1.0"
__email__       = "oriol@nyu.edu"

import argparse
import logging
import os
import time
import json
import xml.etree.ElementTree as ET

import jams


def create_annotation(root, annotator_id, jam_file):
    """Creates an annotation from the given root of an XML svl file."""

    # Load jam file
    jam = jams.load(jam_file)

    # Make sure annotation doesn't already exists
    for section in jam.sections:
        if section.annotation_metadata.annotator == annotator_id:
            return

    # Create Annotation
    annot = jam.sections.create_annotation()

    # Create Metadata
    annot.annotation_metadata.annotator = annotator_id
    # TODO: More metadata

    # Get sampling rate from XML root
    sr = float(root.iter("model").next().attrib["sampleRate"])

    # Create datapoints from the XML root
    points = root.iter("point")
    point = points.next()
    start = float(point.attrib["frame"]) / sr
    label = point.attrib["label"]
    for point in points:
        section = annot.create_datapoint()
        section.start.value = start
        section.end.value = point.attrib["frame"]
        section.label.value = label
        section.label.context = ""  # TODO: Add context!
        start = point.attrib["frame"]
        label = point.attrib["label"]

    # Save file
    with open(jam_file, "w") as f:
        json.dump(jam, f, indent=2)


def process(in_file, annotator_id, out_file="output.jams"):
    """Main process to convert an svl file to JAMS."""
    # Make sure that the jams exist (we simply have metadata there)
    assert(os.path.isfile(out_file))

    # Parse svl file (XML)
    tree = ET.parse(in_file)
    root = tree.getroot()

    # Create Annotation
    create_annotation(root, annotator_id, out_file)


def main():
    """Main function to convert the annotation."""
    parser = argparse.ArgumentParser(description=
        "Converst a Sonic Visualizer annotation into a JAMS.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("in_path",
                        action="store",
                        help="Input dataset")
    parser.add_argument("annotator_id",
                        action="store",
                        help="Identifier of the annotator (e.g. Collin, "
                        "Ferran")
    parser.add_argument("-o",
                        action="store",
                        dest="out_file",
                        help="Output file",
                        default="output.jams")
    args = parser.parse_args()
    start_time = time.time()

    # Setup the logger
    logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s',
                        level=logging.INFO)

    # Run the algorithm
    process(args.in_path, args.annotator_id, args.out_file)

    # Done!
    logging.info("Done! Took %.2f seconds." % (time.time() - start_time))

if __name__ == '__main__':
    main()