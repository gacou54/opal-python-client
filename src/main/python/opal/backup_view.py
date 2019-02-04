"""
Backup views of a project: download view's XML representation and save it in a file, one for each view.
"""

import sys
import opal.core
import opal.io
import os


def add_arguments(parser):
    """
    Add data command specific options
    """
    parser.add_argument('--project', '-pr', required=True, help='Source project name')
    parser.add_argument('--views', '-vw', nargs='+', required=False,
                        help='List of view names to be backed up (default is all)')
    parser.add_argument('--output', '-out', required=False, help='Output directory name (default is current directory)')
    parser.add_argument('--force', '-f', action='store_true', help='Skip confirmation when overwriting the backup file.')
    parser.add_argument('--json', '-j', action='store_true', help='Pretty JSON formatting of the response')


def retrieve_datasource_views(args):
    request = opal.core.OpalClient.build(opal.core.OpalClient.LoginInfo.parse(args)).new_request()
    request.fail_on_error()
    if args.verbose:
        request.verbose()
    response = request.get().resource(
        opal.core.UriBuilder(['datasource', args.project, 'tables']).build()).send().as_json()

    views = []
    for table in response:
        if 'viewLink' in table:
            views.append(str(table[u'name']))

    return views

def backup_view(args, view, outdir):
    outfile = view + '.xml'
    print 'Backup of', view, 'in', outfile, '...'

    outpath = os.path.join(outdir, outfile)

    request = opal.core.OpalClient.build(opal.core.OpalClient.LoginInfo.parse(args)).new_request()
    request.fail_on_error()
    if args.verbose:
        request.verbose()
    response = request.get().resource(
        opal.core.UriBuilder(['datasource', args.project, 'view', view, 'xml']).build()).accept_xml().send()

    dowrite = True
    if os.path.exists(outpath) and not args.force:
        dowrite = False
        print 'Overwrite the file "' + outpath + '"? [y/N]: ',
        confirmed = sys.stdin.readline().rstrip().strip()
        if confirmed == 'y':
            dowrite = True

    if dowrite:
        out = open(outpath, 'w+')
        out.write(response.content)
        out.close()


def do_command(args):
    """
    Retrieve table DTOs of the project, look for the views, download the views in XML into a file in provided or current directory
    """

    # Build and send request
    try:
        views = args.views
        obsviews = retrieve_datasource_views(args)
        if not views:
            views = obsviews
        else:
            safeviews = []
            for view in views:
                if view in obsviews:
                    safeviews.append(view)
            views = safeviews
        if not views:
            print 'No views to backup in project', args.project
        else:
            # prepare output directory
            outdir = args.output
            if not outdir:
                outdir = os.getcwd()
            else:
                outdir = os.path.normpath(outdir)
            print 'Output directory is', outdir
            if not os.path.exists(outdir):
                print 'Creating output directory ...'
                os.makedirs(outdir)

            # backup each view
            for view in views:
                backup_view(args, view, outdir)

    except Exception, e:
        print e
        sys.exit(2)
    except pycurl.error, error:
        errno, errstr = error
        print >> sys.stderr, 'An error occurred: ', errstr
        sys.exit(2)