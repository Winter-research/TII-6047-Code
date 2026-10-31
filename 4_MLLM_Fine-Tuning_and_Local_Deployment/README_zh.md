# MLLM 微调与本地部署

[English](README.md)

## 目录结构

```text
4_MLLM_Fine-Tuning_and_Local_Deployment/
├── configs/
│   ├── training/
│   │   └── Multi-Task_Fine-tuned_MLLM.yaml   # LoRA 微调配置
│   └── export/
│       └── Multi-Task_Fine-tuned_MLLM.yaml   # 模型合并与导出配置
├── scripts/
│   ├── 01_train_lora.sh                      # 启动 LoRA 微调
│   ├── 02_check_training.sh                  # 检查训练结果和 Checkpoint
│   ├── 03_export_model.sh                    # 合并并导出完整模型
│   └── 04_create_ollama_model.sh             # 注册 Ollama 模型
├── results/
│   └── Exported_Model_Files.txt               # LLaMA-Factory 导出文件清单
├── README.md
└── README_zh.md
```

## 环境配置

安装 [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory) 和
[Ollama](https://github.com/ollama/ollama)。以下脚本均在 LLaMA-Factory 根目录运行。

将配置文件复制到 LLaMA-Factory：

```bash
cp /path/to/TII-6047-Code/4_MLLM_Fine-Tuning_and_Local_Deployment/configs/training/Multi-Task_Fine-tuned_MLLM.yaml examples/train_lora/
cp /path/to/TII-6047-Code/4_MLLM_Fine-Tuning_and_Local_Deployment/configs/export/Multi-Task_Fine-tuned_MLLM.yaml examples/merge_lora/
```

在 `data/dataset_info.json` 中注册 `Multi-Task_Fine-Tuning_Dataset.json`，
注册名称需与训练配置中的 `dataset` 字段一致。

## 运行

```bash
bash /path/to/TII-6047-Code/4_MLLM_Fine-Tuning_and_Local_Deployment/scripts/01_train_lora.sh
bash /path/to/TII-6047-Code/4_MLLM_Fine-Tuning_and_Local_Deployment/scripts/02_check_training.sh
bash /path/to/TII-6047-Code/4_MLLM_Fine-Tuning_and_Local_Deployment/scripts/03_export_model.sh
bash /path/to/TII-6047-Code/4_MLLM_Fine-Tuning_and_Local_Deployment/scripts/04_create_ollama_model.sh
```

Ollama 模型名称为：

```text
paper_gllm_joint_language_p1280_e300:latest
```

模型权重不上传到本仓库。LLaMA-Factory 合并导出后的文件清单记录在
`results/Exported_Model_Files.txt`。

