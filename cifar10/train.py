# Adapted from CIFAR10 Tensorflow tutorial
#
# Train a CIFAR10 model
#
# Usage: python cifar10/train.py [options]
#
# Type 'python cifar10/train.py --help' for a list of available options.
#

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import time
from datetime import datetime
import os

import job
import models.data as data
import models.select as select

FLAGS = tf.app.flags.FLAGS

tf.app.flags.DEFINE_integer('max_steps', 10000,
                            """Number of batches to run.""")
tf.app.flags.DEFINE_float('learning_rate', 0.1,
                            """Initial learning rate.""")
tf.app.flags.DEFINE_integer('log_freq', 10,
                            """How often to log results (steps).""")
tf.app.flags.DEFINE_integer('save_freq', 60,
                            """How often to save model to disk (seconds).""")
tf.app.flags.DEFINE_boolean('resume', False,
                            """Continue training the previous model""")

MOVING_AVERAGE_DECAY = 0.9999

def get_run_dir(log_dir, model_name):
    model_dir = os.path.join(log_dir, model_name)
    if os.path.isdir(model_dir):
        if FLAGS.resume:
            # Reuse the last directory
            run = len(os.listdir(model_dir)) - 1
        else:
            # We will create a new directory for this run
            run = len(os.listdir(model_dir))
    else:
        run = 0
    return os.path.join(model_dir, '%d' % run)

def train_loop():

    # Get traing parameters
    data_dir = FLAGS.data_dir
    batch_size = FLAGS.batch_size
    learning_rate = FLAGS.learning_rate

    # Create global step counter
    global_step = tf.Variable(0, name='global_step', trainable=False)

    # Instantiate async producers for images and labels
    images, labels = data.train_inputs(data_dir=data_dir,
                                       batch_size=batch_size)

    # Instantiate the model
    model = select.by_name(FLAGS.model)

    # Build a Graph that computes the logits predictions from the
    # inference model
    logits = model.inference(images)

    # Calculate loss
    loss = model.loss(logits, labels)

    # Attach a scalar summary only to the total loss
    tf.summary.scalar('loss', loss)
    # Note that for debugging purpose, we could also track other losses
    #for l in tf.get_collection('losses'):
    #    tf.summary.scalar(l.op.name, l)

    # Build a graph that applies gradient descent to update model parameters
    optimizer = tf.train.GradientDescentOptimizer(learning_rate)
    sgd_op = optimizer.minimize(loss, global_step = global_step)

    # Build yet another graph to evaluate moving averages of variables after
    # each step: these smoothed parameters will be loaded instead of the raw
    # trained values during evaluation
    variable_averages = \
        tf.train.ExponentialMovingAverage(MOVING_AVERAGE_DECAY, global_step)
    variables_averages_op = variable_averages.apply(tf.trainable_variables())

    # Create a meta-graph that includes sgd and variables moving average
    with tf.control_dependencies([sgd_op, variables_averages_op]):
        train_op = tf.no_op(name='train')

    # Build another graph to provide training summary information
    summary_op = tf.summary.merge_all()

    # We use one log dir per run
    run_dir = get_run_dir(FLAGS.log_dir, FLAGS.model)
    checkpoint_dir = os.path.join(run_dir, 'train')

    # This class implements the callbacks for the logger
    class _LoggerHook(tf.train.SessionRunHook):
      """Logs loss and runtime."""

      def begin(self):
        self._step = -1
        self._start_time = time.time()

      def before_run(self, run_context):
        self._step += 1
        return tf.train.SessionRunArgs(loss)  # Asks for values.

      def after_run(self, run_context, run_values):
        if self._step % FLAGS.log_freq == 0:
            current_time = time.time()
            duration = current_time - self._start_time
            self._start_time = current_time

            loss_value = run_values.results
            examples_per_sec = FLAGS.log_freq * FLAGS.batch_size / duration
            sec_per_batch = float(duration / FLAGS.log_freq)

            format_str = '%s: step %d, loss = %.2f '
            format_str += '(%.1f examples/sec; %.3f sec/batch)'
            print (format_str % (datetime.now(),
                                 self._step,
                                 loss_value,
                                 examples_per_sec,
                                 sec_per_batch))

    # Start the training loop using a monitored session (autmatically takes
    # care of thread sync)
    with tf.train.MonitoredTrainingSession(
        checkpoint_dir=checkpoint_dir,
        save_checkpoint_secs=FLAGS.save_freq,
        hooks=[tf.train.StopAtStepHook(last_step=FLAGS.max_steps),
               tf.train.NanTensorHook(loss),
               _LoggerHook()]) as mon_sess:
        while not mon_sess.should_stop():
            mon_sess.run(train_op)

def main(argv=None):
    data.maybe_download_and_extract(FLAGS.data_dir)
    train_loop()

if __name__ == '__main__':
    tf.app.run()
