#!/usr/bin/env node
'use strict';

/**
 * build_single.js
 *
 * ServiceNow CSA 学習アプリを、スマホ単体で開ける単一HTMLファイルにビルドする。
 * index.html 内の <script src="questions.js"></script> を、
 * questions.js の中身を埋め込んだ <script>...</script> に置換し、
 * csa_single.html として出力する。
 *
 * 実行方法: node build_single.js
 */

const fs = require('fs');
const path = require('path');

const APP_DIR = __dirname;
const INDEX_HTML_PATH = path.join(APP_DIR, 'index.html');
const QUESTIONS_JS_PATH = path.join(APP_DIR, 'questions.js');
const OUTPUT_PATH = path.join(APP_DIR, 'csa_single.html');

const SCRIPT_TAG_RE = /<script\s+src=["']questions\.js["']\s*><\/script>/;

function main() {
  let indexHtml;
  try {
    indexHtml = fs.readFileSync(INDEX_HTML_PATH, 'utf8');
  } catch (err) {
    console.error(`Error: failed to read ${INDEX_HTML_PATH}: ${err.message}`);
    process.exit(1);
  }

  let questionsJs;
  try {
    questionsJs = fs.readFileSync(QUESTIONS_JS_PATH, 'utf8');
  } catch (err) {
    console.error(`Error: failed to read ${QUESTIONS_JS_PATH}: ${err.message}`);
    process.exit(1);
  }

  if (!SCRIPT_TAG_RE.test(indexHtml)) {
    console.error(
      'Error: could not find <script src="questions.js"></script> in index.html. Aborting build.'
    );
    process.exit(1);
  }

  const inlineScript = `<script>\n${questionsJs}\n</script>`;
  // 第2引数を関数にすることで、置換文字列中の $& / $' / $` / $$ が
  // 特殊パターンとして解釈されるのを防ぐ(questions.js に $ を含む場合の破損対策)
  const outputHtml = indexHtml.replace(SCRIPT_TAG_RE, () => inlineScript);

  try {
    fs.writeFileSync(OUTPUT_PATH, outputHtml, 'utf8');
  } catch (err) {
    console.error(`Error: failed to write ${OUTPUT_PATH}: ${err.message}`);
    process.exit(1);
  }

  console.log(`Built ${OUTPUT_PATH}`);
}

main();
