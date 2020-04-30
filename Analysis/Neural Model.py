import torch
import pandas as pd
import matplotlib.pyplot as plt
import gc
import pickle
import numpy as np
from tqdm import tqdm
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from torch.nn import Embedding
from torch.autograd import Variable
from torch.nn import GRU
from scipy import optimize
import pulp

from lenskit.datasets import MovieLens
from lenskit.algorithms.basic import Bias
from lenskit.batch import predict
from lenskit.metrics.predict import rmse

from lenskit.datasets import ML100K
from lenskit import batch, topn, util
from lenskit import crossfold as xf
from lenskit.algorithms import Recommender, als, item_knn as knn
from lenskit import topn

util.load_ml_ratings()