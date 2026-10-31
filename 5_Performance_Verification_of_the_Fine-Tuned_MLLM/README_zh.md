# 微调 MLLM 性能验证

[English](README.md)

本目录用于通过 Ollama 调用微调后的 MLLM，完成 Task1、Task2 和 Task3 的性能测试与指标计算。

## 目录结构

```text
5_Performance_Verification_of_the_Fine-Tuned_MLLM/
├── configs/
│   ├── ollama_model.yaml       # Ollama 地址、模型和推理参数
│   └── tasks.yaml              # 任务数据路径
├── scripts/
│   ├── dg_prompt.py            # Ollama 多模态 Prompt
│   ├── performance_test.py     # 微调模型性能测试
│   ├── calculate_metrics.py    # 指标计算
│   └── common.py               # 配置与文件处理
├── results/
│   ├── Task1/
│   │   ├── performance_testing/
│   │   └── metrics/
│   ├── Task2/
│   │   ├── performance_testing/
│   │   └── metrics/
│   ├── Task3/
│   │   ├── performance_testing/
│   │   └── metrics/
│   └── Multi-Task/
│       └── metrics/            # 多任务汇总指标
├── .env.example                # 商业评价模型 API 配置模板
├── README.md
└── README_zh.md
```

## 环境配置

```bash
python -m pip install requests PyYAML openai
ollama serve
```

复制商业评价模型的环境变量模板：

```powershell
Copy-Item .env.example .env
```

在 `.env` 中填写：

```text
COMMERCIAL_MLLM_API_KEY=your-api-key
COMMERCIAL_MLLM_BASE_URL=https://your-api-endpoint/v1
```

`.env` 仅用于 CoT 视觉正确性、逻辑正确性、幻觉率和完全正确率评价，且不会上传到仓库。

模型与 API 地址配置在 `configs/ollama_model.yaml`：

```yaml
ollama:
  api_url: http://127.0.0.1:11434/api/chat
  model: paper_gllm_joint_language_p1280_e300:latest
```

三个任务的 Prompt 组件统一从仓库根目录的 `Prompt_Components` Python 包导入。

确认模型已加载：

```bash
ollama list
```

## Ollama 请求格式

本目录使用 Ollama 原生 `/api/chat` 请求。图片以 Base64 写入消息的 `images` 数组：

```json
{
  "model": "paper_gllm_joint_language_p1280_e300:latest",
  "messages": [
    {
      "role": "user",
      "content": "prompt text",
      "images": ["<base64-image>"]
    }
  ],
  "stream": false,
  "options": {
    "temperature": 0.0,
    "top_p": 0.9
  }
}
```


## 性能测试

运行全部任务：

```bash
python scripts/performance_test.py
```

运行指定任务：

```bash
python scripts/performance_test.py --tasks Task1
```

结果保存在：

```text
results/<Task>/performance_testing/Prompt4/Multi-Task_Fine-tuned_MLLM/
```

## 指标计算

计算全部任务：

```bash
python scripts/calculate_metrics.py
```

单独计算一个任务：

```bash
python scripts/calculate_metrics.py --task Task1
```

CoT 评价会逐样本写入缓存。运行中断后再次执行同一命令，会跳过已完成样本，
从本任务第一条未完成的 CoT 继续。若商业模型暂时不可用，常规指标和当前 CoT
进度仍会保存。

结果保存在：

```text
results/<Task>/metrics/Metrics.csv
results/<Task>/metrics/Metrics_Details.json
results/<Task>/metrics/CoT_Evaluation_Cache.json
```

多任务汇总保存在：

```text
results/Multi-Task/metrics/Metrics.csv
results/Multi-Task/metrics/Metrics_Details.json
```
