import TkEasyGUI as eg
from icecream import ic

from scr.yaml_sl import load_yaml, save_yaml
from config import CONFIG

'''データ形式
shortcuts:
  play:
    name: 再生
    bind: Alt-p
  loop:
    name: ループ
    bind: Control-Shift-P
  stop:
    name: 停止
    bind: Alt-s
  previous:
    name: 前へ
    bind: Alt-Up
  next:
    name: 次へ
    bind: Alt-Down
  edit:
    name: 書き換え
    bind: Control-Shift-S
  reset:
    name: リセット
    bind: Shift-Alt-s
'''


# --- 設定 ---
MAX_KEYS = 3  # 最大同時押下キー数

# 優先修飾キー
MODIFIER_ORDER = {
    "control_l": 1, "control_r": 1,
    "shift_l": 2, "shift_r": 2,
    "alt_l": 3, "alt_r": 3,
}

# 表示キー名
DISPLAY_NAMES = {
    "control_l": "Control", "control_r": "Control",
    "shift_l": "Shift", "shift_r": "Shift",
    "alt_l": "Alt", "alt_r": "Alt",
    "escape": "Esc", "space": "Space", "return": "Enter",
    "left": "Left", "right": "Right", "up": "Up", "down": "Down",
}

# 既存のショートカット一覧
SHORTCUTS_ALL = [[v['name'], v['bind'].replace('-', '+')] for v in CONFIG['shortcuts'].values()]

# ショートカット名
SHORTCUTS_BIND_NAMES = [item[0] for item in SHORTCUTS_ALL]
# ショートカットキー
SHORTCUTS_BINDS = [item[1] for item in SHORTCUTS_ALL]

# 押されたキーの格納
pressed_keys_list = []
is_finalized = False  # 確定フラグ

def on_key_press(event, window2):
    global is_finalized, pressed_keys_list, SHORTCUTS_BINDS
    
    key_sym = event.keysym.lower()

    # ESCキーが押されたらリセット
    if key_sym == "escape":
        pressed_keys_list = []
        is_finalized = False
        return

    # 確定判定
    # 「修飾キー以外のキー（Enter等）」が押されたら、その瞬間に確定
    if key_sym == "return":

        # シフトが含まれる場合ローマ字を大文字にする等の処理もここで可能
        formatted_keys, current_text = get_current_shortcut_text()
        
        # 空の状態でEnterが押されたら、何もしない or Enterキー単体の登録を防止
        if not pressed_keys_list or any(word in current_text for word in ["Enter", "return"]):
            window2["-REAL_TIME_WARNING-"].update("⚠️ キーを入力してください", text_color="orange")
            ic("⚠️ キーを入力してください")
            return
        
        is_finalized = True
        
        if not any(word == current_text for word in SHORTCUTS_BINDS):
            new_keybind = "-".join(formatted_keys)
            
            sss = window2["-CURRENT-"].get()
            current_index = SHORTCUTS_BIND_NAMES.index(sss)
            
            SHORTCUTS_BINDS[current_index] = new_keybind.replace("+", "-")
            
            window2.post_event("-KEYBIND-ENTER-", {'name': window2["-CURRENT-"].get(), 'bind': new_keybind})
            return
        else:
            window2["-REAL_TIME_WARNING-"].update(f"❌ '{current_text}' は既に使用されています", text_color="red")
            ic(f"❌ '{current_text}' は既に使用されています")

    # 確定済みの状態で新しいキーが押されたら、リストをクリアして新規開始
    # すでに3つ押されている状態で新しいキー(4つ目)が来たら、それを「新しい1つ目」にする
    if is_finalized or len(pressed_keys_list) >= MAX_KEYS:
        pressed_keys_list = []
        is_finalized = False

    # returnを追加しない 重複チェックと最大数制限
    if key_sym != "return" and key_sym not in pressed_keys_list:
        pressed_keys_list.append(key_sym)

    #  修飾キー優先でソート 表示用テキストの整形
    formatted_keys, current_text = get_current_shortcut_text()
    
    # 画面に即時反映
    window2["-KEYBIND-"].update(current_text)
    
        
    if not any(word == current_text for word in SHORTCUTS_BINDS):
        window2["-REAL_TIME_WARNING-"].update("", text_color="gray")
        ic("Enterで確定 / Escでクリア")
    else:
        window2["-REAL_TIME_WARNING-"].update(f"❌ '{current_text}' は既に使用されています", text_color="red")
        ic(f"❌ '{current_text}' は既に使用されています")

def get_current_shortcut_text():
    """表示キーの作成

    Returns:
        _type_: _description_
    """
    global pressed_keys_list
    
    # 4. 修飾キー優先でソート
    sorted_keys = sorted(
        pressed_keys_list, 
        key=lambda k: MODIFIER_ORDER.get(k, 100)
    )

    # 2. Shiftが含まれているかチェック
    has_shift = any("shift" in k for k in pressed_keys_list)
    
    formatted_parts = []
    for k in sorted_keys:
        if k in DISPLAY_NAMES:
            # 修飾キーや特殊キーは定義済みの名前（Ctrl, Alt等）を使用
            formatted_parts.append(DISPLAY_NAMES[k])
        else:
            # 一般キー（文字）の処理
            if has_shift:
                # Shiftが含まれていれば大文字（S）
                formatted_parts.append(k.upper())
            else:
                # Shiftがなければ小文字（s）※お好みでここもupperにする場合が多いです
                formatted_parts.append(k.lower())

    formatted_keys = formatted_parts
    current_text = "+".join(formatted_keys)
    
    return formatted_keys, current_text

def registration(mein_window):
    """ショートカットの書き換えGUI

    Args:
        mein_window (_type_): _description_
    """
    registration_layout = [
        [eg.Text("任意のキーを組み合わせを押して、Enterキーで確定してください。")],
        [eg.Text("Escで終了")],
        [
            eg.Text("変更コマンド:"), 
            eg.Text(mein_window["-TABLE-"].get()[0], key="-CURRENT-"),
            eg.Text(mein_window["-TABLE-"].get()[1])
        ],
        # [eg.Text("キーバインド:"), eg.Input(key="-KEYBIND-", enable_events=True, readonly=True, size=(20,1), expand_x=True)],
        [eg.Input(key="-KEYBIND-", enable_events=True, readonly=True, size=(20,1), expand_x=True)],
        [eg.Text("", key="-NOW_KEY-")],
        [eg.Text("", key="-REAL_TIME_WARNING-")],
    ]
    
    # ウィンドウを表示する
    with eg.Window("Hello App", registration_layout, keep_on_top=True, no_titlebar=True) as window2:
        
        window2.window.bind('<KeyPress>', lambda event: on_key_press(event, window2))
        
        window2["-KEYBIND-"].bind('<Escape>', 'escape')

        # イベントループを処理する
        for event, values in window2.event_iter():
            if event in (None, "Exit", eg.WINDOW_CLOSED, "-KEYBIND-escape"):
                break
            
            if event == "-KEYBIND-ENTER-":
                ic(event, values)
                if not values == "":
                    
                    name_bind = values['name']
                    key_bind = values['bind']
                    
                    # 2. shortcutsの中から「名前」が一致するものを探して書き換える
                    found = False
                    for key, value in CONFIG['shortcuts'].items():
                        if value['name'] == name_bind:
                            CONFIG['shortcuts'][key]['bind'] = key_bind
                            found = True
                            ic(f"Updated: {key} ({name_bind}) -> {key_bind}")
                            save_yaml("setting.yaml", CONFIG)
                            
                            # メインウィンドウに更新を通知
                            mein_window.post_event("-SHORTCUTS-UPDATED-", values)
                            window2.close()

                    if not found:
                        print("対象の名前が見つかりませんでした。")
            
            if event == "-KEYBIND-":
                window2["-NOW_KEY-"].update(f"現在のキー: {values['-KEYBIND-']}")
                

def main():
    """ショートカットキーリストGUI
    """
    global SHORTCUTS_ALL
    # --- 状態管理用の変数 ---
    headings = ["コマンド", "キーバインド"]

    layout = [
        [eg.Table(SHORTCUTS_ALL, headings=headings, key="-TABLE-", justification="left", auto_size_columns=True, enable_events=True)],
    ]

    def bind_exit(e):
        window.post_event("-BIND_EXIT_ESCAPE-", True)
    
    # ウィンドウを表示する
    with eg.Window("キーボード ショートカット", layout) as window:
        
        # ウィンドウをEscで終了バインド
        window.window.bind('<Escape>', lambda e: bind_exit(e))
        
        # イベントループを処理する
        for event, values in window.event_iter():
            if event in (None, "Exit", eg.WINDOW_CLOSED, "-BIND_EXIT_ESCAPE-"):
                break
            
            if event == "-TABLE-":
                try:
                    registration(window)
                except Exception as e:
                    ic(e)
            
            if event == "-SHORTCUTS-UPDATED-":
                # ショートカットリストを再読み込みして表示更新
                SHORTCUTS_ALL = [[v['name'], v['bind'].replace('-', '+')] for v in CONFIG['shortcuts'].values()]
                window["-TABLE-"].update(values=SHORTCUTS_ALL)

if __name__ == "__main__":
    main()