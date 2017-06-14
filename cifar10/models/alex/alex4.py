# Python 2 & 3 compatibility
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf

import models.model as model

WEIGHT_DECAY = 5e2

class Alex4(model.Model):

    def __init__(self, wd=WEIGHT_DECAY):

        super(Alex4, self).__init__(wd)

    def inference(self, images):

        # conv1
        with tf.variable_scope('conv1') as scope:
            weights = self._get_weights_var('weights',
                                            shape=[5, 5, 3, 96],
                                            decay=False)
            biases = tf.get_variable('biases', 
                                    shape=[96],
                                    dtype=tf.float32,
                                    initializer=tf.constant_initializer(0.1))
            conv = tf.nn.conv2d(images,
                                weights,
                                strides=[1,1,1,1],
                                padding='SAME')
            pre_activation = tf.nn.bias_add(conv, biases)
            conv1 = tf.nn.relu(pre_activation, name= scope.name)

        # pool1
        with tf.variable_scope('pooling1_lrn') as scope:
            pool1 = tf.nn.max_pool(conv1,
                                   ksize=[1,3,3,1],
                                   strides=[1,2,2,1],
                                   padding='SAME',
                                   name='pooling1')

        # conv2
        with tf.variable_scope('conv2') as scope:
            weights = self._get_weights_var('weights',
                                            shape=[3, 3, 96, 96],
                                            decay=False)
            biases = tf.get_variable('biases', 
                                    shape=[96],
                                    dtype=tf.float32,
                                    initializer=tf.constant_initializer(0.1))
            conv = tf.nn.conv2d(pool1,
                                weights,
                                strides=[1,1,1,1],
                                padding='SAME')
            pre_activation = tf.nn.bias_add(conv, biases)
            conv2 = tf.nn.relu(pre_activation, name= scope.name)

        # pool2
        with tf.variable_scope('pooling2_lrn') as scope:
            pool2 = tf.nn.max_pool(conv2,
                                   ksize=[1,3,3,1],
                                   strides=[1,2,2,1],
                                   padding='SAME',
                                   name='pooling2')

        # local3
        with tf.variable_scope('fc2') as scope:
            N = images.get_shape().as_list()[0]
            reshape = tf.reshape(pool2, shape=[N, -1])
            dim = reshape.get_shape()[1].value
            weights = self._get_weights_var('weights',
                                            shape=[dim,384],
                                            decay=True)
            biases = tf.get_variable('biases',
                                    shape=[384],
                                    dtype=tf.float32, 
                                    initializer=tf.constant_initializer(0.1))
            fc2 = tf.nn.relu(tf.matmul(reshape, weights) + biases,
                             name=scope.name)

        # local4
        with tf.variable_scope('fc3') as scope:
            weights = self._get_weights_var('weights',
                                            shape=[384,192],
                                            decay=True)
            biases = tf.get_variable('biases',
                                    shape=[192],
                                    dtype=tf.float32,
                                    initializer=tf.constant_initializer(0.1))
            fc3 = tf.nn.relu(tf.matmul(fc2, weights) + biases, name=scope.name)

        # Last fully connected layer
        with tf.variable_scope('fc4') as scope:
            weights = self._get_weights_var('weights',
                                            shape=[192,10],
                                            decay=False)
            biases = tf.get_variable('biases',
                                    shape=[10],
                                    dtype=tf.float32,
                                    initializer=tf.constant_initializer(0.0))
            fc4 = tf.add(tf.matmul(fc3, weights), biases, name=scope.name)
        
        return fc4
