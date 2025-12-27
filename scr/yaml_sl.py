import yaml

def load_yaml(file_path):
    '''YAMLファイルの読み込み'''
    try:
        with open(file_path, encoding='UTF-8') as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"エラー: ファイルの読み込み中に問題が発生しました: {e}")
        return None

def save_yaml(file_path, data):
    try:
        with open(file_path, 'w', encoding='UTF-8') as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)
        print(f"✅ YAMLファイル '{file_path}' が正常に作成されました。")
    except Exception as e:
        print(f"エラー: ファイルの書き込み中に問題が発生しました: {e}")