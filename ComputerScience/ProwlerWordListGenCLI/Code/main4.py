from itertools import product, permutations
import argparse
import pyfiglet
from langs import translations
import os

version_number = 1.0
lang = "fr"

ascii_art = pyfiglet.figlet_format(f'Prowler {version_number}')


# FR: Table de substitutions de leet par defaut
# EN: Default Table for leet speak substitutions
default_leet = {
    'a': ['@', '4'],
    'e': ['3'],
    'i': ['1', '!'],
    'o': ['0'],
    's': ['$', '5'],
}


def load_leet_map(cli_overrides=None):
    # FR: Copie la table par defaut
    # EN: copy the default table
    leet = default_leet.copy()

    # FR: Si l'utilisateur passe des overrides (a=@)
    # EN: if the user passes leet overrides (a=@)
    if cli_overrides:
        # FR: Modifie la table avec les preferences de l'utilisateur
        # EN: modify the table with user preferences
        for kv in cli_overrides:
            if '=' in kv:
                key, value = kv.split('=', 1)
                leet[key.lower()] = [value]
    
    # FR: Retourne la nouvelle table
    # EN: return the new table
    return leet

# Generate all case permutations
def generate_case_permutations(word, prefix='', suffix='', capitalise=False):

    variants = []

    if not word.endswith(".txt"):
        states = list(product([0, 1], repeat=len(word)))

        # Normalize irp
        if isinstance(prefix, str) and prefix.endswith(".txt"):
            with open(prefix, 'r') as f:
                prefix_list = set(f.read().splitlines())
        else:
            prefix_list = [prefix] if prefix else ['']

        # Normalize irs
        if isinstance(suffix, str) and suffix.endswith(".txt"):
            with open(suffix, 'r') as f:
                suffix_list = set(f.read().splitlines())
        else:
            suffix_list = [suffix] if suffix else ['']

        for suffix_item in suffix_list:
            for prefix_item in prefix_list:
                for state in states:
                    new_word = ''
                    for i, bit in enumerate(state):
                        new_word += word[i].lower() if capitalise or not bit else word[i].upper()
                    full_variant = prefix_item + new_word + suffix_item
                    variants.append(full_variant)

    else:
        with open(word, 'r') as wordfile:
            words = set(wordfile.read().splitlines())

        if isinstance(prefix, str) and prefix.endswith(".txt"):
            with open(prefix, 'r') as f:
                prefix_list = set(f.read().splitlines())
        else:
            prefix_list = [prefix] if prefix else ['']

        if isinstance(suffix, str) and suffix.endswith(".txt"):
            with open(suffix, 'r') as f:
                suffix_list = set(f.read().splitlines())
        else:
            suffix_list = [suffix] if suffix else ['']

        for word in words:
            states = list(product([0, 1], repeat=len(word)))
            for suffix_item in suffix_list:
                for prefix_item in prefix_list:
                    for state in states:
                        new_word = ''
                        for i, bit in enumerate(state):
                            new_word += word[i].lower() if capitalise or not bit else word[i].upper()
                        full_variant = prefix_item + new_word + suffix_item
                        variants.append(full_variant)

    return set(variants)

# Apply leetspeak to a list of words
def generate_leet_variants(words, leet_map):
    all_variants = []
    for word in words:
        chars = []
        for c in word:
            variants = [c]
            if c.lower() in leet_map:
                variants.extend(leet_map[c.lower()])
            chars.append(variants)
        all_variants.extend([''.join(p) for p in product(*chars)])
    return set(all_variants)



# main processing function
def run_prowler(args):
    if args.word:
        case_variants = generate_case_permutations(
            args.word, args.prefix, args.suffix,args.capitalise
        )

    if args.combinations:
        states = [''.join(p) for p in permutations(args.combinations)]
        print(states)
        return

    if args.leet:
        leet_map = load_leet_map(args.leetsub)
        all_variants = generate_leet_variants(case_variants, leet_map)
    elif args.word:
        all_variants = case_variants
    else:
        return

    if args.output:
        with open(args.output, 'a') as f:
            for variant in all_variants:
                f.write(variant + '\n')
        print(f"added to {args.output}")
    else:
        for variant in all_variants:
            print(variant)



# interactive shell
def prowler_shell():
    print(ascii_art)
    print(translations[lang]["menu_text"])

    while True:
        cmd = input("prowler> ").strip()

        if cmd.lower() == "exit":
            break
        if not cmd:
            continue

        cmd_args = cmd.split()

        shell_parser = argparse.ArgumentParser(add_help=False)
        shell_parser.add_argument('-w', '--word')
        shell_parser.add_argument('-o', '--output')
        shell_parser.add_argument('-p', '--prefix', default='')
        shell_parser.add_argument('-s', '--suffix', default='')
        shell_parser.add_argument('-l', '--leet', action='store_true')
        shell_parser.add_argument('-ls', '--leetsub', nargs='*')
        shell_parser.add_argument('-cbn', '--combinations')
        shell_parser.add_argument('-cap', '--capitalise', action='store_true')
        shell_parser.add_argument('-clear','--clear', action='store_true')
        shell_parser.add_argument('-cmdfile','--commandfile')

        try:
            args = shell_parser.parse_args(cmd_args)
        except SystemExit:
            print("Invalid command")
            continue
        
        # Clear the terminal
        if args.clear:
            os.system("cls")
            continue
        # Add a file full of commands to produce huge wordlists easily
        elif args.commandfile:
            # open the file
            with open(args.commandfile) as f:
                commands = [line.strip() for line in f]

            # go through each command and execute it
            for cmd in commands:
                tokens = cmd.split()
                args = shell_parser.parse_args(tokens)
                run_prowler(args)
        else:
            run_prowler(args)



# argparses
parser = argparse.ArgumentParser(description="Generate case and leet variants of a word.")
parser.add_argument('-w', '--word', required=False, help='The base word')
parser.add_argument('-o', '--output', help='File to write output')
parser.add_argument('-p', '--prefix', default='', help='Optional prefix')
parser.add_argument('-s', '--suffix', default='', help='Optional suffix')
parser.add_argument('-l', '--leet', action='store_true', help='Enable leetspeak substitutions')
parser.add_argument('-ls', '--leetsub', nargs='*', help='Override default leet map (ex: e=3 s=$)')
parser.add_argument('-cbn', '--combinations', help='Generates all combinations of whatever you input')
parser.add_argument('-cap', '--capitalise', action='store_true', help='Generate the word with no capitalisation')
parser.add_argument('-run', '--run', action='store_true', help='Start interactive shell')
parser.add_argument('-clear', '--clear', action='store_true', required=False, help='Clears the cmd')
parser.add_argument('-cmdfile','--commandfile',help='Allows a file of commands to be read and executed')
args = parser.parse_args()


# main startup
if args.run:
    prowler_shell()
else:
    run_prowler(args)
