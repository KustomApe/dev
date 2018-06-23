window.onload = function(){
  drawSetup($('canvas'),$('canvas2'));
}
var model;
function onFileSelect(e) { var f = e.target.files;
  var reader = new FileReader();
  reader.onload = function(filename){
    var fs = new Float32Stream(reader.result);
    console.log(reader.result);
    model = new Model(fs);
    $('checkButton').disabled = "";
  }
  reader.readAsArrayBuffer(f[0]);
}
$('file').addEventListener('change', onFileSelect, false);

function check() {
  var x = getX($('canvas'));
  var i = model.recognize(x);
  $('result').innerHTML = "Your figure is " + i + "!";
}

function allClear(){
  $('result').innerHTML = "";
  canvasClear($('canvas'));
  canvasClear($('canvas2'));
}

function $(id){
  return document.getElementById(id);
}

