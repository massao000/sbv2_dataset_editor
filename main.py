import TkEasyGUI as eg
from icecream import ic
import sounddevice as sd
import soundfile as sf
from pathlib import Path
import time

from scr.yaml_sl import load_yaml, save_yaml
from config import CONFIG
import shortcut_gui

### 音声再生関連の関数 ###
def play_sound(window, values, is_loop=False):
    """音声ファイルを再生する関数"""
    
    p = Path(window["-INPUT-"].get())
    filepath = p.parent / "raw" / window["-AUDIO_LIST-"].get()
    
    try:    
        window["-PLAY-"].update(disabled=True)
        window["-LOOP-"].update(disabled=True)
        window["-STOP-"].update(disabled=False) # stopボタンを有効化
        window["-RESET-"].update(disabled=True)
        window["-EDIT-"].update(disabled=True)
        
        # ファイル読み込み（dataとサンプリングレートfsを取得）
        data, fs = sf.read(filepath)
        if not is_loop:
            # 再生
            sd.play(data, fs)
            # 終了まで待機
            sd.wait()
        else:
            sd.play(data, fs, loop=is_loop)
            
    except Exception as e:
        eg.popup_error(f"音声ファイルの再生に失敗しました。{e}")
        window["-PLAY-"].update(disabled=False)
        window["-LOOP-"].update(disabled=False)
        window["-STOP-"].update(disabled=True) # stopボタンを無効化
        window["-RESET-"].update(disabled=False)
        window["-EDIT-"].update(disabled=False)

def stop_sound(window):
    """再生中の音声を停止する関数"""
    sd.stop()

    window["-PLAY-"].update(disabled=False)
    window["-LOOP-"].update(disabled=False)
    window["-STOP-"].update(disabled=True)
    window["-RESET-"].update(disabled=False)
    window["-EDIT-"].update(disabled=False)

def play_on_click(window, values):
    """一回だけの再生

    Args:
        window (_type_): _description_
        values (_type_): _description_
    """
    params = {
        "window": window,
        "values": values,
        "is_loop": False,
    }
    
    window.start_thread(
        play_sound,
        **params,
        end_key = "-STOP-"
    )

### コンボメニュー切り替え処理 ###
def update_view(window, values, index):
    """画面上のコンボボックス、テキスト、カウンターを一括更新する補助関数"""
    global audio, data, audio_len
    
    # 選択項目を更新
    new_audio_value = audio[index]
    window["-AUDIO_LIST-"].update(value=new_audio_value)
    
    # テキストとカウンターを更新
    window["-TEXT-"].update(data[index]['text'])
    window["-COUNTER-"].update(f"{index + 1:03d}/{audio_len:03d}")

def next(window, values):
    """次の音声に移動する関数"""
    global audio
    # valuesではなく、現在のGUIから直接値を取得する
    current_val = window["-AUDIO_LIST-"].get()
    if not current_val: return
    
    current_index = audio.index(current_val)
    if current_index < len(audio) - 1:
        update_view(window, values, current_index + 1)

def previous(window, values):
    """前の音声に移動する関数"""
    global audio
    # valuesではなく、現在のGUIから直接値を取得する
    current_val = window["-AUDIO_LIST-"].get()
    if not current_val: return
    
    current_index = audio.index(current_val)
    if current_index > 0:
        update_view(window, values, current_index - 1)

### テキスト編集関連の関数 ###
def click_edit():
    """編集テキストの保存"""
    global audio
    
    current_val = window["-AUDIO_LIST-"].get()
    if not current_val: 
        eg.popup_error("音声ファイルが選択されていません。")
        return

    selected_index = audio.index(current_val)
    
    data[selected_index]['text'] = window["-TEXT-"].get()

    # メインデータを更新
    main_data[selected_index] = '|'.join([
        data[selected_index]['wav'],
        data[selected_index]['name'],
        data[selected_index]['lang'],
        data[selected_index]['text']
    ])
    # 読み込んだファイルを書き換える
    with open(values["-INPUT-"], "w", encoding="utf-8") as f:
        for line in main_data:
            f.write(line + '\n')

    eg.popup_auto_close("テキストを更新しました。")
    
def click_reset():
    """テキストのリセット"""
    global audio
    
    current_val = window["-AUDIO_LIST-"].get()
    if not current_val: 
        eg.popup_error("音声ファイルが選択されていません。")
        return
    
    selected_index = audio.index(current_val)
    
    window["-TEXT-"].update(data[selected_index]['text'])


# メニューの定義
menu = [
    # ショートカットを変更できるようにしてもいいかも
    ['設定', ['ショートカット::-SHORTCUT-', 'デフォルトパス::-DEFAULT_PATH-']],
]

key_bind_list = CONFIG.get("shortcuts", {})

key_bind_previous = key_bind_list.get('previous').get('bind') or 'Alt-Up'
key_bind_next = key_bind_list.get('next').get('bind') or 'Alt-Down'
key_bind_play = key_bind_list.get('play').get('bind') or 'Alt-p'
key_bind_loop = key_bind_list.get('loop').get('bind') or 'Alt-l'
key_bind_stop = key_bind_list.get('stop').get('bind') or 'Alt-s'

key_bind_edit = key_bind_list.get('edit').get('bind') or 'Control-Shift-S'
key_bind_reset = key_bind_list.get('reset').get('bind') or 'Control-Shift-S'

# メインレイアウトの定義
layout = [
    [eg.Menu(menu)],
    [
        eg.Input(key="-INPUT-", readonly=True, enable_events=True, expand_x=True), 
        eg.FileBrowse("Browse", file_types=(("LIST Files", "*.list"),), initial_folder=CONFIG.get("DEFAULT_PATH", ".")),
    ],
    [
        eg.Combo([], key="-AUDIO_LIST-", enable_events=True, readonly=True, expand_x=True), 
        eg.Text("000/000", key="-COUNTER-", enable_events=True)
    ],
    [
        eg.Label(f"{key_bind_previous}: 前 / {key_bind_next}: 次"),
    ],
    [
        # ショートカットキーを設定する
        eg.Button(f"再生: {key_bind_play}", key="-PLAY-", expand_x=True), 
        eg.Button(f"ループ: {key_bind_loop}", key="-LOOP-", expand_x=True), 
        eg.Button(f"停止: {key_bind_stop}", key="-STOP-", expand_x=True, disabled=True)
    ],
    [eg.Multiline(key="-TEXT-", expand_x=True, expand_y=True)],
    [
        eg.Button(f"リセット: {key_bind_reset}", key="-RESET-", expand_x=True, disabled=True),
        eg.Button(f"書き換え: {key_bind_edit}", key="-EDIT-", expand_x=True, disabled=True)
    ]
]


# 読み込んだデータを格納する辞書
data = {}

# 音声ファイル名のリスト
audio = []

# 音声ファイルの数
audio_len = 0

CURRENT_IMAGE_INDEX = 0

# 読み込んだデータを格納するリスト
main_data = []

# ウィンドウを表示する
with eg.Window("データ書き換え", layout) as window:
    
    # d = "E:/sbv2/Style-Bert-VITS2/Data/ITAc_amitaro_punsuka_1.0_emo/esd.list"
    # window.post_event("-INPUT-", {"-INPUT-": d})
    # window["-INPUT-"].update(d) # テスト用
    
    # キーバインドの設定
    window.window.bind(f"<{key_bind_previous}>", lambda e: previous(window, values))
    window.window.bind(f"<{key_bind_next}>", lambda e: next(window, values))
    window.window.bind(f"<{key_bind_play}>", lambda e: play_on_click(window, values))
    window.window.bind(f"<{key_bind_loop}>", lambda e: play_sound(window, values, is_loop=True))
    window.window.bind(f"<{key_bind_stop}>", lambda e: stop_sound(window))

    window.window.bind(f"<{key_bind_edit}>", lambda e: click_edit())
    window.window.bind(f"<{key_bind_reset}>", lambda e: click_reset())

    # イベントループを処理する
    for event, values in window.event_iter():
        
        if event in (None, "Exit", eg.WINDOW_CLOSED):
            break
        
        # ファイルを読み込む
        if event == "-INPUT-":
            with open(values["-INPUT-"], "r", encoding="utf-8") as f:
                main_data = [line.rstrip('\n') for line in f]
                # ic(main_data)
            
            # データをパースする
            for i, line in enumerate(main_data):
                parts = line.split('|')
                audio.append(parts[0])
                data[i] = {
                    'wav': parts[0],
                    'name': parts[1],
                    'lang': parts[2],
                    'text': parts[3],
                }
            
            window["-AUDIO_LIST-"].update(value=audio[0])
            window["-AUDIO_LIST-"].update(values=audio)
            window["-TEXT-"].update(data[0]["text"])
            
            # ボタンの有効か
            window["-RESET-"].update(disabled=False)
            window["-EDIT-"].update(disabled=False)
            
            audio_len = len(audio)
            window["-COUNTER-"].update(f"001/{audio_len:03d}")
            
            # window['-AUDIO_LIST-'].focus()
            window['-TEXT-'].focus()
        
        # 音声リストが選択されたとき
        if event == "-AUDIO_LIST-":
            selected_index = audio.index(values["-AUDIO_LIST-"])
            update_view(window, values, selected_index)
        
        ### 音声再生 ###
        if event == "-PLAY-":
            play_on_click(window, values)
            
        if event == "-LOOP-":
            play_sound(window, values, is_loop=True)
        
        if event == "-STOP-":
            stop_sound(window)
        
        
        # テキストをリセットする
        if event == "-RESET-":
            click_reset()
        
        # テキストを書き換える
        if event == "-EDIT-":
            click_edit()
        
        ### 設定メニュー ###
        if event == "-DEFAULT_PATH-":
            new_path = eg.popup_get_folder("デフォルトパスを選択してください。", default_path=CONFIG.get("DEFAULT_PATH", "."))
            if new_path:
                CONFIG["DEFAULT_PATH"] = new_path
                save_yaml("setting.yaml", CONFIG)
                eg.popup_auto_close(f"デフォルトパスを '{new_path}' に更新しました。")
        
        # ショートカット編集画面を開く
        if event == "-SHORTCUT-":
            stop_sound(window)
            
            shortcut_gui.main()
            
            # キーバインドを再設定する
            CONFIG = load_yaml("setting.yaml")
            key_bind_list = CONFIG.get("shortcuts", {})
            
            # 表示の書き換え
            window["-PLAY-"].update(f'再生: {key_bind_list.get("PLAY", {}).get("bind", "Alt-p")}')
            window["-LOOP-"].update(f'ループ: {key_bind_list.get("LOOP", {}).get("bind", "Alt-l")}')
            window["-STOP-"].update(f'停止: {key_bind_list.get("STOP", {}).get("bind", "Alt-s")}')
            window["-RESET-"].update(f'停止: {key_bind_list.get("edit", {}).get("bind", "Control-Shift-S")}')
            window["-EDIT-"].update(f'停止: {key_bind_list.get("reset", {}).get("bind", "Control-Shift-R")}')

            # 古いバインドを削除
            window.window.unbind(f"<{key_bind_previous}>")
            window.window.unbind(f"<{key_bind_next}>")
            window.window.unbind(f"<{key_bind_play}>")
            window.window.unbind(f"<{key_bind_loop}>")
            window.window.unbind(f"<{key_bind_stop}>")
            window.window.unbind(f"<{key_bind_edit}>")
            window.window.unbind(f"<{key_bind_reset}>")
            
            window.window.bind(f"<{key_bind_list.get('previous').get('bind') or 'Alt-Up'}>", lambda e: previous(window, values))
            window.window.bind(f"<{key_bind_list.get('next').get('bind') or 'Alt-Down'}>", lambda e: next(window, values))
            window.window.bind(f"<{key_bind_list.get('play').get('bind') or 'Alt-p'}>", lambda e: play_on_click(window, values))
            window.window.bind(f"<{key_bind_list.get('loop').get('bind') or 'Alt-l'}>", lambda e: play_sound(window, values, is_loop=True))
            window.window.bind(f"<{key_bind_list.get('stop').get('bind') or 'Alt-s'}>", lambda e: stop_sound(window))
            window.window.bind(f"<{key_bind_list.get('edit').get('bind') or 'Control-Shift-S'}>", lambda e: click_edit())
            window.window.bind(f"<{key_bind_list.get('reset').get('bind') or 'Control-Shift-R'}>", lambda e: click_reset())
            