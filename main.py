"""多 Agent 数据分析平台 — FastAPI 入口"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api.api import router as core_router
from app.api.upload import router as upload_router
from app.api.tasks import router as tasks_router
from app.api.reports import router as reports_router
from app.api.knowledge import router as knowledge_router

app = FastAPI(
    title="Multi-Agent Data Analysis Platform",
    version="1.0.0",
    description="通用多 Agent 数据分析平台 — 文件分析 + 知识库问答",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 路由
app.include_router(core_router)
app.include_router(upload_router)
app.include_router(tasks_router)
app.include_router(reports_router)
app.include_router(knowledge_router)

# 静态文件（Vue 前端构建产物）
STATIC_DIR = os.path.join(os.path.dirname(__file__), "app", "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    # SPA fallback: 非 /api 路径返回 index.html
    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        # 放过 api 路径（已由上面的 router 处理，这里只是兜底）
        if full_path.startswith("api/"):
            from fastapi import HTTPException
            raise HTTPException(404, "Not Found")
        index_path = os.path.join(STATIC_DIR, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        from fastapi import HTTPException
        raise HTTPException(404, "Frontend not built. Run: cd frontend && npm run build")


if __name__ == "__main__":
    import uvicorn
    from app.config.setting import settings
    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=True)
