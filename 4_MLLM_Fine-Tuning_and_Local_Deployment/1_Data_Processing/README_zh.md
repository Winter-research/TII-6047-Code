# 数据处理

[English](README.md)

## 目录结构

```text
1_Data_Processing/
├── configs/
│   └── image_preprocessing.yaml   # 数据路径、输出路径和目标分辨率
├── scripts/
│   └── resize_images.py           # 图片缩放程序
├── results/
│   └── images/                    # 按原数据集结构保存生成图片
├── README.md
└── README_zh.md
```

## 环境配置

```bash
python -m pip install Pillow PyYAML
```

处理参数位于 `configs/image_preprocessing.yaml`。默认生成 224、448、768 和
1280 四种分辨率，保持图片原始宽高比，不放大小于目标分辨率的图片。

## 运行

```bash
python scripts/resize_images.py
```

生成图片同时保存到以下两个目录：

```text
Data/Sample_Dataset/
1_Data_Processing/results/images/
```

`results/images` 会保留 `Task1`、`Task2`、`Task3` 及其数据集子目录结构。
生成图片在原文件名后添加分辨率后缀，例如 `test_Else_944_p1280.jpg`。
