"""
codes are obtained from: https://github.com/philipperemy/tensorflow-maxout
Maxout Networks (Ian Goodfellow, Yoshua Bengio - 2013)
Maxout Networks TensorFlow implementation presented in https://arxiv.org/abs/1302.4389
"""

from __future__ import print_function

import sys
import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data
from .maxout import max_out
import warnings
import os

# suppress warnings
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


def create_weight_variable(name, shape):
    initializer = tf.contrib.layers.xavier_initializer_conv2d()
    return tf.Variable(initializer(shape=shape), name=name)


def create_bias_variable(name, shape):
    initializer = tf.constant_initializer(value=0.0, dtype=tf.float32)
    return tf.Variable(initializer(shape=shape), name=name)


tf.logging.set_verbosity(tf.logging.ERROR)
mnist = input_data.read_data_sets('/tmp/data/', one_hot=True)

# Parameters
learning_rate = 0.01
training_epochs = 100
batch_size = 100
display_step = 1
logs_path = '/tmp/tensorflow_logs/example'

# tf Graph Input
# mnist data image of shape 28*28=784
x = tf.placeholder(tf.float32, [None, 784], name='InputData')
# 0-9 digits recognition => 10 classes
y = tf.placeholder(tf.float32, [None, 10], name='LabelData')


def linear():
    w1 = create_weight_variable('weight', [784, 10])
    b1 = create_bias_variable('bias', [10])
    return tf.nn.softmax(tf.matmul(x, w1) + b1)


def hidden_relu():
    w1 = create_weight_variable('weight_1', [784, 100])
    b1 = create_bias_variable('bias_1', [100])

    w2 = create_weight_variable('2eight_2', [100, 10])
    b2 = create_bias_variable('bias_2', [10])
    t = tf.nn.relu(tf.matmul(x, w1) + b1)
    return tf.nn.softmax(tf.matmul(t, w2) + b2)


def hidden_maxout():
    w1 = create_weight_variable('weight_1', [784, 100])
    b1 = create_bias_variable('bias_1', [100])
    w2 = create_weight_variable('weight_2', [50, 10])
    b2 = create_bias_variable('bias_2', [10])
    t = max_out(tf.matmul(x, w1) + b1, 50)
    return tf.nn.softmax(tf.matmul(t, w2) + b2)


def select_model():
    usage = 'Usage: python mnist_maxout_example.py (LINEAR|RELU|MAXOUT)'
    assert len(sys.argv) == 2, usage
    t = sys.argv[1].upper()
    print('Type = ' + t)
    if t == 'LINEAR':
        return linear()
    elif t == 'RELU':
        return hidden_relu()
    elif t == 'MAXOUT':
        return hidden_maxout()
    else:
        raise Exception('Unknown type. ' + usage)


# Construct model and encapsulating all ops into scopes, making Tensorboard's Graph visualization more convenient
with tf.name_scope('Model'):
    # Model
    pred = select_model()
with tf.name_scope('Loss'):
    # Minimize error using cross entropy
    cost = tf.reduce_mean(-tf.reduce_sum(y * tf.log(pred), reduction_indices=1))
with tf.name_scope('SGD'):
    # Gradient Descent
    optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(cost)
with tf.name_scope('Accuracy'):
    # Accuracy
    acc = tf.equal(tf.argmax(pred, 1), tf.argmax(y, 1))
    acc = tf.reduce_mean(tf.cast(acc, tf.float32))

# Initializing the variables
init = tf.initialize_all_variables()

# Create a summary to monitor cost tensor
tf.summary.scalar('loss', cost)
# Create a summary to monitor accuracy tensor
tf.summary.scalar('accuracy', acc)
# Merge all summaries into a single op
merged_summary_op = tf.summary.merge_all()

# Launch the graph
with tf.Session() as sess:
    sess.run(init)
    # op to write logs to Tensorboard
    summary_writer = tf.summary.FileWriter(logs_path, graph=tf.get_default_graph())
    # Training cycle
    for epoch in range(training_epochs):
        avg_cost = 0.
        total_batch = int(mnist.train.num_examples / batch_size)
        # Loop over all batches
        for i in range(total_batch):
            batch_xs, batch_ys = mnist.train.next_batch(batch_size)
            # Run optimization op (backprop), cost op (to get loss value)
            # and summary nodes
            _, c, summary = sess.run([optimizer, cost, merged_summary_op], feed_dict={x: batch_xs, y: batch_ys})
            # Write logs at every iteration
            summary_writer.add_summary(summary, epoch * total_batch + i)
            # Compute average loss
            avg_cost += c / total_batch
        # Display logs per epoch step
        if (epoch + 1) % display_step == 0:
            print('Epoch:', '%04d' % (epoch + 1), 'cost=', '{:.9f}'.format(avg_cost))

    print('Optimization Finished!')

    # Test model
    # Calculate accuracy
    print('Accuracy:', acc.eval({x: mnist.test.images, y: mnist.test.labels}))
    print('Run the command line:\n --> tensorboard --logdir=/tmp/tensorflow_logs '
          '\nThen open http://0.0.0.0:6006/ into your web browser')
