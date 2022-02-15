"""
This script is intended for the model object
of ResDNN Histology Network.
The model was re-trained for usage with different basis function ('mrtrix') set
as per the proposed model from the paper:
[1] Nath, V., Schilling, K. G., Parvathaneni, P., Hansen,
C. B., Hainline, A. E., Huo, Y., ... & Stepniewska, I. (2019).
Deep learning reveals untapped information for local white-matter
fiber reconstruction in diffusion-weighted MRI.
Magnetic resonance imaging, 62, 220-227.
[2] Nath, V., Schilling, K. G., Hansen, C. B., Parvathaneni,
P., Hainline, A. E., Bermudez, C., ... & Stępniewska, I. (2019).
Deep learning captures more accurate diffusion fiber orientations
distributions than constrained spherical deconvolution.
arXiv preprint arXiv:1911.07927.
"""
from distutils.version import LooseVersion

from dipy.utils.optpkg import optional_package

tf, have_tf, _ = optional_package('tensorflow')

if have_tf:
    if LooseVersion(tf.__version__) < LooseVersion('2.0.0'):
        raise ImportError('Please upgrade to TensorFlow 2+')

import tensorflow as tf
from tensorflow.keras.layers import Input, Dense, Add, Activation
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.optimizers import RMSprop

#from tf.keras.layers import Input, Dense, Dropout, merge, concatenate, Convolution3D, Flatten

def custom_accuracy_sh(y_true, y_pred):
    y_true = y_true[0:45]
    y_pred = y_pred[0:45]

    comp_true = tf.math.conj(y_true)
    norm_true = y_true / tf.sqrt(tf.reduce_sum(tf.multiply(y_true, comp_true)))

    comp_pred = tf.math.conj(y_pred)
    norm_pred = y_pred / tf.sqrt(tf.reduce_sum(tf.multiply(y_pred, comp_pred)))

    comp_p2 = tf.math.conj(norm_pred)
    acc = tf.math.real(tf.reduce_sum(tf.multiply(norm_true, comp_p2)))

    return acc



class HistoResDNN(object):

    def __init__(self, input_shape=(45,),
                 num_hidden=45, act_hidden='relu',
                 num_out=45, act_out='linear',
                 optimizer='rmsprop',
                 loss='mse'):
        """ Single Layer Perceptron with Dropout
        Parameters
        ----------
        input_shape : tuple
            Shape of data to be trained
        num_hidden : int
            Number of nodes in hidden layers 2 and 4
        act_hidden : string
            Activation function used in hidden layer
        num_out : 45
            Number of nodes in output layer
        act_out : string
            Activation function used in output layer
        optimizer :  string
            Select optimizer. Default rmsprop.
        loss : string
            Select loss function for measuring accuracy.
            Default mse.
        """
        self.accuracy = None
        self.loss = None

        #input_dims = self.input_shape
        #skip_neurons = self.num_hidden
        inputs = Input(shape=input_shape)

        # ResDNN Network Flow
        x1 = Dense(400, activation='relu')(inputs)
        x2 = Dense(num_hidden, activation='relu')(x1)
        x3 = Dense(200, activation='relu')(x2)
        x4 = Dense(num_hidden, activation='linear')(x3)
        res_add = Add()([x2, x4])
        x5 = Dense(200, activation='relu')(res_add)
        x6 = Dense(num_hidden)(x5)

        model = Model(inputs=inputs, outputs=x6)

        opt_func = RMSprop(learning_rate=0.0001)
        '''
        model = tf.keras.models.Sequential([
            tf.keras.layers.Flatten(input_shape=input_shape),
            tf.keras.layers.Dense(num_hidden, activation=act_hidden),
            tf.keras.layers.Dropout(dropout),
            tf.keras.layers.Dense(num_out, activation=act_out)
            ])
        '''

        model.compile(optimizer=opt_func,
                      loss=loss,
                      metrics=[custom_accuracy_sh])

        self.model = model

    def load_model_weights(self, weights_path):
        self.model.load_weights(weights_path)
        return self.model

    def predict(self, x_test):
        return self.model.predict(x_test)