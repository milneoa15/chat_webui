import type {
  ChatRequest,
  ChatResponse,
  HealthResponse,
  ModelCard,
} from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Request failed");
  }

  return (await response.json()) as T;
}

export async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`);
  return handleResponse<HealthResponse>(response);
}

export async function fetchModels(): Promise<ModelCard[]> {
  const response = await fetch(`${API_BASE_URL}/mock/models`);
  return handleResponse<ModelCard[]>(response);
}

export async function createMockChat(payload: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/mock/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  return handleResponse<ChatResponse>(response);
}
