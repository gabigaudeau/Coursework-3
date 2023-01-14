import torch.nn as nn
import dgl.function as fn


# build a two-layer GCN with ReLU as the activation in between
class HeteroRGCNLayer(nn.Module):
    def __init__(self, in_size, out_size, edge_types):
        super(HeteroRGCNLayer, self).__init__()
        # W_r for each relation
        self.weight = nn.ModuleDict({
                name: nn.Linear(in_size, out_size) for name in edge_types
            })

    def forward(self, dataset, feat_dict):
        # The input is a dictionary of node features for each type
        funcs = {}
        for src_type, edge_type, dst_type in dataset.canonical_etypes:
            # Compute W_r * h
            weights = self.weight[edge_type](feat_dict[src_type])
            # Save it in graph for message passing
            dataset.nodes[src_type].data['Wh_%s' % edge_type] = weights
            # Specify per-relation message passing functions: (message_func, reduce_func).
            # Note that the results are saved to the same destination feature 'h', which
            # hints the type wise reducer for aggregation.
            funcs[edge_type] = (fn.copy_u('Wh_%s' % edge_type, 'm'), fn.mean('m', 'h'))
        # Trigger message passing of multiple types.
        # The first argument is the message passing functions for each relation.
        # The second one is the type wise reducer, could be "sum", "max",
        # "min", "mean", "stack"
        dataset.multi_update_all(funcs, 'sum')
        # return the updated node feature dictionary
        return {ntype: dataset.nodes[ntype].data['h'] for ntype in dataset.ntypes}