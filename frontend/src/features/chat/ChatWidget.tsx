import { createSignal, For, Show, type Component } from 'solid-js';
import { Send, Bot, Database, Terminal } from 'lucide-solid';
import { chatService } from '../../core/services/chat.service';
import type { Message } from '../../core/models/chat';

export const ChatWidget: Component = () => {
  const [input, setInput] = createSignal('');
  const [messages, setMessages] = createSignal<Message[]>([]);
  const [loading, setLoading] = createSignal(false);
  
  let messagesContainer: HTMLDivElement | undefined;

  const scrollToBottom = () => {
    setTimeout(() => {
      messagesContainer?.scrollTo({ top: messagesContainer.scrollHeight, behavior: 'smooth' });
    }, 50);
  };

  const handleSend = async () => {
    if (!input().trim() || loading()) return;

    const userText = input();
    setInput('');
    
    setMessages(prev => [...prev, {
      id: Date.now().toString(),
      text: userText,
      sender: 'user',
      timestamp: new Date()
    }]);
    
    setLoading(true);
    scrollToBottom();

    try {
      const res = await chatService.sendMessage(userText);
      
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        text: res.resposta,
        sender: 'bot',
        timestamp: new Date()
      }]);
    } catch (err) {
      setMessages(prev => [...prev, {
        id: 'error',
        text: 'Erro: Verifique se o backend Python está rodando na porta 8000.',
        sender: 'bot',
        timestamp: new Date()
      }]);
    } finally {
      setLoading(false);
      scrollToBottom();
    }
  };

  return (
    <div class="flex flex-col h-screen max-w-4xl mx-auto border-x border-border shadow-2xl bg-black">
      <header class="p-4 border-b border-border bg-secondary/20 backdrop-blur flex items-center gap-3 sticky top-0 z-10">
        <div class="p-2 bg-primary/20 rounded-lg border border-primary/20">
          <Database class="text-primary w-5 h-5" />
        </div>
        <div>
          <h1 class="font-bold text-sm tracking-wide text-zinc-100">SQL RAG AGENT</h1>
          <div class="flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
            <p class="text-[10px] text-zinc-400 font-mono">GEMMA-3-27B ONLINE</p>
          </div>
        </div>
      </header>

      <div 
        ref={messagesContainer}
        class="flex-1 overflow-y-auto p-4 space-y-6 scroll-smooth"
      >
        <Show when={messages().length === 0}>
          <div class="h-full flex flex-col items-center justify-center text-zinc-600 gap-4 opacity-50">
            <Terminal size={48} />
            <p class="font-mono text-sm">Aguardando comando...</p>
          </div>
        </Show>

        <For each={messages()}>
          {(msg) => (
            <div class={`flex gap-3 animate-in fade-in slide-in-from-bottom-2 duration-300 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
              
              <Show when={msg.sender === 'bot'}>
                <div class="w-8 h-8 rounded-lg bg-zinc-800 border border-zinc-700 flex items-center justify-center shrink-0">
                  <Bot size={16} class="text-zinc-400" />
                </div>
              </Show>

              <div class={`max-w-[85%] p-3.5 rounded-2xl text-sm whitespace-pre-wrap leading-relaxed shadow-sm
                ${msg.sender === 'user' 
                  ? 'bg-primary text-white rounded-tr-none' 
                  : 'bg-secondary/50 text-zinc-200 border border-border rounded-tl-none font-mono text-xs'
                }`}>
                {msg.text}
              </div>

            </div>
          )}
        </For>
        
        <Show when={loading()}>
          <div class="flex gap-2 items-center text-zinc-500 text-xs font-mono p-4 animate-pulse">
            <div class="w-2 h-2 bg-primary rounded-full animate-bounce"></div>
            <div class="w-2 h-2 bg-primary rounded-full animate-bounce delay-75"></div>
            <div class="w-2 h-2 bg-primary rounded-full animate-bounce delay-150"></div>
            <span class="ml-2">PROCESSANDO TOKENS...</span>
          </div>
        </Show>
      </div>

      <div class="p-4 border-t border-border bg-background/95 backdrop-blur">
        <div class="relative flex items-center">
          <input
            type="text"
            value={input()}
            onInput={(e) => setInput(e.currentTarget.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ex: Qual a estrutura da tabela Z_LOG?"
            disabled={loading()}
            class="w-full bg-input border border-border text-zinc-200 rounded-xl pl-4 pr-12 py-3.5 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary/50 transition-all font-mono text-sm shadow-inner"
          />
          <button 
            onClick={handleSend}
            disabled={loading() || !input()}
            class="absolute right-2 p-2 bg-primary/90 hover:bg-primary text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all active:scale-95"
          >
            <Send size={16} />
          </button>
        </div>
        <p class="text-center text-[10px] text-zinc-600 mt-3 font-mono">
          O modelo pode alucinar. Verifique dados críticos.
        </p>
      </div>
    </div>
  );
};