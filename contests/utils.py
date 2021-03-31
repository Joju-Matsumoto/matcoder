
day_of_week_to_japanese = {
    "Sun": "日",
    "Mon": "月",
    "Tue": "火",
    "Wed": "水",
    "Thu": "木",
    "Fri": "金",
    "Sat": "土",
}

def check_answer(ans1, ans2):
    """ans1とans2が同じかどうかチェックする
    同じ場合はTrue, そうでない場合はFalseを返す"""
    return ans1.strip() == ans2.strip()