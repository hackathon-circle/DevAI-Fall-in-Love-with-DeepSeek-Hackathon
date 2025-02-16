import * as vscode from 'vscode';
import { GroqService } from './services/groqService';
import { MessageHandler } from './services/messageHandler';
import { getChatTemplate } from './templates/chatTemplate';
import * as path from 'path';

export class ChatViewProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'devAiChatView';
    private _view?: vscode.WebviewView;
    private groqService: GroqService;
    private messageHandler?: MessageHandler;

    constructor(
        private readonly _extensionUri: vscode.Uri,
    ) {
        this.groqService = GroqService.getInstance();
    }

    public async resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken,
    ) {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [
                vscode.Uri.joinPath(this._extensionUri, 'src', 'templates'),
                this._extensionUri
            ]
        };

        this.messageHandler = new MessageHandler(webviewView.webview, this.groqService);

        webviewView.webview.html = await getChatTemplate(webviewView.webview, this._extensionUri);

        // Handle messages from the webview
        webviewView.webview.onDidReceiveMessage(async data => {
            switch (data.type) {
                case 'sendMessage':
                    await this.messageHandler?.handleMessage(data.value, data.attachment);
                    break;
                case 'updateConfig':
                    this.messageHandler?.handleConfigUpdate(data.value);
                    break;
                case 'attachment':
                    const selection = await vscode.window.showQuickPick(['Search Workspace Files', 'Select External File'], {
                        placeHolder: 'Choose file selection method'
                    });

                    if (selection === 'Search Workspace Files') {
                        // Get all files in workspace
                        const files = await vscode.workspace.findFiles('**/*');
                        const fileItems = files.map(file => ({
                            label: path.basename(file.fsPath),
                            description: vscode.workspace.asRelativePath(file.fsPath),
                            fsPath: file.fsPath
                        }));

                        const selectedFile = await vscode.window.showQuickPick(fileItems, {
                            placeHolder: 'Select a file from workspace'
                        });

                        if (selectedFile) {
                            webviewView.webview.postMessage({
                                type: 'fileAttached',
                                fileName: selectedFile.label,
                                filePath: selectedFile.fsPath
                            });
                        }
                    } else if (selection === 'Select External File') {
                        const fileUri = await vscode.window.showOpenDialog({
                            canSelectFiles: true,
                            canSelectFolders: false,
                            canSelectMany: false,
                            title: 'Select File to Attach'
                        });
                        
                        if (fileUri && fileUri[0]) {
                            const fileName = path.basename(fileUri[0].fsPath);
                            webviewView.webview.postMessage({
                                type: 'fileAttached',
                                fileName: fileName,
                                filePath: fileUri[0].fsPath
                            });
                        }
                    }
                    break;
                case 'cancelAttachment':
                    // Handle attachment cancellation if needed
                    break;
                case 'newChat':
                    this.messageHandler?.clearMessages();
                    break;
            }
        });
    }
} 