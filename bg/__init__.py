import os
import mimetypes
from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart
import base64
from pprint import pprint

pwd = os.path.abspath(os.path.dirname(__file__)) + "/"
bg = {}

def _pack_image(filename, max_size):
    """Pack image from file into multipart-formdata post body"""
    # image must be less than 700kb in size
    # try:
    #     if os.path.getsize(filename) > (max_size * 1024):
    #         raise TweepError('File is too big, must be less than 700kb.')
    # except os.error, e:
    #     raise TweepError('Unable to access file')

    # image must be gif, jpeg, or png
    file_type = mimetypes.guess_type(filename)
    if file_type is None:
        raise TweepError('Could not determine file type')
    file_type = file_type[0]
    if file_type not in ['image/gif', 'image/jpeg', 'image/png']:
        raise TweepError('Invalid file type for image: %s' % file_type)

    # build the mulitpart-formdata body
    fp = open(filename, 'rb')
    BOUNDARY = 'TwicPaint'
    body = []
    body.append('--' + BOUNDARY)
    body.append('Content-Disposition: form-data; name="image"; filename="%s"' % filename)
    body.append('Content-Type: %s' % file_type)
    body.append('')
    body.append(fp.read())
    body.append('--' + BOUNDARY + '--')
    body.append('')
    fp.close()
    body = '\r\n'.join(body)

    # build headers
    headers = {
        'Content-Type': 'multipart/form-data; boundary='+BOUNDARY,
        'Content-Length': len(body)
    }

    return headers, body

dirList=os.listdir(pwd)
for i, fname in enumerate(dirList):
    if fname[-3:] == "gif":
        bg[i] = _pack_image(pwd+fname, 800)

    # pprint(bg[x])
    # pprint(bg[x])
    # root = MIMEMultipart('form-data')
    # fp = open(pwd + "/" + x +".png", "rb")
    # data = fp.read()
    # fp.close()
    # 
    # img = MIMEImage(data)
    # 
    # root.attach(img)
    # img.add_header('Content-Length', str(len(img.get_payload())))
    # 
    # bg[x] = root
    # print(dir(bg[x]))
    # print bg[x]._headers
    # print(bg[x].as_string())
