import os
from src.services.analysis_service import analyze_video, find_record_by_filename
from config import OUTPUT_FOLDER, RESULTS_CSV

def test_analyze_video():
    # ここでは実ファイルでなく、テスト用の短い動画を想定
    # 実際にはsample_video.mp4をテスト用に置いておき、簡易な動画を解析
    input_video = "tests/sample_video.mp4"
    player = "Test Player"

    # 前提: sample_video.mp4は静的に用意しておく
    if not os.path.exists(input_video):
        # テスト用ダミー動画がなければスキップ
        return

    result = analyze_video(input_video, player, OUTPUT_FOLDER, RESULTS_CSV)
    assert result["player"] == player
    assert "output_filename" in result
    assert "stroke_cycle_time" in result

    # CSVに書き込まれたかをチェック
    record = find_record_by_filename(result["output_filename"], RESULTS_CSV)
    assert record is not None
