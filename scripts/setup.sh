#!/bin/bash
# ============================================================
# Multi-Agent 平台一键初始化脚本
# 1. 生成样例数据
# 2. 索引知识库到 ChromaDB
# ============================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "========================================"
echo "  Multi-Agent Platform Setup"
echo "========================================"
echo ""

# Step 1: 样例数据
echo "[1/2] 生成样例数据..."
python scripts/generate_sample_data.py
echo ""

# Step 2: 知识库索引
echo "[2/2] 索引知识文档到 ChromaDB..."
python scripts/index_knowledge.py
echo ""

echo "========================================"
echo "  初始化完成！"
echo "  启动服务: python run.py"
echo "========================================"
