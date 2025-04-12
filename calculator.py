# Goal: to make a simple command-line application that does binary to decimal, and vice-versa, conversions for IPv4 addressing
# Author: @voiding

import sys
import argparse
from core_utils import is_ipv4, verify_octet, convert_ip

parser = argparse.ArgumentParser()

parser.add_argument("address",
                    help="The 32-bit IPv4 address to convert with \
                          the usual delimiting dot separating each octet. \
                          You can use binary or decimal notation")

parser.add_argument("-v", "--verbose",
                    action="store_true", 
                    help="Display procedural results of the conversion")

args = parser.parse_args()

# Should be something like ["192", "168", "1", "1"]
ip_address = args.address.split(".") 

# Iteratively store length of octets, should be all 1s through all 3s for decimal and all 8 (8*4) for binary
# Used as a reference for performing the right calculation in future
octet_lengths = []

if __name__ == '__main__':
    status_code = is_ipv4(args, ip_address)

    # If IP length is not exactly 4 octets, exit early
    if status_code != 0:
        sys.exit(status_code)

    for index, octet in enumerate(ip_address):
        octet_length = len(octet)

        # Integer 0 as a final exit code if successful, else NoneType (just displays error message and returns)
        if verify_octet(args, index, octet, octet_length) == 0:
            octet_lengths.append(octet_length)
        else:
            sys.exit(2)

    convert_ip(args, ip_address, octet_lengths)