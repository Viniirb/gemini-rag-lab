import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

interface Message {
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule], 
  template: `
    <div class="chat-container">
      <header>
        <h1>🤖 Gemini RAG - Hacking Docs</h1>
        <span class="status" [class.online]="backendOnline">
          {{ backendOnline ? 'Online' : 'Desconectado' }}
        </span>
      </header>

      <div class="messages-area">
        <div *ngFor="let msg of messages" [class]="'message ' + msg.sender">
          <div class="bubble">
            <p [innerHTML]="msg.text"></p>
            <span class="time">{{ msg.timestamp | date:'shortTime' }}</span>
          </div>
        </div>
        
        <div *ngIf="isLoading" class="message bot">
          <div class="bubble loading">Digitando...</div>
        </div>
      </div>

      <div class="input-area">
        <input [(ngModel)]="userQuestion" 
               (keyup.enter)="sendMessage()" 
               placeholder="Pergunte sobre o PDF..." 
               [disabled]="isLoading">
        <button (click)="sendMessage()" [disabled]="isLoading || !userQuestion.trim()">
          Enviar ➤
        </button>
      </div>
    </div>
  `,
  styles: [`
    .chat-container { max-width: 800px; margin: 0 auto; height: 95vh; display: flex; flex-direction: column; font-family: 'Segoe UI', sans-serif; background: #1e1e1e; color: #fff; }
    header { padding: 20px; background: #2d2d2d; border-bottom: 1px solid #444; display: flex; justify-content: space-between; align-items: center; }
    .status { font-size: 0.8rem; color: #ff5555; }
    .status.online { color: #55ff55; }
    .messages-area { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 15px; }
    .message { display: flex; }
    .message.user { justify-content: flex-end; }
    .message.bot { justify-content: flex-start; }
    .bubble { max-width: 70%; padding: 12px 16px; border-radius: 12px; font-size: 1rem; line-height: 1.4; white-space: pre-wrap; } /* pre-wrap ajuda na formatação */
    .user .bubble { background: #007bff; color: white; border-bottom-right-radius: 2px; }
    .bot .bubble { background: #333; color: #e0e0e0; border-bottom-left-radius: 2px; }
    .time { display: block; font-size: 0.7rem; margin-top: 5px; opacity: 0.7; text-align: right; }
    .loading { font-style: italic; color: #888; }
    .input-area { padding: 20px; background: #2d2d2d; display: flex; gap: 10px; }
    input { flex: 1; padding: 12px; border-radius: 25px; border: none; background: #444; color: white; outline: none; }
    button { padding: 10px 20px; border-radius: 25px; border: none; background: #007bff; color: white; cursor: pointer; font-weight: bold; }
    button:disabled { background: #555; cursor: not-allowed; }
  `]
})
export class AppComponent {
  userQuestion = '';
  messages: Message[] = [];
  isLoading = false;
  backendOnline = false;
  private apiUrl = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient, private cdr: ChangeDetectorRef) {
    this.checkHealth();
  }

  checkHealth() {
    this.http.get(this.apiUrl).subscribe({
      next: () => {
        this.backendOnline = true;
        console.log('✅ Backend Online!');
      },
      error: () => {
        this.backendOnline = false;
        console.error('❌ Backend Offline');
      }
    });
  }

  sendMessage() {
    if (!this.userQuestion.trim()) return;

    const question = this.userQuestion;
    
    this.messages.push({ text: question, sender: 'user', timestamp: new Date() });
    this.userQuestion = '';
    this.isLoading = true;

    console.log('Enviando pergunta:', question);

    this.http.post<any>(`${this.apiUrl}/chat`, { pergunta: question })
      .subscribe({
        next: (res) => {
          console.log('📩 Resposta recebida do Python:', res);
          
          this.messages.push({ 
            text: res.resposta,
            sender: 'bot', 
            timestamp: new Date() 
          });
          
          this.isLoading = false;
          this.cdr.detectChanges(); 
        },
        error: (err) => {
          console.error('❌ Erro na requisição:', err);
          this.messages.push({ text: "Erro ao conectar. Veja o console (F12).", sender: 'bot', timestamp: new Date() });
          this.isLoading = false;
          this.cdr.detectChanges();
        }
      });
  }
}