import streamlit as st
from typing import Dict, Any
from agents.tool import function_tool
from firecrawl import FirecrawlApp

@function_tool
async def deep_research(query: str, max_depth: int, time_limit: int, max_urls: int) -> Dict[str, Any]:
    """
    Firecrawlのディープリサーチエンドポイントを使用して包括的なウェブリサーチを実行します。
    """
    try:
        # セッション状態からAPIキーを使用してFirecrawlAppを初期化
        firecrawl_app = FirecrawlApp(api_key=st.session_state.firecrawl_api_key)

        # リサーチパラメータを定義
        params = {"maxDepth": max_depth, "timeLimit": time_limit, "maxUrls": max_urls}

        # リアルタイム更新のためのコールバックを設定
        def on_activity(activity):
            st.write(f"[{activity['type']}] {activity['message']}")

        # ディープリサーチを実行
        with st.spinner("詳細なリサーチを実行中..."):
            results = firecrawl_app.deep_research(query=query, params=params, on_activity=on_activity)

        return {
            "success": True,
            "final_analysis": results["data"]["finalAnalysis"],
            "sources_count": len(results["data"]["sources"]),
            "sources": results["data"]["sources"],
        }
    except Exception as e:
        st.error(f"リサーチエラー: {str(e)}")
        return {"error": str(e), "success": False}
