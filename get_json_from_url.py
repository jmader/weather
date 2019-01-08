def get_json_from_url(url):
    '''
    Reads input URL and returns a Python list.  It is assumed that
    the URL returns data in JSON format.

    @type url: string
    @param url: URL to read and convert JSON to Python list
    '''

    import verification
    import json
    import urllib.request

    try:

        # Read the input URL

        data = urllib.request.urlopen(url)

        # Convert from byte to ascii

        newData = data.read().decode('utf8').replace("'", '"')

        # Convert to Python list

        jsonData = json.loads(newData)
        return jsonData
    except:
        return 'ERROR'
