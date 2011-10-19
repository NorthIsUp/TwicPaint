import os
import mimetypes
from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart
import base64
import Image
from pprint import pprint

bg = {}

def _pack_image(filename, max_size):
    """Pack image from file into multipart-formdata post body"""
    # image must be less than 700kb in size
    try:
        if os.path.getsize(filename) > (max_size * 1024):
            raise Exception('File is too big, must be less than 700kb. ' + filename)
    except os.error, e:
        raise Exception('Unable to access file ' + filename)

    # image must be gif, jpeg, or png
    file_type = mimetypes.guess_type(filename)
    if file_type is None:
        raise TweepError('Could not determine file type')
    file_type = file_type[0]
    if file_type not in ['image/gif', 'image/jpeg', 'image/png']:
        raise TweepError('Invalid file type for image: %s' % file_type)

    # build the mulitpart-formdata body
    fp = open(filename, 'rb')
    fpim = fp.read()
    fp.close()

    BOUNDARY = 'TwicPaint'
    body = []
    body.append('--' + BOUNDARY)
    body.append('Content-Disposition: form-data; name="image"; filename="%s"' % filename)
    body.append('Content-Type: %s' % file_type)
    body.append('')
    body.append(fpim)
    body.append('--' + BOUNDARY + '--')
    body.append('')
    body = '\r\n'.join(body)

    # build headers
    headers = {
        'Content-Type': 'multipart/form-data; boundary='+BOUNDARY,
        'Content-Length': len(body)
    }

    return headers, body

path = os.path.abspath(os.path.dirname(__file__)+"/../static/")
for fname in os.listdir(path + "/bgs_master/"):
    im = Image.open(path + "/bgs_master/" + fname)
    im.load()
    
    im_16 = im.resize((16, 16))
    im_32 = im.resize((32, 32))
    
    im_16.save(path + "/bgs/" + fname[:-4] + "_16.gif" )
    im_32.save(path + "/bgs/" + fname[:-4] + "_32.gif" )


for fname in os.listdir(path + "/bgs/"):
    if fname[-3:] == "gif":
        pack = _pack_image(path+"/bgs/"+fname, 800)
        size = str(fname[-6:-4])
        bg_id = fname[:-7]
        if bg_id not in bg:
            bg[bg_id] = {}
        bg[bg_id][size]={"headers":pack[0], "mime_data":pack[1]}
