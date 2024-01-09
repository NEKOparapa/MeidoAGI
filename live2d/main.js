//导入（es6写法）
//import { app, BrowserWindow } from 'electron'

//导入（es5写法）
const {  app, BrowserWindow, ipcMain } = require('electron')  //需要额外安装electron

 
//分函数：创建窗口并加载html
function createWindow () {
  const win = new BrowserWindow({
    width: 350,    // 设置整体应用窗口的宽高，相当于底板大小
    height: 380,
    resizable: false, // 禁用鼠标调整窗口大小功能
    transparent: true,     // 设置窗口透明
    frame: false,          // 禁用默认的窗口框架
    alwaysOnTop: true,     // 设置窗口总是在最前
    webPreferences: {    // 设置渲染进程的一些参数
      nodeIntegration: true,   // 是否集成node，默认为false
      contextIsolation: false,  // 是否隔离上下文，默认为true，建议保持默认
      defaultEncoding: 'UTF-8'  // 添加此行
    }
  })

  win.loadFile('index.html')    // 展示的网页文件

}

//主进程的启动时的事件
app.whenReady().then(createWindow)



//用户信息输出
ipcMain.on('USER', (event, data) => {
    console.log('【用户信息】:', data);
});

//助手消息输出
ipcMain.on('AI', (event, data) => {
  console.log('【AI信息】:', data,"\n");
});

//错误消息输出
ipcMain.on('DEBUG', (event, data) => {
  console.log('【DEBUG】:', data,"\n");
});



