# Goal: to make a simple command-line application that does binary to decimal, and vice-versa, conversions for IP addressing
# Author: @voiding

import argparse
parser = argparse.ArgumentParser()

parser.add_argument("address",
                    help="The 32-bit IPv4 address to convert with \
                          the usual delimiting dot separating each octet. \
                          You can use binary or decimal notation")

parser.add_argument("-v", "--verbose",
                    action="store_true", 
                    help="Display procedural results of the conversion")

args = parser.parse_args() # Defaults to a list-like Namespace object containing kv pairs of arguments passed to script call
octets = args.address.split(".") # args.address is a string of what the user typed in at the prompt

def is_ipv4(ip): # Takes list of strings of octets read in from stdin

    # IPv4 addresses have 4 relatively straightforward octets - not dealing with IPv6 at the moment
    # Check if it is a correctly formed IPv4 address. If not, return an appropriate message and error code
    if len(ip) > 4: 
        return ("Your address is too large. Did you put an extra octet?", 1) # Exit status code
    
    elif len(ip) < 4: 
        return (f"Your address is too small. Expected 4 octets, got {len(ip)} instead", 2)
    
    else: return ("Address OK", 0)

def check_ip_integrity(ip):
    # If IP length is not exactly 4 octets, exit early
    message, status_code = is_ipv4(ip)

    if status_code != 0: # Return value
        print(message)
        return status_code
    else:
        if args.verbose: print(message) # Affirmative message is not an error message so it won't be shown unless the verbosity option is enabled

    octet_lengths = []

    for index, octet in enumerate(ip):
        # Check if it's binary or decimal first
        # How?
        # Length!

        # Keep track of octet lengths
        
        octet_lengths.append(len(octet))

        if len(octet) == 8: # Binary notation

            # Verbose mode: diplay info message
            if args.verbose: print(f"Octet {index + 1}: Length {len(octet)}, presuming binary")

            # Loop over each bit in the string
            for bit in octet:
                # Check if the bits are either 1 or 0
                if bit == "0" or bit == "1":
                    # Verbose mode: display info message
                    if args.verbose: print(f"OK: Found a bit of value {bit}")
                    # Go ahead with the next iteration
                    continue
                else:
                    # Inform the user they entered an invalid byte string 
                    print(f"Invalid binary: Found a bit of value {bit} in octet {index + 1}, exiting...")
                    # Terminate loop at first occurrence and exit
                    return 4
        elif 1 <= len(octet) <= 3: # Decimal notation
            try:
                if int(octet) > 255: # Decimal octets cannot be greater than 255 (2^7 or 11111111)
                    print(f"Invalid decimal: Octet {index + 1} is greater than 255")
                    return 5
                elif int(octet) < 0:
                    print(f"Invalid decimal: Octet {index + 1} is less than 0")
                    return 6
                else:
                    if args.verbose: print(f"OK: Octet {index + 1}, value {octet}")
            except ValueError:
                print(f"Is your octet, {octet}, a valid numeric string?")
        else: 
            print(f"Don't know what {octet} (octet {index + 1}) is, exiting...")
            return 7
        
    # At this point octet_lengths should be [1, 1, 1, 1] = 4 (summed) for an address like 1.1.1.1 where all octets represent 1 decimal number each
    # [10, 0, 0, 255] = [2, 1, 1, 3]
    # To a maximum of [3, 3, 3, 3] = 12 (summed) 
    # Whereas, binary is 8*4 or 32 summed ([8, 8, 8, 8])

    # Descending 2^7 down to 2^0
    # (exponent, positional value) format
    binary_pos_value = ((7,128), (6,64), (5,32), (4,16), (3,8), (2,4), (1,2), (0,1)) 

    # Init list for /new/ IP
    converted_ip = [] 

    if 4 <= sum(octet_lengths) <= 12: # It's decimal, return binary conversion
        for octet in ip:
            octet = int(octet)   # Convert octet to an integer for arithmetic purposes
            converted_octet = "" # Init empty binary octet
            for value in binary_pos_value:
                if octet >= value[1]:
                    if args.verbose: print(f"{octet} is greater than or equal to the positional value of {value[1]} (2^{value[0]}), therefore the bit representation is 1")
                    converted_octet += "1"
                    if args.verbose: print(f"{octet} - {value[1]} = {octet - value[1]}")
                    octet -= value[1]
                else:
                    if args.verbose: print(f"{octet} is less than the positional value of {value[1]} (2^{value[0]}), therefore the bit representation is 0")
                    converted_octet += "0"
            converted_ip.append(converted_octet)
        print("Binary IPv4 address:", ".".join(converted_ip))

    elif sum(octet_lengths) == 32: # It's binary, return decimal
        for octet in ip:
            binary_to_decimal = int(octet, base=2)      # Converts a base2 string, i.e. bits, into a base10 integer
            if args.verbose: print(f"{octet} is {binary_to_decimal} in base10")
            converted_ip.append(str(binary_to_decimal)) # Turn it back into a string and append it to the empty IP container, makes it easier to string back together in a moment
        print("Dotted decimal IPv4 address:", ".".join(converted_ip))
                    
check_ip_integrity(octets)