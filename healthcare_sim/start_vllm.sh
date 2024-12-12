#!/bin/bash

# Environment setup
export MODEL_NAME="hugging-quants/Meta-Llama-3.1-70B-Instruct-AWQ-INT4"
export TENSOR_PARALLEL_SIZE=4
export GPU_MEMORY_UTILIZATION=0.85
export MAX_NUM_BATCHED_TOKENS=512
export QUANTIZATION=awq

# Start vLLM server with OpenAI API compatibility
python -m vllm.entrypoints.openai.api_server \
    --model $MODEL_NAME \
    --tensor-parallel-size $TENSOR_PARALLEL_SIZE \
    --gpu-memory-utilization $GPU_MEMORY_UTILIZATION \
    --max-num-batched-tokens $MAX_NUM_BATCHED_TOKENS \
    --quantization $QUANTIZATION \
    --host "0.0.0.0" \
    --port 8000