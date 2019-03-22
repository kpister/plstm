# https://github.com/wabyking/TextClassificationBenchmark/blob/master/models/LSTM.py
# -*- coding: utf-8 -*-

import torch
import torch.nn as nn
from torch import autograd


class LSTMClassifier(nn.Module):
    # embedding_dim, hidden_dim, vocab_size, label_size, batch_size, use_gpu
    def __init__(self,input_dim, hidden_dim, output_dim, device_id='cuda'):
        super().__init__()

        self.device_id = device_id
        self.hidden_dim = hidden_dim
        self.lstm = nn.LSTM(input_dim, hidden_dim)
        self.fc = nn.Linear(hidden_dim, output_dim)

    def init_hidden(self, batch):
        if self.device_id == 'cuda':
            return (autograd.Variable(torch.randn(1, batch, self.hidden_dim)).cuda(),
                    autograd.Variable(torch.randn(1, batch, self.hidden_dim)).cuda())
        return (autograd.Variable(torch.randn(1, batch, self.hidden_dim)),
                autograd.Variable(torch.randn(1, batch, self.hidden_dim)))


    def forward(self, batch_x):
        #<len>,<batch>,<vocab>
        _, (ht, ct) = self.lstm(batch_x, self.init_hidden(batch_x.size(1)))

        try:
            return self.fc(ht[-1])
        except:
            return self.fc(ht[-1])
