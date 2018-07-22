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

    def predict(self, sted):
        """Predict the quality score of an image using a remote neural network.

        :param sted (str/tuple): Path of saved numpy array or numpy array for sted

        .. note::

            The data type of image and mask contained (or path given) in `sted`
            data must be [0, 1] floats.

        :returns: Predicted quality score (float) in [0, 1].
        """
        if isinstance(sted, str):
            sted = np.load(sted)
        
        tosend = json.dumps({'img': sted,
                             'img-type': '{}'.format(sted.dtype)})
        print("Asking QualityNet...")
        r = requests.post(self.url, data=tosend)
        print("QualityNet call result", r.text)
        return json.loads(r.text)['score']


class PrefNet:

    def __init__(self, address, port=5000):
        self.address = address
        self.port = port
        self.url = 'http://{}:{}'.format(self.address, self.port)

    def predict(self, pair_set):
        pair_set2send = json.dumps({'pair_set':pair_set.astype(float).tolist(), 
                               'type':'{}'.format(pair_set.dtype)})
        print("Asking PrefNet...")
        r = requests.post(self.url, data=pair_set2send)
        return json.loads(r.text)['good_pair']
