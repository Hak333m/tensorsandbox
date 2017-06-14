import tensorflow as tf

import cs231n
import tuto
import convone
import alex.select

tf.app.flags.DEFINE_string('model', 'cs231n',
        """One of [cs231n, tuto, convone, alex{N}].""")

def by_name(name):
    if name == 'cs231n':
        model = cs231n.Cs231n()
    elif name == 'tuto':
        model = tuto.Tuto()
    elif name == 'convone':
        model = convone.ConvOne()
    elif name.startswith('alex'):
        model = alex.select.by_name(name)
    else:
        raise ValueError('No such model %s' % name)
    return model
