import torch
import os
import numpy as np
import random
from .models.model import GRU_CNN_Attention as models
from .utilsf import  parse_lca as paser


def set_seed(args):
    """
    :param args:
    :return:
    """
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    np.random.seed(args.seed)
    random.seed(args.seed)
    torch.backends.cudnn.deterministic = True


def collate_fn(word_to_idx, texts):
    text_indices = []
    for post in texts:
        if len(post) == 0:
            post_indices = []
        else:
            post_indices = [word_to_idx.get(word, word_to_idx['<UNK>']) for word in post]
        text_indices.append(post_indices)
    max_num_posts = len(text_indices)
    max_num_words = min(200, max((len(post) for post in text_indices), default=1))
    batch_size = 1
    padded_texts = torch.zeros(batch_size, max_num_posts, max_num_words, dtype=torch.long)
    post_masks = torch.zeros(batch_size, max_num_posts, max_num_words, dtype=torch.bool)
    text_masks = torch.zeros(batch_size, max_num_posts, dtype=torch.bool)
    for i, post in enumerate(text_indices):
        num_words = min(len(post), max_num_words)
        if num_words > 0:
            padded_texts[0, i, :num_words] = torch.tensor(post[:num_words])
            post_masks[0, i, :num_words] = 1
        text_masks[0, i] = 1
    return padded_texts, text_masks, post_masks


def main(word_to_idx, texts):
    args = paser.load_config()
    set_seed(args)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    vob_size = len(word_to_idx)
    model = models(args, word_to_idx, vob_size, device=device)
    model = model.to(device)
    model_path = os.path.join(os.path.dirname(__file__), 'model.pth')
    model.load_state_dict(torch.load(model_path))
    padded_texts, text_masks, post_masks = collate_fn(word_to_idx, texts)
    padded_texts = padded_texts.to(device)
    text_masks = text_masks.to(device)
    post_masks = post_masks.to(device)
    model.eval()
    with torch.no_grad():
        output = model(padded_texts, text_masks, post_masks)
    probabilities = torch.sigmoid(output)
    predicted = (probabilities > 0.5).float()
    return predicted

