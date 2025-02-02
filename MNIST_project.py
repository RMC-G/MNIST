#########################################################################
#
# Author  : 	Raymond McCreesh 
#
#
# File Name: 	Keras MNIST 
#
# Description:  A multi-layered convolutional layer is created,
#				using relu Activation and maxpooling. 
#				A dropout function is used between the layers.
#				Flatten is used to convert the pooled feature maps to a single column 
#               this is then inputted into 2 dense layers.
#				Following, the output is given to a softmax activtion 
#				where the outcome is used for
#				backpropagtion and one hot encoding the labels.
#
# Inputs: 		Keras MNIST Dataset --> Convolutional()-->maxpool-->
#				Convolutional() --> dropout--> maxpool--> Flatten --> 
#				Dense(hidden)--> Dropout--> Dense(output).
#
##########################################################################


EPOCHS  = 20   # Training run parameters.
SPLIT   = 0.1  # (90% training, 10% validation.) 
SHUFFLE = True # Random shuffle on each epoch of train/val samples.
BATCH   = 32   # Batch size (note Keras default is 32).
OPT = 'adam'   # Adam optimizer


# Import the relevant Keras library modules into the IPython notebook.
import tensorflow
tensorflow.random.set_seed(2)         # and the seed of the Tensorflow backend.

from tensorflow.keras.utils import to_categorical # for one hot encoding 
from tensorflow.keras import optimizers # Network updates based on loss function
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Flatten, Dropout
from tensorflow.keras.layers import Conv2D, MaxPooling2D, BatchNormalization
print(tensorflow.__version__)    # Should be at least 2.0.


import numpy as np
import matplotlib.pyplot as plt
np.random.seed(1)                # Initialise system RNG.


# Load up the MNIST dataset.
from tensorflow.keras.datasets import mnist 


# Extract the training images into "training_inputs" and their 
# associated class labels into "training_labels".  
# 
# Similarly with the testing set, images in in "testing_inputs" 
# and labels in "testing_labels".
# 
# There are 60000 28 x 28 8-bit greyscale training images and 
# 10000 test images.

(training_inputs, training_labels), (testing_inputs, testing_labels) = mnist.load_data()

print(training_inputs.shape, training_inputs.dtype, testing_inputs.shape, testing_inputs.dtype)

# Testing of random class distribution
print("\n First 1000 training labels: \n", training_labels[:1000])
print("\n First 1000 testing labels: \n", testing_labels[:1000])    


# The inputs to the network need to be normalised 'float32' 
# values, in a tensor of shape (N,28,28,1).  N is the number of 
# images, each one with 28 rows and 28 columns, and one channel.  
# 
# A greyscale image has one channel (normally implicit), an RGB 
# image would have 3. A convolutional net can work with multiple-
# channel input images, but needs the number of channels to be 
# explicitly stated, hence the final 1 in the tensor shape.
# 
# (This is because the Keras "Conv2D" layer expects 4-tensors 
#  as inputs.)
# 
# The labels also need to be converted to categorical form.

training_images = (training_inputs.astype('float32')/255)[:,:,:,np.newaxis]  # Normalised float32 4-tensor.

categorical_training_outputs = to_categorical(training_labels)

testing_images = (testing_inputs.astype('float32')/255)[:,:,:,np.newaxis]

categorical_testing_outputs = to_categorical(testing_labels)
print(training_images.shape,training_images.dtype)
print(testing_images.shape,testing_images.dtype)
print(categorical_training_outputs.shape, training_labels.shape)
print(categorical_testing_outputs.shape, testing_labels.shape)

plt.figure(figsize=(14,4))
for i in range(20):
    plt.subplot(2,10,i+1)
    plt.imshow(training_images[i,:,:,0],cmap='gray')
    plt.title(str(training_labels[i]))
    plt.axis('off')

# Create a Keras model for a net.
# 
# It has six convolutional layers and two maxpooling 
# layers.  The net is then flattened and capped with two dense 
# layers.
# 
# Stride on the convolutional layer is implicitly 1.
# 
# The Maxpool layer uses a 2 x 2 sampling window, without 
# overlap (i.e., strides of 2 in both x and y).
# 
# Finally the network is flattened to 1-d and fed to what is 
# essentially a standard hidden+ouput backprop net for 
# classification.
#

# Creating a Keras model for a net. 
model = Sequential([
                    Conv2D(32, kernel_size=3, padding='same', 
                    input_shape= training_images.shape[1:]),
                    Activation('relu'),
                    BatchNormalization(),

                    Conv2D(32,kernel_size=3),
                    Activation('relu'),
                    BatchNormalization(),

                    Conv2D(32,kernel_size=5),
                    Activation('relu'),
                    MaxPooling2D(pool_size=(2,2), strides=(2,2)), # Dimensionality reduction of the inputs
                    BatchNormalization(),
                    Dropout(0.4),

                    Conv2D(64,kernel_size=3),
                    Activation('relu'),
                    BatchNormalization(),

                    Conv2D(64,kernel_size=3),
                    Activation('relu'),
                    BatchNormalization(),

                    Conv2D(64, kernel_size=5, padding='same'), 
                    Activation('relu'),
                    BatchNormalization(),
                    MaxPooling2D(pool_size=(2,2), strides=(2,2)),
                    Dropout(0.4),

                    Flatten(),
                    Dense(128),
                    Activation('relu'),
                    BatchNormalization(),
                    Dropout(0.4),
                    BatchNormalization(),
                    Dense(10),            # 10 neuron units to predict 0-9 numbers 
                    Activation('softmax') # For output nonlinearity 
                ])

## An overfitted model "memorizes" the noise and details in the training dataset 
## to a point where it negatively impacts the performance of the model on new data. 
## Deep learning models tend to be good at fitting to the training data, 
## but the real challenge is generalization, not fitting.
##


# Review the network.

# model summary
print("The Keras network model")
model.summary()

# Once we have a model and an optimizer, we compile it on the computational
# backend being used by Keras.  When we compile, we specify a loss, or error
# function.
# 
# Here, because we have a convolutional network model, Log-Loss is a good 
# metric.  In Keras this is called "categorical_crossentropy".  And, if 
# using Log-Loss, we really need an adaptive gradient algorithm, here 
# I've used ADAM, which is a good, reliable 
# adaptive algoithm.  My metric is accuracy 
# on the validation set, but I'm also interested in monitoring training
# accuracy and training/validation loss.
# 

#model compilation
model.compile(loss='categorical_crossentropy', optimizer=OPT, metrics=['accuracy'])

from tensorflow.keras.callbacks import EarlyStopping

stop = EarlyStopping(monitor='val_loss', min_delta=0, patience=3, 
                     verbose=2, mode='auto',
                     restore_best_weights=True)


history = model.fit(training_images, categorical_training_outputs,
                    epochs=EPOCHS, 
                    batch_size=BATCH, 
                    shuffle=SHUFFLE, 
                    validation_split=SPLIT,
                    verbose=2, 
                    callbacks=[stop])


# Graphing the training and validation loss for each epoch

plt.figure('Training and Validation Losses per epoch', figsize=(8,8))

plt.plot(history.history['loss'],label='training') # Training data error per epoch.

plt.plot(history.history['val_loss'],label='validation') # Validation error per ep.

plt.grid(True)

plt.legend()

plt.xlabel('Epoch Number')
plt.ylabel('Loss')
plt.show()

model_history = history.history
print(model_history.keys())

validation_accuracy = model_history['val_accuracy']
model_loss = model_history['loss']
validation_loss = model_history['val_loss']
model_accu = model_history['accuracy']
epochs = range(len(model_accu))

#plot of Validation Accuracy and Training Accuracy
plt.figure(figsize = (14,10))
plt.subplot(211)
plt.plot(epochs, validation_accuracy, 'bo', label = 'Validation Accuracy')
plt.plot(epochs, model_accu, 'orange', label = 'Training Accuracy') 
plt.xlabel('Epochs')
plt.ylabel('Accuracy')         
plt.legend()
         
#plot of Validation Loss and Training Loss
plt.figure(figsize = (14,10))
plt.subplot(212)
plt.plot(epochs, validation_loss, 'bo', label = 'Validation Loss')         
plt.plot(epochs, model_loss,'orange', label = 'Training Loss')         
plt.xlabel('Epochs')
plt.ylabel('Loss')         
plt.legend()

plt.show()

# Comparing the model with an unseen/used dataset

print("Performance of network on testing set:")
test_loss,test_acc = model.evaluate(testing_images,categorical_testing_outputs)
print("Accuracy on testing data: {:6.2f}%".format(test_acc*100))
print("Test error (loss):        {:8.4f}".format(test_loss))
print("")

# Reporting the results of the model performance.
print("Performance of network:")
print("Accuracy on training data:   {:6.2f}%".format(history.history['accuracy'][-1]*100))
print("Accuracy on validation data: {:6.2f}%".format(history.history['val_accuracy'][-1]*100))
print("Accuracy on testing data:    {:6.2f}%".format(test_acc*100))

