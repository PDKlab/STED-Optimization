import json
import requests

import numpy as np

from skimage.io import imread
from skimage.transform import resize

import utils


class QualityNet:
    """This class implements a remote network

    :param address (str): Address of the network.
    :param port (int): Port of the network (default: 5000)
    """

    def __init__(self, address, port=5000):
        self.address = address
        self.port = port
        self.url = 'http://{}:{}'.format(self.address, self.port)

    def predict(self, sted_confocal):
        """Predict the quality score of an image using a remote neural network.

        :param sted_confocal (str/tuple): Path of saved numpy arrays or tuple of numpy
                                          arrays for sted and confocal

        .. note::

            The data type of image and mask contained (or path given) in `sted_confocal`
            data must be [0, 1] floats.

        :returns: Predicted quality score (float) in [0, 1].
        """
        if isinstance(sted_confocal, str):
            npz = np.load(sted_confocal)
            # img, mask = npz['arr_0'], npz['arr_1']
            sted, confocal = npz['arr_0'], npz['arr_1']
        elif isinstance(sted_confocal, tuple) or isinstance(sted_confocal, list) :
            # img, mask = img_mask
            sted, confocal = sted_confocal
        else:
            print(' [!] img must be a str or a numpy array')

        width, height = sted.shape
        mask_width = int(np.ceil(width / 16))
        mask_height = int(np.ceil(height / 16))
        
        # foreground on confocal image
        fg_c = utils.get_foreground(confocal)
        # foreground on sted image
        fg_s = utils.get_foreground(sted)
        # remove STED foreground points not in confocal foreground, if any
        fg = fg_s * fg_c
        
        # compute binary background mask
        mask = resize(fg, (mask_width, mask_height))
        mask[mask > 0] = 1.0
        mask = (mask / np.sum(mask)) if np.sum(mask) > 0 else mask
        
        tosend = json.dumps({'img':sted.tolist(),
                             'img-type':'{}'.format(sted.dtype),
                             'mask': mask.tolist(),
                             'mask-type':'{}'.format(mask.dtype)})
        r = requests.post(self.url, data=tosend)
        print("VirtualNet call result", r.text)
        return json.loads(r.text)['score']


class PrefNet:

    def __init__(self, address, port=5000):
        self.address = address
        self.port = port
        self.url = 'http://{}:{}'.format(self.address, self.port)

    def predict(self, pair_set):
        pair_set2send = json.dumps({'pair_set':pair_set.astype(float).tolist(), 
                               'type':'{}'.format(pair_set.dtype)})
        r = requests.post(self.url, data=pair_set2send)
        return json.loads(r.text)['good_pair']
