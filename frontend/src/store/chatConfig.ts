import { create } from "zustand";
import type { ChatConfig } from "../types/api";

interface ChatConfigState {
  config: ChatConfig;
  update: (partial: Partial<ChatConfig>) => void;
}

const defaultConfig: ChatConfig = {
  temperature: 0.7,
  top_p: 0.85,
  max_tokens: 256,
  presence_penalty: 0,
  frequency_penalty: 0,
};

export const useChatConfig = create<ChatConfigState>((set) => ({
  config: defaultConfig,
  update: (partial) =>
    set((state) => ({
      config: { ...state.config, ...partial },
    })),
}));
