import os
import datetime
import subprocess
import shutil

from django.conf import settings

def check_same(output1: str, output2: str):
    output1 = output1.replace("\r\n", "\n").replace("\n", " ").strip()
    output2 = output2.replace("\r\n", "\n").replace("\n", " ").strip()
    return output1 == output2

def exec_code_python(code: str, username: str, test_input: str="", test_output: str=""):
    # 設定
    docker_dir = os.path.join(settings.BASE_DIR, "docker")
    # format: container_name, mount_dir, python_file_name
    python_command_template = "docker run -i --rm --name {} -v {}:/usr/src/main -w /usr/src/main python:3.8 python {}"
    # format: container_name
    kill_command_template = "docker kill {}"

    code_id = "{}_{}".format(username, datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    code_dir = os.path.join(docker_dir, code_id)

    # 作業用ディレクトリの作成
    os.mkdir(code_dir)
    
    # main.py(実行用ファイル)の作成
    file_name = "main.py"
    file_path = os.path.join(code_dir, file_name)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)
    
    # dockerコマンドの実行，結果の記録
    exec_cmd = python_command_template.format(code_id, code_dir, file_name)

    status = "AC"
    output = ""
    error = ""
    
    try:
        outputs = subprocess.run(
            exec_cmd, timeout=2.5, shell=True, input=test_input,
            encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        return_code = outputs.returncode
        if return_code == 0:    # 正常終了
            if check_same(outputs.stdout, test_output): # 出力が一致するかチェック
                status = "AC"
            else:
                status = "WA"
        else:   # 異常終了
            status = "RE"
            error = outputs.stdout
    except Exception as e:  # タイムアウト
        kill_cmd = kill_command_template.format(code_id)
        subprocess.run(kill_cmd, shell=True) # コンテナをキルする
        status = "TLE"
        error = "time out error"
    
    # 作業用ディレクトリの削除
    shutil.rmtree(code_dir)
    
    return status, output, error
