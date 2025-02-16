import * as vscode from 'vscode';
import { GroqConfig, GroqMessage, GroqModel, GroqRequestBody } from '../types/groq-sdk';

export class GroqService {
    private static instance: GroqService;
    private apiKey: string;
    private baseUrl = 'https://api.groq.com/openai/v1/chat/completions';
    private currentConfig: GroqConfig = {
        model: "mixtral-8x7b-32768",
        temperature: 1,
        max_completion_tokens: 1024,
        top_p: 1,
        stream: true,
        stop: null
    };

    private constructor() {
        this.apiKey = process.env.GROQ_API_KEY || "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";
    }

    public static getInstance(): GroqService {
        if (!GroqService.instance) {
            GroqService.instance = new GroqService();
        }
        return GroqService.instance;
    }

    public setConfig(config: Partial<GroqConfig>) {
        this.currentConfig = { ...this.currentConfig, ...config };
    }

    public getConfig(): GroqConfig {
        return { ...this.currentConfig };
    }

    public async generateResponse(messages: GroqMessage[]): Promise<string> {
        try {
            const response = await fetch(this.baseUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.apiKey}`
                },
                body: JSON.stringify({
                    model: this.currentConfig.model,
                    messages: messages,
                    temperature: this.currentConfig.temperature,
                    max_completion_tokens: this.currentConfig.max_completion_tokens,
                    stream: true
                })
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
            }

            const reader = response.body?.getReader();
            if (!reader) {
                throw new Error('Failed to get response reader');
            }

            const decoder = new TextDecoder();
            let result = '';
            let buffer = '';

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';

                for (const line of lines) {
                    if (line.trim() === '') continue;
                    if (line === 'data: [DONE]') continue;
                    if (!line.startsWith('data: ')) continue;

                    try {
                        const jsonStr = line.slice(5).trim();
                        if (!jsonStr) continue;
                        
                        const data = JSON.parse(jsonStr);
                        const content = data.choices?.[0]?.delta?.content;
                        if (content) {
                            result += content;
                        }
                    } catch (error: any) {
                        console.error('Error parsing JSON:', error.message);
                        console.error('Problematic line:', line);
                        continue;
                    }
                }
            }

            // Handle any remaining buffer
            if (buffer) {
                try {
                    if (buffer.startsWith('data: ') && buffer !== 'data: [DONE]') {
                        const jsonStr = buffer.slice(5).trim();
                        if (jsonStr) {
                            const data = JSON.parse(jsonStr);
                            const content = data.choices?.[0]?.delta?.content;
                            if (content) {
                                result += content;
                            }
                        }
                    }
                } catch (error: any) {
                    console.error('Error parsing remaining buffer:', error.message);
                }
            }

            return result;
        } catch (error: any) {
            console.error('Error in generateResponse:', error);
            throw new Error(`Failed to generate response: ${error.message}`);
        }
    }

    private extractJsonFromResponse(result: string): string {
        try {
            const startIdx = result.indexOf('{');
            const endIdx = result.lastIndexOf('}') + 1;
            if (startIdx >= 0 && endIdx > 0) {
                let jsonStr = result.slice(startIdx, endIdx)
                    .replace(/\\n/g, "")
                    .replace(/\\"/g, '"')
                    .replace(/\s+/g, " ")
                    .replace(/\\/g, "")
                    .replace(/"{/g, "{")
                    .replace(/}"/g, "}");
                return jsonStr;
            }
            return result;
        } catch (error) {
            console.error('Error extracting JSON:', error);
            return result;
        }
    }
} 