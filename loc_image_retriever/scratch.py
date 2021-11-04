import argparse
import logging
import pathlib
import sys
import yaml
from pathlib import Path

CONFIG_FILE = 'scratch.yml'  # constant

def main(args):
    """TODO"""

    # Create a parser
    parser = argparse.ArgumentParser('scratch file')
    parser.add_argument(
        '-k',
        '--key',
        type=str,
        required=True,
        help='Required YAML map key'
    )
    parser.add_argument(
        '-f',
        '--format',
        type=str,
        required=False,
        default='jpg',
        help="Image format"
        )

    parser = parser.parse_args(args)
    city = parser.key
    format = parser.format

    # Create a logger (scratch.log)
    logging.basicConfig(
        format='%(levelname)s: %(message)s',
        level=logging.DEBUG
    )

    logger = logging.getLogger()
    # logger.setLevel(logging.DEBUG)

    # Add file and stream handlers
    logger.addHandler(logging.FileHandler('output/scratch.log'))
    logger.addHandler(logging.StreamHandler(sys.stdout))

    # Read YAML file
    with open(CONFIG_FILE, 'r') as file_object:
        data = yaml.load(file_object, Loader=yaml.FullLoader)

        logger.info(f"Read {CONFIG_FILE}")

        # Filter YAML data with CLI arg
        if city == 'ann_arbor_1925':
            print(f"{data['cities']['ann_arbor_1925']['url']}\n")
        elif city == 'chelsea_1918':
            print(f"{data['cities']['chelsea_1918']['url']}\n")
        elif city == 'jackson_1907':
            print(f"{data['cities']['jackson_1907']['url']}\n")
        else:
            print('Municipality not recognized.')

if __name__ == '__main__':
    main(sys.argv[1:]) # ignore the first element (program name)