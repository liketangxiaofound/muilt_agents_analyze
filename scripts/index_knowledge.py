"""
知识库索引脚本

一次性将 knowledge_docs/ 下的文档分块后录入 ChromaDB。
运行方式: python scripts/index_knowledge.py
"""
import sys
import os

# 确保项目根目录在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.knowledge_base import index_document_file, list_collection_names, get_collection_info

DOCS_MAP = {
    "policies": ["knowledge_docs/government_policies.txt"],
    "finance": ["knowledge_docs/finance_policies.txt"],
    "manual": ["knowledge_docs/platform_manual.txt"],
    "it_policies": ["knowledge_docs/it_policies.txt"],
    "hr_policies": ["knowledge_docs/hr_policies.txt"],
    "procurement": ["knowledge_docs/procurement_policies.txt"],
}


def main():
    print("开始索引知识文档...")
    for collection_name, files in DOCS_MAP.items():
        for file_path in files:
            print(f"  索引 [{collection_name}]: {file_path}")
            result = index_document_file(collection_name, file_path)
            if "error" in result:
                print(f"    错误: {result['error']}")
            else:
                print(f"    完成: 添加 {result['added']} 个文本块")

    print("\n知识库概览:")
    for name in list_collection_names():
        info = get_collection_info(name)
        print(f"  [{name}] 文档块数: {info.get('document_count', 0)}")
    print("索引完成!")


if __name__ == "__main__":
    main()
