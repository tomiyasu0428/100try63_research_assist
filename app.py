import asyncio
import streamlit as st
import os
from dotenv import load_dotenv
from agents import Runner, set_default_openai_key
from tools import deep_research
from my_agents import create_research_agent, create_elaboration_agent

# .envファイルが存在する場合は読み込む
load_dotenv()

# ページ設定
st.set_page_config(page_title="高度リサーチアシスタント", page_icon="🔍", layout="wide")

# APIキーのセッション状態を初期化
if "openai_api_key" not in st.session_state:
    st.session_state.openai_api_key = os.getenv("OPENAI_API_KEY", "")
if "firecrawl_api_key" not in st.session_state:
    st.session_state.firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY", "")

# サイドバーにAPIキー設定
with st.sidebar:
    st.title("API設定")
    openai_api_key = st.text_input("OpenAI APIキー", value=st.session_state.openai_api_key, type="password")
    firecrawl_api_key = st.text_input(
        "Firecrawl APIキー", value=st.session_state.firecrawl_api_key, type="password"
    )
    if openai_api_key:
        st.session_state.openai_api_key = openai_api_key
        set_default_openai_key(openai_api_key)
    if firecrawl_api_key:
        st.session_state.firecrawl_api_key = firecrawl_api_key

# メインコンテンツ
st.title("🔍 リサーチエージェント")
st.markdown("このマルチエージェントシステムはOpenAI Agents SDKとFirecrawlを使用して包括的なリサーチを行います")

# リサーチトピック入力
research_topic = st.text_input("リサーチトピックを入力してください:", placeholder="例: AIの最新動向")

# 詳細設定の展開可能セクション
with st.expander("詳細設定"):
    col1, col2, col3 = st.columns(3)
    with col1:
        max_depth = st.slider(
            "リサーチの深さ",
            min_value=1,
            max_value=5,
            value=3,
            help="値が高いほど詳細なリサーチが行われますが、時間がかかります",
        )
    with col2:
        time_limit = st.slider(
            "時間制限（秒）",
            min_value=60,
            max_value=300,
            value=180,
            help="リサーチの最大時間（秒）",
        )
    with col3:
        max_urls = st.slider(
            "検索するURL数の上限",
            min_value=5,
            max_value=20,
            value=10,
            help="分析するURLの最大数",
        )


async def run_research_process(topic: str, max_depth: int, time_limit: int, max_urls: int):
    """完全なマルチエージェントリサーチプロセスを実行します。"""
    # エージェントの作成
    research_agent = create_research_agent([deep_research])
    elaboration_agent = create_elaboration_agent()
    # ステップ1: 最初のエージェントによる初期リサーチ
    with st.spinner("エージェント1: 初期リサーチを実行中..."):
        research_prompt = f"""
        以下のトピックについて詳細なリサーチを行ってください: {topic}
        以下のパラメータでdeep_researchツールを使用してください:
        - max_depth: {max_depth}
        - time_limit: {time_limit}
        - max_urls: {max_urls}
        
        あなたの発見を整理された構造のレポートにまとめてください。
        """
        research_result = await Runner.run(research_agent, research_prompt)
        initial_report = research_result.final_output

    # 初期レポートを表示するセクション
    # 初期レポートを展開可能セクションに表示
    with st.expander("初期リサーチレポートを表示（エージェント1の出力）"):
        st.markdown(initial_report)

    # ステップ2: 2番目のエージェントによるレポートの強化
    with st.spinner("エージェント2: 追加情報でレポートを強化中..."):
        elaboration_input = f"""
        リサーチトピック: {topic}
        初期リサーチレポート:
        {initial_report}
        このリサーチレポートに追加情報、例、ケーススタディ、より深い洞察を加えて強化してください。
        学術的厳密さと事実の正確さを維持してください。
        """
        elaboration_result = await Runner.run(elaboration_agent, elaboration_input)
        enhanced_report = elaboration_result.final_output

    return enhanced_report


# メインリサーチプロセス
if st.button(
    "マルチエージェントリサーチを開始", disabled=not (openai_api_key and firecrawl_api_key and research_topic)
):
    if not openai_api_key or not firecrawl_api_key:
        st.warning("サイドバーに両方のAPIキーを入力してください。")
    elif not research_topic:
        st.warning("リサーチトピックを入力してください。")
    else:
        try:
            # 最終レポート用のプレースホルダーを作成
            report_placeholder = st.empty()

            # ステータスコンテナ
            status_container = st.container()
            with status_container:
                st.subheader("リサーチ状況:")

            # マルチエージェントリサーチプロセスを実行
            enhanced_report = asyncio.run(
                run_research_process(research_topic, max_depth, time_limit, max_urls)
            )

            # 強化されたレポートを表示
            report_placeholder.markdown("## 強化されたリサーチレポート（マルチエージェント出力）")
            report_placeholder.markdown(enhanced_report)

            # ダウンロードボタンを追加
            st.download_button(
                "レポートをダウンロード",
                enhanced_report,
                file_name=f"{research_topic.replace(' ', '_')}_report.md",
                mime="text/markdown",
            )
        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")

# フッター
st.markdown("---")
st.markdown(
    "OpenAI Agents SDKとFirecrawlを活用 - サブスクリプション料金なしであなた自身のディープリサーチソリューション"
)
