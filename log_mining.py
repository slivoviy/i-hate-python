# This script is used in pm4py virtual environment to creat a log graph

import pandas as pd
import numpy as np

df = pd.read_csv('log.csv') 
df.columns = ['time:timestamp', 'milli', 'level', 'case:concept:name', 'concept:name']
df = df.drop(['milli', 'level'], axis=1)

df['time:timestamp'] = pd.to_datetime(df['time:timestamp'])  
df['time:timestamp'] = df['time:timestamp'].astype(np.int64)
df.sort_values('time:timestamp')

from pm4py.objects.conversion.log import converter as log_conv
log = log_conv.apply(df)

from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
heu_net = heuristics_miner.apply_heu(log)

from pm4py.visualization.heuristics_net import visualizer as hn_vis_factory
gviz = hn_vis_factory.apply(heu_net)
hn_vis_factory.view(gviz)
