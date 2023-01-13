import torch.nn as nn
import torch.nn.functional as F
from dgl.nn.pytorch import GraphConv


# build a two-layer GCN with ReLU as the activation in between
class GCN(nn.Module):
    def __init__(self, in_feats, h_feats, num_classes):
        super(GCN, self).__init__()
        self.gcn_layer1 = GraphConv(in_feats, h_feats)
        self.gcn_layer2 = GraphConv(h_feats, num_classes)

    def forward(self, graph, inputs):
        h = self.gcn_layer1(graph, inputs)
        h = F.relu(h)
        h = self.gcn_layer2(graph, h)
        return h
