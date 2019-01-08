import os

def fix_html(file, log_writer=''):
    """
    Remove Bokey header from HTML file.
    Add include of header.js.
    """

    # Does the file exist?
    if not os.path.exists(file):
        if log_writer:
            log_writer.info('fix_html file does not exist {}'.format(file))

    # Read the file and find the start of the data section
    with open(file, 'r') as fp:
        data = fp.read().splitlines(True)

    dataString = '<div class="bk-root"'
    num = holo = 0
    for key, line in enumerate(data):
        if num == 0 and dataString in line:
            num = key
        if holo == 0 and 'HoloViewsWidget' in line:
            holo = key

    if num == 0:
        if log_writer:
            log_writer.info('fix_html.py data section not found')
    else:
        # Create new HTML file
        with open(file, 'w') as fp:
            fp.writelines(data[num:])
        if log_writer:
            log_writer.info('fix_html.py file header updated')

        # Create header.js to output directory
        # Stored locally now and copied to release
#        outDir = os.path.dirname(file)
#        hFile = ''.join((outDir, '/header.js'))
#        if not os.path.exists(hFile):
#            with open(hFile, 'w') as fp2:
#                fp2.writelines(data[holo:num])
#            if log_writer:
#                log_writer.info('fix_html.py header.js created in {}'.format(outDir))
