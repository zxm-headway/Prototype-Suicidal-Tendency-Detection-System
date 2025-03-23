
import argparse
def parse_args(args=None):
    parser = argparse.ArgumentParser(
        description='Training and Testing GRU CLASS Models',
        usage='train.py [<args>] [-h | --help]'
    )
    parser.add_argument('--lr', type=float, default=0.001)
    parser.add_argument("--path_texts", type=str, default='./cut_clean_dataset/text_dataset/')
    parser.add_argument("--save_log", type=str, default='./log_record/')
    parser.add_argument("--path_labels", type=str, default='./cut_clean_dataset/text_label/text_label_sort.csv')
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--embed_size", type=int, default=300)
    parser.add_argument("--hidden_size", type=int, default=64)
    parser.add_argument("--dropout", default=0.5, type=float)
    parser.add_argument("--weight_decay", default=1e-6, type=float)
    parser.add_argument("--epochs", default=50, type=int)
    parser.add_argument("--seed", default=42, type=int)
    return parser.parse_args(args)

