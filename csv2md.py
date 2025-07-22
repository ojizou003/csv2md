#!/usr/bin/env python3
"""
csv2md - CSVファイルをマークダウンテーブルに変換するツール

使用方法:
    python csv2md.py <csvファイル名> [出力ファイル名]
    
例:
    python csv2md.py data.csv
    python csv2md.py data.csv output.md
"""

import csv
import sys
import os
from pathlib import Path


class CSV2MD:
    def __init__(self, input_dir=None, output_dir=None):
        # パス設定（デフォルトは要件定義の固定パス）
        self.input_dir = Path(input_dir) if input_dir else Path("/mnt/c/Users/sinis/Downloads")
        self.output_dir = Path(output_dir) if output_dir else Path("/mnt/c/Users/sinis/Dropbox/Obsidian/00_inbox")
        
    def read_csv(self, csv_filename):
        """CSVファイルを読み込む"""
        csv_path = self.input_dir / csv_filename
        
        if not csv_path.exists():
            raise FileNotFoundError(f"CSVファイルが見つかりません: {csv_path}")
            
        rows = []
        try:
            with open(csv_path, 'r', encoding='utf-8', newline='') as file:
                # CSVの方言を自動検出
                sample = file.read(1024)
                file.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.reader(file, delimiter=delimiter)
                rows = list(reader)
                
        except UnicodeDecodeError:
            # UTF-8で読めない場合はShift_JISを試す
            with open(csv_path, 'r', encoding='shift_jis', newline='') as file:
                sample = file.read(1024)
                file.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.reader(file, delimiter=delimiter)
                rows = list(reader)
                
        return rows
    
    def escape_markdown_chars(self, text):
        """マークダウンで特別な意味を持つ文字をエスケープ"""
        if not isinstance(text, str):
            text = str(text)
        
        # パイプ文字をエスケープ（テーブル区切り文字のため）
        text = text.replace('|', '\\|')
        
        # 改行文字をスペースに置換（テーブル内では改行不可）
        text = text.replace('\n', ' ').replace('\r', ' ')
        
        # 連続するスペースを単一スペースに
        import re
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def convert_to_markdown_table(self, rows):
        """CSVデータをマークダウンテーブルに変換"""
        if not rows:
            return ""
            
        markdown_lines = []
        
        # ヘッダー行（1行目）
        if len(rows) > 0:
            header = rows[0]
            escaped_header = [self.escape_markdown_chars(cell) for cell in header]
            markdown_lines.append("| " + " | ".join(escaped_header) + " |")
            
            # セパレーター行
            separator = ["---"] * len(header)
            markdown_lines.append("| " + " | ".join(separator) + " |")
        
        # データ行（2行目以降）
        for row in rows[1:]:
            # 列数をヘッダーに合わせる
            if len(rows) > 0:
                header_length = len(rows[0])
                # 不足している列を空文字で埋める
                while len(row) < header_length:
                    row.append("")
                # 余分な列は切り捨て
                row = row[:header_length]
            
            escaped_row = [self.escape_markdown_chars(cell) for cell in row]
            markdown_lines.append("| " + " | ".join(escaped_row) + " |")
        
        return "\n".join(markdown_lines)
    
    def save_markdown(self, markdown_content, output_filename):
        """マークダウンファイルを保存"""
        # 出力ディレクトリが存在しない場合は作成
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = self.output_dir / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(markdown_content)
            
        return output_path
    
    def convert(self, csv_filename, output_filename=None):
        """CSVファイルをマークダウンテーブルに変換"""
        try:
            # CSVファイルを読み込み
            print(f"CSVファイルを読み込み中: {csv_filename}")
            rows = self.read_csv(csv_filename)
            
            if not rows:
                print("警告: CSVファイルが空です")
                return None
            
            print(f"読み込み完了: {len(rows)}行, {len(rows[0]) if rows else 0}列")
            
            # マークダウンテーブルに変換
            markdown_content = self.convert_to_markdown_table(rows)
            
            # 出力ファイル名を決定
            if output_filename is None:
                # 拡張子を.mdに変更
                csv_path = Path(csv_filename)
                output_filename = csv_path.stem + ".md"
            
            # ファイルを保存
            output_path = self.save_markdown(markdown_content, output_filename)
            
            print(f"変換完了: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"エラー: {e}")
            return None


def main():
    """メイン関数"""
    if len(sys.argv) < 2:
        print("使用方法: python csv2md.py <csvファイル名> [出力ファイル名]")
        print("例:")
        print("  python csv2md.py data.csv")
        print("  python csv2md.py data.csv output.md")
        sys.exit(1)
    
    csv_filename = sys.argv[1]
    output_filename = sys.argv[2] if len(sys.argv) > 2 else None
    
    converter = CSV2MD()
    result = converter.convert(csv_filename, output_filename)
    
    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()