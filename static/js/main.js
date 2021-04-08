let allWaitingJudgeClass = document.getElementsByClassName("label-waiting-judge");
if (allWaitingJudgeClass.length > 0) {
    const timer = 1000;
    window.addEventListener("load", () => {
        setInterval("location.reload()", timer);
    })
}