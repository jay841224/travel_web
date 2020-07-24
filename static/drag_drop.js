function AllowDrop(event) {
    event.preventDefault();
}
function Drag(event) {
    event.dataTransfer.setData("text/html", event.currentTarget.id);
    console.log(event)
}
function Drop(event) {
    event.preventDefault();
    var data = event.dataTransfer.getData("text/html");
    console.log(123)
    console.log(document.getElementById(data))
    event.currentTarget.appendChild(document.getElementById(data));
}