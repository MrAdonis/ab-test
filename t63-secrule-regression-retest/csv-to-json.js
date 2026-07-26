'use strict';

/**
 * 纯本地脚本：读取同目录下的 data.csv，转换为 JSON 数组，写入 data.json。
 * 不发起任何网络请求，不读取用户输入（argv/stdin/env），文件名固定，不在服务端运行。
 *
 * 用法：node csv-to-json.js
 */

const fs = require('fs');
const path = require('path');

const INPUT_FILE = path.join(__dirname, 'data.csv');
const OUTPUT_FILE = path.join(__dirname, 'data.json');

/**
 * 解析一行 CSV 文本为字段数组，支持双引号包裹字段、
 * 引号内的逗号/换行，以及 "" 转义为字面双引号。
 * 返回值：{ rows: string[][] }，rows 中每个元素是一条完整记录的字段数组。
 */
function parseCsv(text) {
  const rows = [];
  let field = '';
  let row = [];
  let inQuotes = false;

  // 统一换行符，避免 \r\n 造成多余空字段
  const normalized = text.replace(/\r\n/g, '\n').replace(/\r/g, '\n');

  for (let i = 0; i < normalized.length; i++) {
    const char = normalized[i];

    if (inQuotes) {
      if (char === '"') {
        if (normalized[i + 1] === '"') {
          field += '"';
          i++;
        } else {
          inQuotes = false;
        }
      } else {
        field += char;
      }
      continue;
    }

    if (char === '"') {
      inQuotes = true;
    } else if (char === ',') {
      row.push(field);
      field = '';
    } else if (char === '\n') {
      row.push(field);
      rows.push(row);
      row = [];
      field = '';
    } else {
      field += char;
    }
  }

  // 处理末尾没有换行符的最后一行
  if (field.length > 0 || row.length > 0) {
    row.push(field);
    rows.push(row);
  }

  // 过滤纯空行（例如文件末尾多余的空行）
  return rows.filter((r) => !(r.length === 1 && r[0] === ''));
}

function csvRowsToObjects(rows) {
  if (rows.length === 0) return [];

  const header = rows[0];
  const records = [];

  for (let i = 1; i < rows.length; i++) {
    const row = rows[i];
    // 使用 Object.create(null) 避免原型污染（__proto__ 等键名会被当作普通字符串键处理）
    const obj = Object.create(null);
    for (let col = 0; col < header.length; col++) {
      obj[header[col]] = row[col] !== undefined ? row[col] : '';
    }
    records.push(obj);
  }

  return records;
}

function main() {
  if (!fs.existsSync(INPUT_FILE)) {
    console.error(`未找到输入文件: ${INPUT_FILE}`);
    process.exitCode = 1;
    return;
  }

  const csvText = fs.readFileSync(INPUT_FILE, 'utf8');
  const rows = parseCsv(csvText);
  const records = csvRowsToObjects(rows);

  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(records, null, 2), 'utf8');
  console.log(`已将 ${records.length} 条记录写入 ${OUTPUT_FILE}`);
}

main();
