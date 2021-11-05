import argparse

DESCRIPTION = """
Library of Congress (LoC) image retrieval script.

The retriever.py script retrieves a single volume of map images from the
Library of Congress (https://www.loc.gov/). The script relies on config.yml to provide
configuration values that "point" the script to the target image collection. The script is run from
the terminal and accepts a number of command line options.

Once configured, the script retrieves the target images, renames the downloaded files,
stores them locally in the < output > location, and logs the process both via the terminal and
a log file.

LoC URL template

{scheme}://{server}{/id_prefix}/{identifier}/{region}/{size}/{rotation}/{quality}.{format}
"""

def create_parser():
    """Return a custom argument parser.

    Parameters:
       None

    Parser arguments:
        short_flag (str): short version of command option
        long_flag (str): long version of command option
        type (str): argument type (e.g., str, int, bool)
        required (bool): specifies whether or not command option is required
        default (obj): default value, typically str or int
        help (str): short description of command option

    Returns:
        parser (ArgumentParser): parser object
    """

    parser = argparse.ArgumentParser(DESCRIPTION)
    parser.add_argument(
        '-k',
        '--key',
        type=str,
        required=True,
        help=("String value that matches a map key in the companion < config.yml > file. The \
               argument is used to filter the relevant map data contained in the loaded YAML file.")
        )
    parser.add_argument(
        '-f',
        '--format',
        type=str,
        required=False,
        default='jpg',
        help=("String value that sets the image format extension. Options: 'jpg', 'gif', 'jp2', \
               'tif'. Default value = 'jpg'.")
        )
    parser.add_argument(
        '-o',
        '--output',
        type=str,
        required=False,
        default='./output',
        help=("String value corresponding to the filepath for local storage of the retrieved \
              images. Default value = './output'.")
	)
    parser.add_argument(
        '-q',
        '--quality',
        type=str,
        required=False,
        default='default',
        help=("String value that sets the image quality. Options: 'color', 'grey', 'bitonal', \
              'default'. Default value = 'default'.")
        )
    parser.add_argument(
        '-r',
        '--region',
        type=str,
        required=False,
        default='full',
        help=("String value that defines the rectangular portion of the full image to be returned. \
               Region can be specified by pixel coordinates, percentage or by the value “full”, \
               which specifies that the entire image should be returned. Default value = 'full'.")
        )
    parser.add_argument(
        '-rd',
        '--rotation_degrees',
        type=int,
        required=False,
        default=0,
        help=("Integer value that sets the image rotation by degrees (0-360). Default value = 0.")
        )
    parser.add_argument(
        '-s',
        '--size',
        type=int,
        required=False,
        default=25,
        help=("Integer value that sets the width and height of the image scaled to n percent of \
              the width and height of the extracted region ('pct:n'). The aspect ratio of the \
              returned image is the same as that of the extracted region. Default value = 25.")
        )

    return parser
