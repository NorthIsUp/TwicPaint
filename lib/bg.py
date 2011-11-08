import os
import mimetypes
import Image

class BG(object):
    _instance = None
    def __new__(cls, sizes=[16, 32]):
        if not cls._instance:
            cls._instance = super(BG, cls).__new__(cls)

            cls._instance.sizes = sizes
            cls._instance.composites = None
            cls._instance.bg = {}

            path = os.path.abspath(os.path.join(os.path.dirname(__file__),"../static/"))
            for fname in os.listdir(os.path.join(path , "bgs_master")):
                im = Image.open(os.path.join(path, "bgs_master", fname))
                im.load()

                for size in sizes:  
                    str_size = str(size)
                    im = im.resize((size, size))

                    name = fname[:-4] + "_" + str_size + ".gif"
                    im.save(path + "/bgs/" + name )

                    bg_id = name[:-7]
                    if bg_id not in cls._instance.bg:
                        cls._instance.bg[bg_id] = {}
                    if str_size not in cls._instance.bg[bg_id]:
                        cls._instance.bg[bg_id][str_size] = {}
                    cls._instance.bg[bg_id][str_size]['im'] = im

            cls._instance.composites = dict([ (str(size), Image.new('RGB', (size * len(cls._instance.bg.keys())/2, size*2))) for size in sizes ])

            for fname in os.listdir(path + "/bgs/"):
                if fname[-3:] == "gif" and "composite" not in fname:
                    pack = BG._pack_image(path+"/bgs/"+fname, 800)
                    size = str(fname[-6:-4])
                    bg_id = fname[:-7]
                    # if bg_id not in cls._instance.bg:
                    #     cls._instance.bg[bg_id] = {}
                    # if size not in cls._instance.bg[bg_id]:
                    #     bg[bg_id][size] = {}

                    ibd = int(bg_id)
                    isize = int(size)
                    x = 0 if ibd == 0 else ibd / 2 * isize
                    y = ibd % 2 * isize
                    print "%d, %d"%(x,y)
                    cls._instance.composites[size].paste(cls._instance.bg[bg_id][size]["im"], (x, y))

                    cls._instance.bg[bg_id][size].update({"headers":pack[0], "mime_data":pack[1], "raw":pack[2], "x":x, "y":y})


            for k,v in cls._instance.composites.iteritems():
                p = os.path.join(path,"bgs","composite_" + k + ".png")
                v.save(p)
        
            cls._instance.keys = cls._instance.bg.keys()
            cls._instance.count = len(cls._instance.bg)

        return cls._instance


    @staticmethod
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

        return headers, body, fpim