function mouseMove(ev) {
    Ev = ev || window.event;
    var mousePos = mouseCoords(ev);
    //获取当前的x,y坐标
    document.getElementById("mouseX").innerText = mousePos.x;
    document.getElementById("mouseY").innerText = mousePos.y;
}
function mouseCoords(ev) {
    //鼠标移动的位置
    if (ev.pageX || ev.pageY) {
        return { x: ev.pageX, y: ev.pageY };
    }
    return {
        x: ev.clientX + document.body.scrollLeft - document.body.clientLeft,
        y: ev.clientY + document.body.scrollTop - document.body.clientTop
    };
}
document.onmousemove = mouseMove;