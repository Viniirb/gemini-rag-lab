import type { ChatResponse } from "../models/chat";

export const chatService = {
  async sendMessage(pergunta: string): Promise<ChatResponse> {
    try {
      const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pergunta })
      });

      if (!response.ok) throw new Error('Erro na API');
      return await response.json();
    } catch (error) {
      console.error(error);
      throw error;
    }
  }
};