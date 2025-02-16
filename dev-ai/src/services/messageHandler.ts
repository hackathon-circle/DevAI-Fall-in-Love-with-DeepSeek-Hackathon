import * as vscode from 'vscode';
import { GroqService } from './groqService';
import * as fs from 'fs';
import * as path from 'path';
import * as marked from 'marked';

export class MessageHandler {
    constructor(
        private readonly webview: vscode.Webview,
        private readonly groqService: GroqService
    ) {
        // Set up message handling for the webview
        this.webview.onDidReceiveMessage(
            async (message) => {
                switch (message.type) {
                    case 'sendMessage':
                        await this.handleMessage(message.value, message.attachment);
                        break;
                    case 'updateConfig':
                        this.handleConfigUpdate(message.value);
                        break;
                    case 'applyCode':
                        await this.handleApplyCode(message.code, message.filename);
                        break;
                    case 'checkFileExists':
                        await this.checkFileExists(message.filename);
                        break;
                }
            },
            undefined
        );
    }

    private async checkFileExists(filename: string) {
        try {
            if (!filename) return;

            let exists = false;
            if (vscode.workspace.workspaceFolders) {
                const workspaceRoot = vscode.workspace.workspaceFolders[0].uri;
                const targetFile = vscode.Uri.joinPath(workspaceRoot, filename);
                
                try {
                    // Use fs.stat for faster check instead of workspace.findFiles
                    await vscode.workspace.fs.stat(targetFile);
                    exists = true;
                } catch {
                    exists = false;
                }
            }

            // Send the result back immediately
            this.webview.postMessage({
                type: 'fileExistsResult',
                filename: filename,
                exists: exists
            });
        } catch (error) {
            console.error('Error checking file existence:', error);
            // Send a result even if there's an error
            this.webview.postMessage({
                type: 'fileExistsResult',
                filename: filename,
                exists: false
            });
        }
    }

    private async handleApplyCode(code: string, suggestedFilename?: string) {
        try {
            console.log('1. Starting handleApplyCode', { code, suggestedFilename });
            
            // Check workspace
            if (!vscode.workspace.workspaceFolders || vscode.workspace.workspaceFolders.length === 0) {
                throw new Error('Please open a folder first (File -> Open Folder)');
            }

            // Get workspace path
            const workspaceFolder = vscode.workspace.workspaceFolders[0];
            const workspacePath = workspaceFolder.uri.fsPath;
            console.log('2. Using workspace path:', workspacePath);

            // Validate filename
            if (!suggestedFilename) {
                throw new Error('No filename provided');
            }

            // Create full file path
            const filePath = path.join(workspacePath, suggestedFilename);
            console.log('3. Will create file at:', filePath);

            // Check if directory exists
            const directory = path.dirname(filePath);
            if (!fs.existsSync(directory)) {
                console.log('4. Creating directory:', directory);
                fs.mkdirSync(directory, { recursive: true });
            }

            // Check if file already exists
            const fileExists = fs.existsSync(filePath);
            console.log('5. File exists check:', fileExists);

            if (fileExists) {
                const answer = await vscode.window.showWarningMessage(
                    `File ${suggestedFilename} already exists. Do you want to overwrite it?`,
                    'Yes', 'No'
                );
                if (answer !== 'Yes') {
                    console.log('6. User cancelled overwrite');
                    this.webview.postMessage({
                        type: 'addMessage',
                        message: '❌ File creation cancelled by user',
                        sender: 'assistant'
                    });
                    return;
                }
            }

            try {
                // Write the file
                console.log('7. Writing file content...');
                await vscode.workspace.fs.writeFile(
                    vscode.Uri.file(filePath),
                    Buffer.from(code, 'utf8')
                );
                console.log('8. File written successfully');

                // Try to open the file
                console.log('9. Opening file in editor...');
                const document = await vscode.workspace.openTextDocument(filePath);
                await vscode.window.showTextDocument(document);
                console.log('10. File opened in editor');

                // Show success messages
                const successMessage = `✅ File created successfully:\n\`${filePath}\``;
                this.webview.postMessage({
                    type: 'addMessage',
                    message: successMessage,
                    sender: 'assistant'
                });
                vscode.window.showInformationMessage('File created: ' + suggestedFilename);

            } catch (writeError: any) {
                console.error('Error during file operations:', writeError);
                throw new Error(`Failed to write/open file: ${writeError.message}`);
            }

        } catch (error: any) {
            // Log and show error
            console.error('Error in handleApplyCode:', error);
            const errorMessage = `❌ Error: ${error.message}\nWorkspace: ${vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || 'none'}`;
            this.webview.postMessage({
                type: 'addMessage',
                message: errorMessage,
                sender: 'assistant'
            });
            vscode.window.showErrorMessage(errorMessage);
        }
    }

    async handleMessage(message: string, attachment?: string) {
        try {
            let fullMessage = message;
            
            if (attachment) {
                try {
                    // Read and format the attachment content
                    const fileContent = fs.readFileSync(attachment, 'utf8');
                    fullMessage = `${message}\n\nAttached Content:\n\`\`\`\n${fileContent}\n\`\`\``;
                } catch (error: any) {
                    console.error('Error reading attachment:', error);
                    throw new Error(`Failed to read attachment: ${error.message}`);
                }
            }

            // Add user message to the chat with markdown formatting
            this.webview.postMessage({
                type: 'addMessage',
                message: marked.parse(fullMessage),
                rawMessage: fullMessage,
                sender: 'user'
            });

            // Read role.txt
            const roleText = fs.readFileSync('src/services/role.txt', 'utf8');

            // Generate response using Groq
            const response = await this.groqService.generateResponse([
                {
                    role: "system",
                    content: roleText
                },
                {
                    role: "user",
                    content: fullMessage
                }
            ]);

            // Add assistant response to the chat with markdown formatting
            this.webview.postMessage({
                type: 'addMessage',
                message: marked.parse(response),
                rawMessage: response,
                sender: 'assistant'
            });
        } catch (error: any) {
            console.error('Error in handleMessage:', error);
            this.webview.postMessage({
                type: 'addMessage',
                message: `Error: ${error.message}`,
                sender: 'assistant'
            });
        }
    }

    handleConfigUpdate(config: any) {
        this.groqService.setConfig(config);
    }

    clearMessages() {
        this.webview.postMessage({
            type: 'clearMessages'
        });
    }
} 