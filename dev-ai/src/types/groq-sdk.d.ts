export type GroqModel = 
  // Production Models
  | "distil-whisper-large-v3-en"
  | "gemma2-9b-it"
  | "llama-3.3-70b-versatile"
  | "llama-3.1-8b-instant"
  | "llama-guard-3-8b"
  | "llama3-70b-8192"
  | "llama3-8b-8192"
  | "mixtral-8x7b-32768"
  | "whisper-large-v3"
  | "whisper-large-v3-turbo"
  // Preview Models
  | "deepseek-r1-distill-llama-70b"
  | "llama-3.3-70b-specdec"
  | "llama-3.2-1b-preview"
  | "llama-3.2-3b-preview"
  | "llama-3.2-11b-vision-preview"
  | "llama-3.2-90b-vision-preview";

export interface GroqConfig {
  model: GroqModel;
  temperature?: number;
  max_completion_tokens?: number;
  top_p?: number;
  stream?: boolean;
  stop?: string[] | null;
}

export interface GroqMessage {
  role: string;
  content: string;
}

export interface GroqRequestBody {
  messages: GroqMessage[];
  model: GroqModel;
  temperature?: number;
  max_completion_tokens?: number;
  top_p?: number;
  stream?: boolean;
  stop?: string[] | null;
} 