import * as vscode from 'vscode';

export const getChatTemplate = async (webview: vscode.Webview, extensionUri: vscode.Uri) => {
    const styleUri = webview.asWebviewUri(vscode.Uri.joinPath(extensionUri, 'src', 'templates', 'chat.css'));
    const scriptUri = webview.asWebviewUri(vscode.Uri.joinPath(extensionUri, 'src', 'templates', 'chat.js'));
    const htmlUri = vscode.Uri.joinPath(extensionUri, 'src', 'templates', 'chat.html');
    
    const htmlContent = await vscode.workspace.fs.readFile(htmlUri);
    
    return `
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link href="${styleUri}" rel="stylesheet">
                <title>Dev AI Chat</title>
            </head>
            <body>
                ${Buffer.from(htmlContent).toString('utf8')}
                <script src="${scriptUri}"></script>
            </body>
        </html>
    `;
};