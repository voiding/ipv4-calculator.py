# Modularize code by putting the large helper functions 
# into a separate file aside from main

# Takes list as strings of octets read in from stdin
def is_ipv4(parser_args, ip_address):

    # IPv4 addresses have 4 relatively straightforward octets - not dealing with IPv6 at the moment
    # Check if it is a correctly formed IPv4 address. If not, return an appropriate message and error code

    # Using status code convention I found at https://iifx.dev/en/articles/1055151
    # 2 indicating user error at prompt

    ip_length = len(ip_address)

    if ip_length > 4: 
        print("Your address is too large. Did you put an extra octet?")
        return 2
    elif ip_length < 4: 
        print(f"Your address is too small. Expected 4 octets, got {ip_length} instead")
        return 2
    else:
        # If it's well-formed, it is probably redundant to inform the user
        if parser_args.verbose:
            print("Address OK")
        return 0

# Parameters from left to right:
# - List-like object from the argparse module with the parsed args from the command line in it (used for checking if the verbosity option is toggled)
# - Where the octet is
# - What the octet is
# - How long it is (precalculated, probably could have just done the one-liner in the function but I didn't know which one would be more efficient, and I feel like it was pretty trivial anyway)
def verify_octet(parser_args, index, octet, octet_length):

        # Binary notation
        if octet_length == 8:

            # Verbose mode: display info message
            if parser_args.verbose: 
                print(f"Octet {index + 1}: Length {octet_length}, presuming binary")

            # Loop over each bit in the string
            for bit in octet:
                # Check if the bits are either 1 or 0
                if bit == "0" or bit == "1":
                    # Verbose mode: display info message
                    if parser_args.verbose: 
                        print(f"OK: Found a bit of value {bit}")

                    # Go ahead with the next iteration
                    continue
                else:
                    # Inform the user they entered an invalid byte string 
                    # Terminate loop at first occurrence and exit
                    return print(f"Invalid binary: Found a bit of value {bit} in octet {index + 1}, exiting...")

        # Decimal notation
        elif 1 <= octet_length <= 3:
            try:
                if int(octet) > 255: # Decimal octets cannot be greater than 255 (2^7 or 11111111)
                    return print(f"Invalid decimal: Octet {index + 1} is greater than 255")
                elif int(octet) < 0:
                    return print(f"Invalid decimal: Octet {index + 1} is less than 0")
                else:
                    if parser_args.verbose: 
                        print(f"OK: Octet {index + 1}, value {octet}")
            except ValueError:
                return print(f"Is your octet, {octet}, a valid numeric string?")
        
        # Invalid string fallthrough case
        else: 
            return print(f"Don't know what {octet} (octet {index + 1}) is, exiting...")
        
        return 0

def convert_ip(parser_args, ip_address, octet_lengths):
    # At this point lengths should be [1, 1, 1, 1] = 4 (summed) for an address like 1.1.1.1 where all octets represent 1 decimal number each
    # [10, 0, 0, 255] = [2, 1, 1, 3]
    # To a maximum of [3, 3, 3, 3] = 12 (summed) 
    # Whereas, binary is 8*4 or 32 summed ([8, 8, 8, 8])

    # Descending 2^7 down to 2^0
    # (exponent, positional value) format
    positional_value = ((7,128), (6,64), (5,32), (4,16), (3,8), (2,4), (1,2), (0,1)) 

    # Init list for /new/ IP
    converted_ip = [] 

    # It's decimal, return binary conversion
    if 4 <= sum(octet_lengths) <= 12:
        for octet in ip_address:
            octet = int(octet)   # Convert octet to an integer for arithmetic purposes
            converted_octet = "" # Init empty binary octet
            for value in positional_value:
                if octet >= value[1]:
                    if parser_args.verbose: 
                        print(f"{octet} is greater than or equal to the positional value of {value[1]} (2^{value[0]}), therefore the bit representation is 1")
                    converted_octet += "1"

                    if parser_args.verbose: 
                        print(f"{octet} - {value[1]} = {octet - value[1]}")
                    octet -= value[1]
                else:
                    if parser_args.verbose: 
                        print(f"{octet} is less than the positional value of {value[1]} (2^{value[0]}), therefore the bit representation is 0")
                    converted_octet += "0"
            converted_ip.append(converted_octet)

        print("Binary IPv4 address:", ".".join(converted_ip))

    # It's binary, return decimal
    elif sum(octet_lengths) == 32:
        for octet in ip_address:
            binary_to_decimal = int(octet, base=2) # Converts a base2 string, i.e. bits, into a base10 integer

            if parser_args.verbose: 
                print(f"{octet} is {binary_to_decimal} in base10")
            
            # Turn it back into a string and append it to the empty IP container, makes it easier to string back together
            converted_ip.append(str(binary_to_decimal)) 

        print("Dotted decimal IPv4 address:", ".".join(converted_ip))