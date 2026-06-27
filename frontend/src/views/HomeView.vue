<template>
  <div>
    <div class="hero">
      <h1>多 Agent 数据分析</h1>
      <p>上传文件，AI 自动解析、分析并生成交互式报告。也支持知识库语义检索问答。</p>
    </div>

    <div class="mode-cards">
      <router-link to="/analysis" class="mode-card">
        <h3>文件分析</h3>
        <p>上传 Excel、CSV、Word、PDF 文件，选择分析模板，Agent 自动协作完成统计分析、异常检测、趋势预测并生成报告。</p>
        <div class="meta">Excel · CSV · Word · PDF</div>
      </router-link>

      <router-link to="/knowledge" class="mode-card">
        <h3>知识库问答</h3>
        <p>直接从预置知识库中检索答案。每个回答标注来源文档，支持多轮对话追问。</p>
        <div class="meta">6 个知识库 · 语义检索</div>
      </router-link>
    </div>

    <div class="card mt-8">
      <h3 class="card-title">快速开始</h3>
      <div class="grid-2">
        <div>
          <p class="text-muted mb-2">生成样例数据：</p>
          <pre>python scripts/generate_sample_data.py</pre>
        </div>
        <div>
          <p class="text-muted mb-2">可用分析模板：</p>
          <div class="flex flex-wrap gap-2">
            <span class="badge badge-info">数据统计</span>
            <span class="badge badge-info">财务审计</span>
            <span class="badge badge-info">绩效评估</span>
            <span class="badge badge-info">对比分析</span>
            <span class="badge badge-info">文档提取</span>
            <span class="badge badge-info">综合报告</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
