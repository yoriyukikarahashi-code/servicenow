# 新資格版 学習アプリ構築プレイブック

このリポジトリの学習アプリ(CSA版)を別の資格に横展開するための完全な手順書。
**特定のLLMやツールに依存せず**、任意のLLM(Claude/GPT/Gemini等)または手作業で再現できる。

## アーキテクチャ

```
servicenow/
├── template/app_template.html   # アプリの器(全資格共通・変更不要)
├── certs/<cert_id>/             # 資格ごとのコンテンツ(ここだけ作る)
│   ├── config.json              # タイトル・分野構成・配点
│   ├── notes/*.md               # 分野別ノート(Markdown)
│   └── questions.js             # 問題データ
├── tools/build.py               # ビルドスクリプト
├── app/<cert_id>_single.html    # 生成物(GitHub Pagesで配信)
└── docs/NEW_CERT_PLAYBOOK.md    # このファイル
```

- 生成物は**完全単一HTMLファイル**。CDN・外部リソースなし。オフライン動作。
- 進捗はlocalStorageに保存。`storage_prefix` を資格ごとに変えることで混在しない。
- テンプレートには出題エンジン・模擬試験・弱点復習(間隔反復)・Markdownレンダラー・
  ダーク/ライトテーマ・スマホ対応が実装済み。**コンテンツ以外は作る必要がない**。

## 構築手順

### Step 1: 試験ガイドの調査

対象資格の公式試験ガイド(Exam Blueprint)を入手し、以下を確定する:
- 分野(ドメイン)の一覧と配点(%)
- 各分野の出題トピック
- 対象製品のバージョン(例: Zurichリリース)

### Step 2: config.json 作成

`certs/csa/config.json` をコピーして編集:

```json
{
  "cert_id": "cad",
  "app_title": "ServiceNow CAD 学習システム",
  "app_subtitle": "Certified Application Developer 試験対策",
  "version_badge": "PDI: Zurich リリース準拠",
  "storage_prefix": "cad",
  "output_single": "cad_single.html",
  "domains": [
    { "id": 1, "label": "...", "weight": 15, "note": "01_xxx.md" }
  ]
}
```

注意:
- `storage_prefix` は既存資格と重複させない(進捗データが混ざる)
- `version_badge` には準拠バージョンを明記(教材の鮮度をユーザーが判断できる)

### Step 3: ノート作成 (notes/*.md)

各分野1ファイル。**CSA版のノート(certs/csa/notes/)を書式サンプルとして参照する**こと。
各ノートに必ず含めるセクション:

1. `# 分野N: <名前>(配点 X%)` — 見出し
2. 番号付きセクション — 概念説明(コード例・テーブル名を具体的に)
3. `## 全体構造マップ` — ASCII図で概念の関係を図解
4. `## PDI 操作ガイド` — 実機(Personal Developer Instance)での演習タスク5個前後。
   ナビゲーションパス(`All → System Definition → ...`)を明記
5. `## 試験との接続` — 「試験でこう問われたらこう答える」のQ&A形式

Markdown対応記法: 見出し(#〜###)、リスト(ネスト可)、**太字**、`コード`、
コードブロック(```)、表、水平線。

LLMに書かせる場合のプロンプト例:

```
ServiceNow <資格名> 試験の分野「<分野名>」(配点X%)の学習ノートを
Markdownで書いてください。試験ガイドのトピック: <トピック列挙>。
必須セクション: 概念説明(テーブル名・API名を具体的に)/全体構造マップ(ASCII図)/
PDI操作ガイド(実機演習5タスク・ナビゲーションパス明記)/試験との接続(Q&A形式)。
準拠バージョン: <リリース名>。日本語で。
```

### Step 4: 問題作成 (questions.js)

`certs/csa/questions.js` の構造をそのまま踏襲:

```javascript
const DOMAINS = {
  1: { name: "...", weight: 15 },
};

const QUESTIONS = [
  {
    id: 101, domain: 1,
    q: "問題文",
    choices: ["選択肢1", "選択肢2", "選択肢3", "選択肢4"],
    answer: [0],          // choicesのインデックス。複数正解は [0, 2] のように
    expl: "解説。正解の根拠と、誤答選択肢がなぜ違うかを両方書く"
  },
];
```

規約:
- idは `分野番号 * 100 + 連番`(例: 分野3の12問目 = 312)。**重複禁止**
- 1分野あたり最低15問、配点の高い分野は多めに(CSA版は27%分野に67問)
- 複数選択問題には問題文に「(複数選択)」を付ける
- explは「なぜ正解か」+「なぜ他が誤りか」の両方を書く

### Step 5: 品質監査(最重要)

**作りっぱなしにしない。** CSA版で実際に見つかった欠陥の類型:
- 正解自体が間違っている(技術仕様の誤解)
- 旧UI前提の操作手順(例:「歯車アイコン」→ 正しくは右クリック→Configure)
- 非推奨機能を現役として記述(例: gs.log、Connect Chat、Agent Workspace)
- テーブル名の誤り(例: catalog_ui_policy を sc_cat_item_gui_policy と誤記)
- 出題範囲のカバレッジ欠落(重要トピックの問題が0問)

監査プロンプト(LLMに分野ごとに投げる):

```
以下のServiceNow <資格名> 試験対策の問題データを監査してください。
各問題について: (1)正解が技術仕様として本当に正しいか (2)解説が正確か
(3)選択肢に曖昧さがないか (4)最新リリース(<リリース名>)のUI・仕様に即しているか。
問題のあるものだけ「id/問題点/修正案」で列挙。
[questions.jsの該当分野を貼る]
```

さらに:
- 監査は**コンテンツ全体をカバーしているか必ず確認**する(ファイルの一部だけ
  読んで「全問OK」と報告される事故がCSA版で実際に起きた)
- 疑わしい指摘はWeb検索で公式ドキュメント・KBを確認して裏取りする
  (監査LLMの指摘自体が間違っていることもある。CSA版ではUpdate Setと
  ダッシュボードの関係で監査側が誤指摘した)
- ノート本文も同じ観点で監査する

### Step 6: ビルドと検証

```bash
python3 tools/build.py <cert_id>
```

チェックリスト:
- [ ] ID重複なし・answer範囲OK(build.pyが自動チェック)
- [ ] 生成HTMLにプレースホルダ `{{...}}` が残っていない
- [ ] 全分野のノートが表示される(ブラウザで確認)
- [ ] スマホ幅(390px)で横スクロールが発生しない
- [ ] 模擬試験・分野別練習・弱点復習が動作する
- [ ] localStorageのキーが他資格と衝突していない

### Step 7: デプロイ

```bash
git add certs/<cert_id> app/<cert_id>_single.html
git commit -m "feat: add <cert_id> study app"
git push origin main
```

GitHub Pagesが有効なので、プッシュ後数分で
`https://<user>.github.io/servicenow/app/<cert_id>_single.html` で配信される。
スマホでキャッシュが残る場合はバージョンバッジの文言を変えて確認する。

## テンプレート(器)を修正する場合

`template/app_template.html` を編集 → `python3 tools/build.py --all` で
全資格を再ビルド。器の修正が全資格に一括反映される。

CSSの重要な既知対応(壊さないこと):
- `*, *::before, *::after { box-sizing: border-box }` — 幅あふれ防止
- `.study-layout > *:last-child { min-width: 0 }` — グリッド1frの縮小許可
- `.note-body code { word-break: break-all }` — インラインコードの折返し
- モバイルbreakpointは768px
