const { app, BrowserWindow } = require('electron')
const ipc = require('electron').ipcMain




const express = require('express');
const expressApp = express();
const http = require('http').Server(expressApp);


var bodyParser = require("body-parser");
var win;
/*var app = require("express")();
var http = require("http").Server(app);*/
var aaa = 1;





function createWindow() {
    let win = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true, 
            contextIsolation: false,
        },
        fullscreen: true
    })
    win.loadFile('../main.html');



    // Emitted when the window is closed.
    win.on('closed', function () {
        win = null;
    })


    expressApp.use(bodyParser.json())

    expressApp.post("/", function (req, res) {
        var equipe = req.body.equipe;
        var points = req.body.points;
        console.log("python: " + equipe + "," + points);
        
        dico = { "equipe": equipe, "points": points };
        console.log(win.webContents)

        win.webContents.send('some_js_Method', dico);
        res.send('OK');
    });

    //update_score(team_id, point_scored)

    http.listen(3000, function () {
        console.log("listening...");
    });


}

app.on('ready', createWindow)


// Quit when all windows are closed.
app.on('window-all-closed', function () {
    // On OS X it is common for applications and their menu bar
    // to stay active until the user quits explicitly with Cmd + Q
    if (process.platform !== 'darwin') {
        app.quit()
    }
})
