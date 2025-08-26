"""
敲磚塊遊戲 - 主程式入口點
一個使用 Python 和 Pygame 開發的經典敲磚塊遊戲，具有豐富的視覺效果和音效。

操作說明：
- 滑鼠移動：控制底板位置
- 空白鍵/右鍵：發射球
- 左 Shift：按住時球會加速移動
- ESC：退出遊戲
- R 鍵：重新隨機化磚塊漸層顏色
- Q 鍵：顯示/隱藏操作說明
- 左鍵：切換底板自動模式
- 中鍵：切換物理計算面板顯示
"""

from src.game.game_logic import BrickBreakerGame


def main():
    """主程式入口點"""
    try:
        game = BrickBreakerGame()
        game.run()
    except Exception as e:
        print(f"遊戲運行時發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
