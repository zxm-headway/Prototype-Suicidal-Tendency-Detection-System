import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np


class AdaptiveFusion(nn.Module):
    def __init__(self, hidden_size):
        super(AdaptiveFusion, self).__init__()
        self.Wf = nn.Linear(hidden_size, hidden_size)
        self.Wt = nn.Linear(hidden_size, hidden_size)
        self.sigmoid = nn.Sigmoid()

    def forward(self, Vf, Vt):
        lambda_fusion = self.sigmoid(self.Wf(Vf) + self.Wt(Vt))
        Vfuse = (1 - lambda_fusion) * Vf + lambda_fusion * Vt
        return Vfuse


class Attention(nn.Module):
    def __init__(self, hidden_size, batch_first=False):
        super(Attention, self).__init__()
        self.hidden_size = hidden_size
        self.batch_first = batch_first
        self.att_weights = nn.Parameter(torch.Tensor(1, hidden_size), requires_grad=True)
        stdv = 1.0 / np.sqrt(self.hidden_size)
        for weight in self.att_weights:
            nn.init.uniform_(weight, -stdv, stdv)

    def forward(self, inputs, text_masks):
        if self.batch_first:
            batch_size, max_len = inputs.size()[:2]
        else:
            max_len, batch_size = inputs.size()[:2]
        weights = torch.bmm(inputs,
                            self.att_weights
                            .permute(1, 0)
                            .unsqueeze(0)
                            .repeat(batch_size, 1, 1)
                            )
        attentions = torch.softmax(F.relu(weights.squeeze()), dim=-1)
        masked = attentions * text_masks
        _sums = masked.sum(-1).unsqueeze(-1)
        attentions = masked.div(_sums)
        weighted = torch.mul(inputs, attentions.unsqueeze(-1).expand_as(inputs))
        representations = weighted.sum(1).squeeze()
        return representations, attentions


class MultiLayerPerceptron(torch.nn.Module):
    def __init__(self, input_dim, embed_dims, dropout, class_num, output_layer=True):
        super().__init__()
        layers = list()
        for embed_dim in embed_dims:
            layers.append(torch.nn.Linear(input_dim, embed_dim))
            layers.append(torch.nn.BatchNorm1d(embed_dim))
            layers.append(torch.nn.ReLU())
            layers.append(torch.nn.Dropout(p=dropout))
            input_dim = embed_dim
        if output_layer:
            layers.append(torch.nn.Linear(input_dim, class_num))
        self.mlp = torch.nn.Sequential(*layers)

    def forward(self, x):
        result = self.mlp(x)
        return result.squeeze(1)


class GRU_CNN_Attention(nn.Module):
    def __init__(self, args, words_id, vocab_size, device, weights=None, is_pretrain=False):
        super(GRU_CNN_Attention, self).__init__()
        self.args = args
        self.device = device
        self.words_id = words_id
        self.dropout = self.args.dropout
        self.gru_size = self.args.gru_size
        self.class_num = self.args.class_num
        self.embedding_dim = self.args.embedding_dim
        if is_pretrain:
            self.word_embed = nn.Embedding.from_pretrained(weights, freeze=False)
        else:
            self.word_embed = nn.Embedding(vocab_size, self.embedding_dim)
        self.word_gru = nn.GRU(input_size=self.embedding_dim, hidden_size=self.gru_size, num_layers=1,
                               bidirectional=True, batch_first=True)
        self.word_query = nn.Parameter(torch.Tensor(2 * self.gru_size, 1), requires_grad=True)
        self.word_fc = nn.Linear(2 * self.gru_size, 2 * self.gru_size)
        self.sentence_gru = nn.GRU(input_size=2 * self.gru_size, hidden_size=self.gru_size, num_layers=1,
                                   bidirectional=True, batch_first=True)
        self._init_weights()
        self.class_fc = MultiLayerPerceptron(self.gru_size * 4, [self.gru_size * 2, self.gru_size], self.dropout,
                                             self.class_num)
        self.adaptive_fusion = AdaptiveFusion(self.gru_size * 2)
        self.attention = Attention(2 * self.gru_size, batch_first=True)

    def _init_weights(self):
        nn.init.xavier_uniform_(self.word_query)

    def compute_batch_commonality_optimized(self, batch_post_vectors, post_mask, max_recent_posts=35):
        batch_size = batch_post_vectors.size(0)
        embedding_dim = batch_post_vectors.size(2)
        batch_commonality = torch.zeros(batch_size, embedding_dim, device=batch_post_vectors.device)
        leaky_relu = torch.nn.LeakyReLU(negative_slope=0.01)
        for i in range(batch_size):
            post_vectors = batch_post_vectors[i]
            mask = post_mask[i].bool()
            real_post_vectors = post_vectors[mask]
            if real_post_vectors.size(0) <= max_recent_posts:
                recent_posts = real_post_vectors
            else:
                recent_posts = real_post_vectors[-max_recent_posts:]
            l = recent_posts.size(0)
            if l == 0:
                continue
            sum_vector = torch.sum(recent_posts, dim=0)
            sum_of_squares = torch.sum(recent_posts ** 2, dim=0)
            s_pair = (sum_vector ** 2 - sum_of_squares) / (2 * l)
            aggregated_features = leaky_relu(s_pair)
            batch_commonality[i] = aggregated_features
        return batch_commonality

    def forward(self, x, text_masks, post_masks, use_gpu=False):
        batch_size, sentence_num, sentence_len = x.size()
        x = x.view(-1, sentence_len)
        post_masks = post_masks.view(-1, sentence_len)
        word_lengths = post_masks.sum(dim=1)
        non_zero_indices = (word_lengths > 0).nonzero(as_tuple=True)[0]
        if len(non_zero_indices) == 0:
            return torch.zeros(batch_size, self.fc.out_features)
        texts_non_zero = x[non_zero_indices]
        word_lengths_non_zero = word_lengths[non_zero_indices]
        embed_x = self.word_embed(texts_non_zero)
        embed_x_mask = post_masks[non_zero_indices]
        packed_words = nn.utils.rnn.pack_padded_sequence(
            embed_x, word_lengths_non_zero.cpu(), batch_first=True, enforce_sorted=False)
        word_output, word_hidden = self.word_gru(packed_words)
        word_output, lengths = nn.utils.rnn.pad_packed_sequence(word_output, batch_first=True)
        word_attention = torch.tanh(self.word_fc(word_output))
        weights = torch.matmul(word_attention, self.word_query)
        weights = F.softmax(weights, dim=1)
        x = x.unsqueeze(2)
        embed_x_mask = embed_x_mask.unsqueeze(2)
        if use_gpu:
            weights = torch.where(embed_x_mask != 0, weights, torch.full_like(embed_x_mask, 0,
                                                                              dtype=torch.float).cuda())
        else:
            weights = torch.where(embed_x_mask != 0, weights, torch.full_like(embed_x_mask, 0, dtype=torch.float))
        weights = weights / (torch.sum(weights, dim=1).unsqueeze(1) + 1e-4)
        world_hidden = torch.sum(weights * word_output, dim=1)
        pair_post = torch.zeros(batch_size * sentence_num, world_hidden.size(1)).to(self.device)
        pair_post[non_zero_indices] = world_hidden
        pair_vector = pair_post.view(batch_size, sentence_num, world_hidden.size(1))
        commonality = self.compute_batch_commonality_optimized(pair_vector, text_masks)
        post_lengths = text_masks.sum(dim=1)
        non_zero_post_indices = (post_lengths > 0).nonzero(as_tuple=True)[0]
        if len(non_zero_post_indices) == 0:
            return torch.zeros(batch_size, self.class_fc.out_features)
        texts_non_zero = pair_vector[non_zero_post_indices]
        packed_sentences = nn.utils.rnn.pack_padded_sequence(
            texts_non_zero, post_lengths[non_zero_post_indices].cpu(), batch_first=True, enforce_sorted=False)
        sentence_output, sentence_hidden = self.sentence_gru(packed_sentences)
        sentence_output, lengths = nn.utils.rnn.pad_packed_sequence(sentence_output, batch_first=True)
        document_vector, _ = self.attention(sentence_output, text_masks)
        pair_emtion_vectors = self.adaptive_fusion(document_vector, commonality)
        all_user_vectors = torch.cat([pair_emtion_vectors, sentence_output[:, -1, :]],
                                     dim=1)
        document_class = self.class_fc(all_user_vectors)
        return document_class
