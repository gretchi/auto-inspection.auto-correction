#!/usr/bin/env python3

import os
import logging
import datetime
import re
import glob
import pprint
import shutil
import unicodedata

from openai import OpenAI


PS1 = r"[\u@\h] \W \$"


# 各種path
user_home = os.environ["HOME"]
script_dir = os.path.abspath(os.path.dirname(__file__))
log_dir = os.path.join(script_dir, "logs")
log_file_path = os.path.join(log_dir, datetime.datetime.now().isoformat() + ".log")
problem_dir = os.path.join(script_dir, "problems")

# ワークディレクトリをホームディレクトリへ
os.chdir(user_home)

# ログ
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format='%(levelname)s: %(asctime)s: %(message)s'
)


OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(
    api_key=OPENAI_API_KEY
)

SYSTEM_PROMPT = f"""以下の問題を解決します。

PS1は`{PS1}`が設定されています。


"""


def contents_width(contents: str) -> int:
    """文字列の幅を計算する関数"""
    width_dict = {
        'F': 2,   # Fullwidth
        'H': 1,   # Halfwidth
        'W': 2,   # Wide
        'Na': 1,  # Narrow
        'A': 2,   # Ambiguous
        'N': 1    # Neutral
    }

    east_asian_width_list = [unicodedata.east_asian_width(char) for char in contents]
    width_list = [width_dict[east_asian_width] for east_asian_width in east_asian_width_list]

    return sum(width_list)


def main():
    logging.info("Starting the script...")

    problem_files = []

    for path in glob.glob(os.path.join(problem_dir, "*.txt")):
        problem_file = {
            "path": path,
            "filename": os.path.basename(path),
            "contents": ""
        }

        problem_files.append(problem_file)

    terminal_size = shutil.get_terminal_size()

    print(terminal_size)

    for i, problem_file in enumerate(problem_files):
        contents = ""
        with open(problem_file["path"], "r") as fh:
            contents = fh.read()

        problem_files[i]["contents"] = contents

        contents = re.sub(r"\n", "\\\\n", contents.strip())

        contents_header = ""
        for c in contents:
            contents_header += c

            if contents_width(contents_header) > terminal_size.columns - 4 - 2 - 1:  # 4: "    ", 2: "…" の分
                break

        # if len(contents_header) % 2 == 1:
        #     contents_header += " "

        print(f"{i + 1}: {problem_file['filename']}\n    {contents_header}…")

    # print(problem_files)

    while True:
        print("\n問題番号を入力してください。終了する場合は `q` を入力してください。")
        problem_number = input(f"[1-{len(problem_files)}]> ").strip()
        problem_number = problem_number.encode()

        if problem_number.lower() == "q":
            print("終了します。")
            logging.info("Script terminated by user.")
            return

        if not problem_number.isdigit():
            print("無効な入力です。数字を入力してください。")
            continue

        problem_number = int(problem_number)

        if problem_number < 1 or problem_number > len(problem_files):
            print(f"1から{len(problem_files)}の範囲で入力してください。")
            continue

        break

    system_prompt = SYSTEM_PROMPT + f"問題: {problem_files[problem_number-1]["contents"]}\n"

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=[
            {
                "role": "system", "content": system_prompt
            },
            {
                "role": "user", "content": ""
            }
        ]
    )

    content = completion.choices[0].message.content
    content = content.strip()

    print(content)


if __name__ == "__main__":
    main()
