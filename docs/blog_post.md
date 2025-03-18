# OpenAI Agents SDKで作る高度なリサーチアシスタント：ゼロから始める開発ガイド

## はじめに

AIの進化により、私たちの情報収集や分析の方法は劇的に変化しています。特に、複数のAIエージェントが連携して動作するマルチエージェントシステムは、単一のAIでは難しかった複雑なタスクを効率的に処理できるようになりました。

この記事では、OpenAI Agents SDKとFirecrawlを使用して、ウェブリサーチを自動化し、その結果を整理・強化する「リサーチアシスタント」の開発方法を解説します。このアプリケーションは、2つのAIエージェントが連携して動作し、ユーザーが入力したトピックについて包括的なリサーチレポートを生成します。

## 必要な環境とツール

このアプリケーションを開発するには、以下のツールとAPIキーが必要です：

1. **Python 3.8以上**
2. **OpenAI APIキー**：GPT-4などの高度な言語モデルにアクセスするために必要
3. **Firecrawl APIキー**：ウェブ検索と情報収集のために使用
4. **必要なPythonパッケージ**：
   - `openai-agents>=0.0.4`：OpenAI Agents SDK
   - `firecrawl>=0.1.11`：ウェブ検索と情報収集
   - `streamlit>=1.32.0`：WebUIの構築
   - `python-dotenv>=1.0.0`：環境変数の管理

## アプリケーションの構造

このアプリケーションは、以下の3つの主要ファイルで構成されています：

1. **app.py**：メインのStreamlitアプリケーション（UI部分）
2. **my_agents.py**：エージェントの定義
3. **tools.py**：ツール（deep_research）の定義

### エージェントとツールの概要

このアプリケーションには、2つのエージェントと1つのツールがあります：

1. **エージェント**：
   - **Research Agent（Agent 1）**：リサーチを実行し、初期レポートを生成するエージェント
   - **Elaboration Agent（Agent 2）**：初期レポートを受け取り、内容を強化して最終レポートを生成するエージェント

2. **ツール**：
   - **deep_research**：Firecrawl APIを使用してウェブ検索と情報収集を行うツール

## 開発手順

### ステップ1：プロジェクトのセットアップ

まず、プロジェクトディレクトリを作成し、必要なパッケージをインストールします。

```bash
# プロジェクトディレクトリの作成
mkdir deep_research_agent
cd deep_research_agent

# 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# requirements.txtの作成
echo "openai-agents>=0.0.4
firecrawl>=0.1.11
streamlit>=1.32.0
python-dotenv>=1.0.0" > requirements.txt

# パッケージのインストール
pip install -r requirements.txt
```

### ステップ2：.envファイルの作成

APIキーを安全に管理するために、`.env`ファイルを作成します。

```bash
# .envファイルの作成
echo "OPENAI_API_KEY=your_openai_api_key
FIRECRAWL_API_KEY=your_firecrawl_api_key" > .env
```

### ステップ3：ツールの実装（tools.py）

まず、Firecrawlを使用したウェブリサーチツールを実装します。

```python
# tools.py
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
```

### ステップ4：エージェントの実装（my_agents.py）

次に、2つのエージェントを定義します。

```python
# my_agents.py
from agents import Agent

# リサーチエージェント（Agent 1）の定義
def create_research_agent(tools):
    """リサーチを行うエージェントを作成します"""
    return Agent(
        name="research_agent",
        instructions="""あなたは任意のトピックについて詳細な調査を行うリサーチアシスタントです。
        リサーチトピックや質問が与えられたら：
        1. deep_researchツールを使用して包括的な情報を収集してください
        2. このツールはウェブを検索し、複数のソースを分析して情報を統合します
        3. 研究結果をレビューし、整理された構造のレポートにまとめてください
        4. すべての情報源に適切な引用を含めてください
        5. 重要な発見や洞察を強調してください
        """,
        tools=tools,
    )

# 内容強化エージェント（Agent 2）の定義
def create_elaboration_agent():
    """レポートの内容を強化するエージェントを作成します"""
    return Agent(
        name="elaboration_agent",
        instructions="""あなたはリサーチレポートの内容強化を専門とする専門家です。
        リサーチレポートが与えられたら：
        1. レポートの構造と内容を分析してください
        2. 以下の方法でレポートを強化してください：
        - 複雑な概念についてより詳細な説明を追加する
        - 関連する例、ケーススタディ、実世界での応用例を含める
        - 重要なポイントに追加の文脈やニュアンスを加えて展開する
        - ビジュアル要素の説明（チャート、図表、インフォグラフィック）を追加する
        - 最新のトレンドと将来の予測を取り入れる
        - 異なるステークホルダーにとっての実用的な意味を提案する
        3. 学術的厳密さと事実の正確さを維持してください
        4. オリジナルの構造を保ちながら、より包括的にしてください
        5. すべての追加が関連性があり、トピックに価値をもたらすことを確認してください
        """,
    )
```

### ステップ5：メインアプリケーションの実装（app.py）

最後に、Streamlitを使用してメインアプリケーションを実装します。

```python
# app.py
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
```

### ステップ6：アプリケーションの実行

アプリケーションを実行するには、以下のコマンドを使用します：

```bash
streamlit run app.py
```

## アプリケーションの動作フロー

このアプリケーションは、以下の流れで動作します：

1. ユーザーがリサーチトピックを入力し、詳細設定を調整します
2. 「マルチエージェントリサーチを開始」ボタンをクリックすると、リサーチプロセスが開始されます
3. Research Agent（Agent 1）がdeep_researchツールを使用してウェブリサーチを実行し、初期レポートを生成します
4. 初期レポートは展開可能セクションに表示されます
5. Elaboration Agent（Agent 2）が初期レポートを受け取り、内容を強化して最終レポートを生成します
6. 強化されたレポートがメイン画面に表示され、ダウンロードボタンが提供されます

## OpenAI Agents SDKの特徴と利点

OpenAI Agents SDKは、エージェントを単なる関数ではなく、特定の指示や能力を持った自律的なAIアシスタントとして実装することができます。このフレームワークの主な特徴と利点は以下の通りです：

1. **エージェントの自律性**：各エージェントは独自の指示と能力を持ち、特定のタスクに特化することができます
2. **ツールの統合**：エージェントは外部ツール（APIやデータベースなど）を使用して情報を収集・処理できます
3. **マルチエージェント連携**：複数のエージェントが連携して複雑なタスクを処理できます
4. **非同期処理**：`async/await`パターンを使用して効率的に処理を行えます

## まとめ

この記事では、OpenAI Agents SDKとFirecrawlを使用して、ウェブリサーチを自動化し、その結果を整理・強化する「リサーチアシスタント」の開発方法を解説しました。このアプリケーションは、2つのAIエージェントが連携して動作し、ユーザーが入力したトピックについて包括的なリサーチレポートを生成します。

マルチエージェントシステムの開発は、単一のAIでは難しかった複雑なタスクを効率的に処理するための強力なアプローチです。OpenAI Agents SDKを使用することで、エージェントの定義と連携が簡単になり、より高度なAIアプリケーションの開発が可能になります。

ぜひ、このコードをベースに独自のマルチエージェントアプリケーションを開発してみてください。例えば、特定の業界に特化したリサーチエージェントや、異なるタイプの情報源（学術論文、ニュース、SNSなど）を統合するエージェントなど、様々な拡張が考えられます。

## 参考リンク

- [OpenAI Agents SDK公式ドキュメント](https://platform.openai.com/docs/agents)
- [Firecrawl公式サイト](https://firecrawl.dev/)
- [Streamlit公式ドキュメント](https://docs.streamlit.io/)
