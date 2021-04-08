from . import docker
from . import models

def check_answer(submission: models.Submission):
    """submissionのanswerを，すべてのテストケースに対して実行して結果を保存する
    """
    # submissionがacceptされるか
    accepted = True

    # テストケースの取得
    test_cases = models.TestCase.objects.filter(problem=submission.problem)
    for test_case in test_cases:
        # テストの実行
        status, output, error = docker.exec_code_python(
            submission.answer,
            submission.user.username,
            test_case.test_input,
            test_case.test_output,
        )
        # すべての結果のstatusがACでないと，submissionはacceptされない
        if status != "AC":
            accepted = False
            submission.accepted = False
        submission.status = status
        submission.judged_test_case += 1
        submission.save()   # 1つのTestCaseごとにデータベースを更新
        print(test_case, status)
        # TestResultの作成と保存
        test_result = models.TestResult.objects.create(
            submission=submission,
            test_case=test_case,
            status=status,
            output=output,
            error=error,
        )
        test_result.save()  # 保存
    
    print("Accepted:", accepted)

    return accepted
