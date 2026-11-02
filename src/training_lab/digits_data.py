"""划分训练、验证和测试集"""

import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

def load_splits():
    digits = load_digits()

    # 数据像素范围是0到16，用固定范围归一化。
    x = digits.data.astype(np.float32) / 16.0
    y = digits.target.astype(np.int64)

    x_rest, x_test, y_rest, y_test = train_test_split(
        x,
        y,
        test_size=0.2, # 20%测试
        random_state=42,
        stratify=y,
    )

    x_train, x_val, y_train, y_val = train_test_split(
        x_rest,
        y_rest,
        train_size=0.25, # 80% * 25% = 20%验证，剩余60%训练
        random_state=42,
        stratify=y_rest,
    )

    return {
        "train": (x_train, y_train),
        "validation": (x_val, y_val),
        "test": (x_test, y_test),
    }