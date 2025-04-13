# Modularize code by putting the large helper functions 
# into a separate file aside from main
from tabulate import tabulate

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
                    print(f"Invalid binary: Found a bit of value {bit} in octet {index + 1}, exiting...")
                    return

        # Decimal notation
        elif 1 <= octet_length <= 3:
            try:
                if int(octet) > 255: # Decimal octets cannot be greater than 255 (2^7 or 11111111)
                    print(f"Invalid decimal: Octet {index + 1} is greater than 255")
                    return
                elif int(octet) < 0:
                    print(f"Invalid decimal: Octet {index + 1} is less than 0")
                    return
                else:
                    if parser_args.verbose: 
                        print(f"OK: Octet {index + 1}, value {octet}")
            except ValueError:
                print(f"Is your octet, {octet}, a valid numeric string?")
                return
        
        # Invalid string fallthrough case
        else: 
            print(f"Don't know what {octet} (octet {index + 1}) is, exiting...")
            return
        
        return 0

def convert_ip(parser_args, ip_address, octet_lengths):
    # At this point lengths should be [1, 1, 1, 1] = 4 (summed) for an address like 1.1.1.1 where all octets represent 1 decimal number each
    # [10, 0, 0, 255] = [2, 1, 1, 3]
    # To a maximum of [3, 3, 3, 3] = 12 (summed) 
    # Whereas, binary is 8*4 or 32 summed ([8, 8, 8, 8])

    conversion_table = {
        "base":      [2]*8,
        "exponents": [7, 6, 5, 4, 3, 2, 1, 0],
        "values":    [128, 64, 32, 16, 8, 4, 2, 1],
    }

    def build_table(**kwargs):
        # Performs a shallow copy so that the original table is not modified in case of appendage
        new_table = conversion_table.copy()
        
        # Check for a keyword argument called bits and add it to the table if it exists
        # This is used to display the bits in the table 
        if kwargs.get("bits") != None:
            new_table["bits"] = kwargs["bits"]

        return tabulate(new_table, headers="keys", tablefmt="grid")

    # Init list for /new/ IP
    converted_ip = [] 

    print(f"\nConverting IP address {".".join(ip_address)}...\n")

    # It's decimal, return binary conversion
    if 4 <= sum(octet_lengths) <= 12:
        for octet in ip_address:
            if parser_args.verbose:
                print("-" * 37)
                print(f"\nNEW OCTET: {octet}")
            
            octet = int(octet)   # Convert octet to an integer for arithmetic purposes
            converted_octet = "" # Init empty binary octet

            for index, value in enumerate(conversion_table["values"]):
                if octet >= value:
                    converted_octet += "1"

                    if parser_args.verbose: 
                        print(f"{octet} >= {value} (2^{conversion_table["exponents"][index]})")
                        print("∴ bit is 1")
                        print(f"Subtracting {value} from {octet}...")
                        print(f"New value: {octet - value}\n")

                    octet -= value
                elif octet < value:
                    converted_octet += "0"

                    if octet == 0:
                        # Pad the rest of the octet with 0s to make it 8 bits long
                        converted_octet += "0" * (len(conversion_table["values"]) - len(converted_octet))
                        if parser_args.verbose:
                            print(f"{octet} < {value} (2^{conversion_table["exponents"][index]})")
                            print("∴ bit is 0")
                            print(f"Octet is 0, no need to keep going so finishing up...\n")
                        break # No need to keep going if the octet is 0

                    if parser_args.verbose: 
                        print(f"{octet} < {value} (2^{conversion_table["exponents"][index]})")
                        print("∴ bit is 0\n")

            converted_ip.append(converted_octet) # Append the binary octet to the empty IP container
            
            if parser_args.verbose:
                bits = [bit for bit in converted_octet]
                print(build_table(bits=bits)) # Display the table with the bits filled in
                print(f"= {converted_octet}\n")

    # It's binary, return decimal
    elif sum(octet_lengths) == 32:

        # Returns ['base', '2', '2', '2', '2', '2', '2', '2', '2']
        # base = ["exponents"] + positional_value["base"]

        # Returns ['exponents', '128', '64', '32', '16', '8', '4', '2', '1']
        # exponents = ["exponents"] + positional_value["exponents"]

        # Returns ['values', '128', '64', '32', '16', '8', '4', '2', '1']
        # values = [["values"] + [str(value) for value in positional_value["values"]]]
        
        # Returns ['bits', []]
        # Inner list of variable size, appending iteratively
        # bits = ["bits"] + positional_value["bits"]  

        for octet in ip_address:
            decimalized_octet = int(octet, base=2) # Converts a base2 string, i.e. bits, into a base10 integer

            if parser_args.verbose:
                bits = [bit for bit in octet] # Break down octet into its constituent bits

                formula = [] # Init empty string for the formula used to calculate the decimal representation

                # Tabulate conversion_table with bits filled in and formula displayed, before resetting in advance of next octet
                # Only if verbosity is enabled; if not, skip this step
                print(f"Consulting table to convert octet {octet} to decimal...")

                print(build_table(bits=bits), end="") # Display the table with the bits filled in

                for index, bit in enumerate(bits):
                    if bit == "1":
                        positional_value = conversion_table["values"][index] # Get the positional value of the bit
                        if len(formula) == 0:
                            # Pad it with spaces for alignment if it is the first in the list
                            formula.append("\n  " + str(positional_value)) 
                        else:
                            formula.append(str(positional_value)) # Add it to per-octet formula list
                print("\n+ ".join(formula)) # That is not fucking regex
                print(f"= {decimalized_octet}\n")

            # Turn it back into a string and append it to the empty IP container, makes it easier to string back together
            converted_ip.append(str(decimalized_octet))

    converted_ip = ".".join(converted_ip) # Return the binary address as a single string
    return converted_ip