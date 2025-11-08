export interface HealthResponse {
  status: string;
  version: string;
  timestamp: string;
}

export interface ModelCard {
  id: string;
  name: string;
  quantization: string;
  context_length: number;
  parameter_count: number;
  description: string;
}

export interface ChatConfig {
  temperature: number;
  top_p: number;
  max_tokens: number;
  presence_penalty: number;
  frequency_penalty: number;
}

export interface ChatRequest {
  model_id: string;
  prompt: string;
  system_prompt: string;
  config: ChatConfig;
}

export interface ChatChunk {
  token: string;
  index: number;
  is_final: boolean;
}

export interface ChatResponse {
  model_id: string;
  stream: ChatChunk[];
}
