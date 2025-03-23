
config_data = {
    "lr": 0.001,
    "path_texts": "./cut_clean_dataset/text_dataset/",
    "save_log": "./log_record/",
    "path_labels": "./cut_clean_dataset/text_label/text_label_sort.csv",
    "save_model_path": "../check_point/",
    "batch_size": 16,
    "embedding_dim": 300,
    "gru_size": 100,
    "dropout": 0.5,
    "weight_decay": 1e-6,
    "epochs": 50,
    "class_num": 1,
    "patience": 20,
    "seed": 42
}


class Config:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def load_config(file_path='config.json'):
    return Config(**config_data)