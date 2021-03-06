"""
Data export in SPSS (using R).
"""

import opal.core
import opal.io
import sys


def add_arguments(parser):
    """
    Add data command specific options
    """
    parser.add_argument('--datasource', '-d', required=True, help='Datasource name')
    parser.add_argument('--tables', '-t', nargs='+', required=True, help='The list of tables to be exported')
    parser.add_argument('--output', '-out', required=True, help='Output file name (.sav or .zsav (compressed format))')
    parser.add_argument('--identifiers', '-id', required=False, help='Name of the ID mapping')
    parser.add_argument('--no-multilines', '-nl', action='store_true',
                        help='Do not write value sequences as multiple lines')
    parser.add_argument('--json', '-j', action='store_true', help='Pretty JSON formatting of the response')


def do_command(args):
    """
    Execute export data command
    """
    # Build and send request
    try:
        # Check output filename extension
        if not (args.output.endswith('.sav')) and not (args.output.endswith('.zsav')):
            raise Exception('Output must be a SPSS file (.sav or .zsav).')

        client = opal.core.OpalClient.build(opal.core.OpalClient.LoginInfo.parse(args))
        exporter = opal.io.OpalExporter.build(client=client, datasource=args.datasource, tables=args.tables,
                                              identifiers=args.identifiers, output=args.output, incremental=False,
                                              multilines=(not args.no_multilines), verbose=args.verbose)
        # print result
        response = None
        if args.output.endswith('.sav'):
            response = exporter.submit('RSPSS')
        else:
            response = exporter.submit('RZSPSS')

        # format response
        res = response.content
        if args.json:
            res = response.pretty_json()

        # output to stdout
        print(res)

    except Exception as e:
        print(e)
        sys.exit(2)
    except pycurl.error as error:
        errno, errstr = error
        print('An error occurred: ', errstr, file=sys.stderr)
        sys.exit(2)
