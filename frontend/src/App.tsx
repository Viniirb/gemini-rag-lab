import type { Component } from 'solid-js';
import { ChatWidget } from './features/chat/ChatWidget';

const App: Component = () => {
  return (
    <div class="bg-black min-h-screen text-white">
      <ChatWidget />
    </div>
  );
};

export default App;