# SummaryLounge
怠惰な研究者のための論文収集・要約ツール  
完全個人用  

# 機能
- 入力したキーワードに基づいて，Google Scholarや ArXiVで論文PDFを取得
- 生成AI API を用いて，論文の要約を実施
- 論文の要約資料や，論文リストをテーブルにして資料化

## 現状対応
- Google Scholar で 複数キーワードから論文を収集
  - クエリの投げ方はまた考え直す
  - パースが上手くいかずエラー終了する場合がある
- PDF から日本語マークダウンサマリーを出力

## 予定
- GUI対応
- arxiv.org 経由で論文PDFのダウンロード
- CiNiiや，arxivでの検索結果取得
  - 学会名やジャーナル名の表記を統一
- 検索結果と，サマライズ機能の統合
- 論文間キーワードや著者の関連グラフの作成
- LangChain対応


## 参考
LangChainの概要と使い方
https://zenn.dev/umi_mori/books/prompt-engineer/viewer/langchain_overview