import base64
 
from django.shortcuts import render, redirect
from django.views import generic
from django.views.generic import TemplateView
import numpy as np
from dataset.mnist import load_mnist
from two_layer_net import TwoLayerNet
from train_neuralnet import NeuralNetwork
 
# データの読み込み
(x_train, t_train), (x_test, t_test) = load_mnist(normalize=True, one_hot_label=True)

network = TwoLayerNet(input_size=784, hidden_size=50, output_size=10)
z = x_train[0]
y = TwoLayerNet.predict(network, z)
x = np.argmax(y)

print(x)
 
 
class Home(generic.TemplateView):
    template_name = 'main/home.html'