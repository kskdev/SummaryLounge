# GCP(Vertex AI)を使ったGeminiAPIの利用方法(Gemini Advancedの回答)

**1. Vertex AI API の有効化**

* Google Cloud コンソールにアクセスし、プロジェクトを選択します。
* 検索バーで「Vertex AI API」と検索し、API を有効化します。

**2. サービスアカウントの作成**

* Google Cloud コンソールで「IAM と管理」>「サービスアカウント」を選択します。
* 「サービスアカウントを作成」をクリックします。
* サービスアカウント名を入力し、「作成して続行」をクリックします。
* 「ロール」で「Vertex AI ユーザー」を選択し、「続行」をクリックします。
* 「完了」をクリックします。

**3. 認証情報の取得**

* 作成したサービスアカウントの詳細画面で「キー」タブを選択します。
* 「キーを追加」>「JSON」を選択し、「作成」をクリックします。
* JSON ファイルがダウンロードされるので、安全な場所に保管します。

**4. Python 環境の準備**

* Python 3.9 以降がインストールされていることを確認します。
* 以下のライブラリをインストールします。

```bash
pip install google-cloud-aiplatform
```

**5. Python コードの実装**

```python
import vertexai

# 環境変数に認証情報を設定（または、直接パスを指定）
vertexai.init(project="YOUR_PROJECT_ID", location="YOUR_REGION")

# Gemini API の呼び出し（例：テキスト生成）
parameters = {
    "temperature": 0.8,
    "max_output_tokens": 1024,
}
response = vertexai.preview.generate_text(
    model="models/chat-bison",
    prompt="こんにちは！",
    parameters=parameters
)
print(response.text)
```

**補足**

* `YOUR_PROJECT_ID` と `YOUR_REGION` は実際の値に置き換えてください。
* Gemini API のモデルやパラメータは、用途に合わせて調整してください。
* より詳細な情報や最新のドキュメントは、以下の公式リソースをご確認ください。

    * **Vertex AI 公式ドキュメント:** [https://cloud.google.com/vertex-ai/docs](https://cloud.google.com/vertex-ai/docs)
    * **Gemini API リファレンス:** [https://cloud.google.com/vertex-ai/docs/generative-ai/learn/models](https://cloud.google.com/vertex-ai/docs/generative-ai/learn/models)

**注意点**

* Gemini API はまだプレビュー版であり、変更される可能性があります。
* 利用料金が発生する可能性があるので、ご注意ください。

不明な点があれば、お気軽にご質問ください。