import cv2
import numpy as np
import tensorflow.compat.v1 as tf
import tf_slim as slim

from app.ml.filter import Filter

__model_path__ = 'app/ml/cartoonify/model'


def _res_block(inputs, out_channel=32, name='resblock'):
    with tf.variable_scope(name):
        x = slim.convolution2d(inputs, out_channel, [3, 3],
                               activation_fn=None, scope='conv1')
        x = tf.nn.leaky_relu(x)
        x = slim.convolution2d(x, out_channel, [3, 3],
                               activation_fn=None, scope='conv2')
        return x + inputs


def _tf_box_filter(x, r):
    k_size = int(2 * r + 1)
    ch = x.get_shape().as_list()[-1]
    weight = 1 / (k_size ** 2)
    box_kernel = weight * np.ones((k_size, k_size, ch, 1))
    box_kernel = np.array(box_kernel).astype(np.float32)
    output = tf.nn.depthwise_conv2d(x, box_kernel, [1, 1, 1, 1], 'SAME')
    return output


def _resize_crop(image):
    h, w, c = np.shape(image)
    # st.write(h, w, c)
    if min(h, w) > 720:
        if h > w:
            h, w = int(720 * h / w), 720
        else:
            h, w = 720, int(720 * w / h)
    w = int(w / 2)
    h = int(h / 2)
    image = cv2.resize(np.float32(image), (w, h),
                       interpolation=cv2.INTER_AREA)
    h, w = (h // 8) * 8, (w // 8) * 8
    # st.write(h,w)
    image = image[:h, :w, :]
    return image


class Cartoonify(Filter):
    def __init__(self, layout, frames_dir):
        self.input_placeholder = None
        self.sess = None
        self.out_placeholder = None
        self.frames_dir = frames_dir
        super().__init__(layout, "Cartoonify")
        print("Cartoonify filter initialized")

    def register_filter(self):
        print("TODO: Register the filter here")

    # @st.cache
    def initialize(self):
        tf.disable_v2_behavior()

        # input_photo = tf.placeholder(tf.float32, [1, None, None, 3])
        self.input_placeholder = tf.placeholder(tf.float32, shape=[1, None, None, 3], name='input')
        network_out = self._unet_generator()
        self.out_placeholder = self._guided_filter(network_out, r=1, eps=5e-3)

        all_vars = tf.trainable_variables()
        gene_vars = [var for var in all_vars if 'generator' in var.name]
        saver = tf.train.Saver(var_list=gene_vars)

        config = tf.ConfigProto()
        self.sess = tf.Session(config=config)
        self.sess.run(tf.global_variables_initializer())

        saver.restore(self.sess, tf.train.latest_checkpoint(__model_path__))
        print("Cartoonify model loaded successfully")

    def _unet_generator(self, channel=32, num_blocks=4, name='generator', reuse=False):
        with tf.variable_scope(name, reuse=reuse):
            x0 = slim.convolution2d(self.input_placeholder, channel, [7, 7], activation_fn=None)
            x0 = tf.nn.leaky_relu(x0)

            x1 = slim.convolution2d(x0, channel, [3, 3], stride=2, activation_fn=None)
            x1 = tf.nn.leaky_relu(x1)
            x1 = slim.convolution2d(x1, channel * 2, [3, 3], activation_fn=None)
            x1 = tf.nn.leaky_relu(x1)

            x2 = slim.convolution2d(x1, channel * 2, [3, 3], stride=2, activation_fn=None)
            x2 = tf.nn.leaky_relu(x2)
            x2 = slim.convolution2d(x2, channel * 4, [3, 3], activation_fn=None)
            x2 = tf.nn.leaky_relu(x2)

            for idx in range(num_blocks):
                x2 = _res_block(x2, out_channel=channel * 4, name='block_{}'.format(idx))

            x2 = slim.convolution2d(x2, channel * 2, [3, 3], activation_fn=None)
            x2 = tf.nn.leaky_relu(x2)

            h1, w1 = tf.shape(x2)[1], tf.shape(x2)[2]
            x3 = tf.image.resize_bilinear(x2, (h1 * 2, w1 * 2))
            x3 = slim.convolution2d(x3 + x1, channel * 2, [3, 3], activation_fn=None)
            x3 = tf.nn.leaky_relu(x3)
            x3 = slim.convolution2d(x3, channel, [3, 3], activation_fn=None)
            x3 = tf.nn.leaky_relu(x3)

            h2, w2 = tf.shape(x3)[1], tf.shape(x3)[2]
            x4 = tf.image.resize_bilinear(x3, (h2 * 2, w2 * 2))
            x4 = slim.convolution2d(x4 + x0, channel, [3, 3], activation_fn=None)
            x4 = tf.nn.leaky_relu(x4)
            x4 = slim.convolution2d(x4, 3, [7, 7], activation_fn=None)

            return x4

        # def fast_guided_filter(lr_x, lr_y, hr_x, r=1, eps=1e-8):
        #     # assert lr_x.shape.ndims == 4 and lr_y.shape.ndims == 4 and hr_x.shape.ndims == 4
        #
        #     lr_x_shape = tf.shape(lr_x)
        #     # lr_y_shape = tf.shape(lr_y)
        #     hr_x_shape = tf.shape(hr_x)
        #
        #     N = tf_box_filter(tf.ones((1, lr_x_shape[1], lr_x_shape[2], 1), dtype=lr_x.dtype), r)
        #
        #     mean_x = tf_box_filter(lr_x, r) / N
        #     mean_y = tf_box_filter(lr_y, r) / N
        #     cov_xy = tf_box_filter(lr_x * lr_y, r) / N - mean_x * mean_y
        #     var_x = tf_box_filter(lr_x * lr_x, r) / N - mean_x * mean_x
        #
        #     A = cov_xy / (var_x + eps)
        #     b = mean_y - A * mean_x
        #
        #     mean_A = tf.image.resize_images(A, hr_x_shape[1: 3])
        #     mean_b = tf.image.resize_images(b, hr_x_shape[1: 3])
        #
        #     output = mean_A * hr_x + mean_b
        #
        #     return output
    def _guided_filter(self, y, r, eps=1e-2):
        x = self.input_placeholder
        x_shape = tf.shape(x)

        n = _tf_box_filter(tf.ones((1, x_shape[1], x_shape[2], 1), dtype=x.dtype), r)

        mean_x = _tf_box_filter(x, r) / n
        mean_y = _tf_box_filter(y, r) / n
        cov_xy = _tf_box_filter(x * y, r) / n - mean_x * mean_y
        var_x = _tf_box_filter(x * x, r) / n - mean_x * mean_x

        a = cov_xy / (var_x + eps)
        b = mean_y - a * mean_x

        mean_a = _tf_box_filter(a, r) / n
        mean_b = _tf_box_filter(b, r) / n

        output = mean_a * x + mean_b

        return output

    def apply_filter(self, frame):
        image = cv2.imread(frame)
        image = _resize_crop(image)

        batch_image = image.astype(np.float32) / 127.5 - 1
        batch_image = np.expand_dims(batch_image, axis=0)

        output = self.sess.run(self.out_placeholder, feed_dict={self.input_placeholder: batch_image})
        output = (np.squeeze(output) + 1) * 127.5
        output = np.clip(output, 0, 255).astype(np.uint8)

        cv2.imwrite(frame, output)
