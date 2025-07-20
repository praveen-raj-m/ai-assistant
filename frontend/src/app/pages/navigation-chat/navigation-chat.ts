import { Component, AfterViewInit } from '@angular/core';
import Split from 'split.js';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-navigation-chat',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './navigation-chat.html',
  styleUrls: ['./navigation-chat.css'],
})
export class NavigationChatComponent implements AfterViewInit {
  selectedFile: File | null = null;
  chunkPreview: any = {};
  generatedPrompt: string = '';
  userQuery: string = '';
  chatHistory: { user: string; ai: string }[] = [];
  isUploading = false;
  uploadSteps: string[] = [];

  constructor(private http: HttpClient) {}
  ngAfterViewInit(): void {
    // Upload + Preview
    Split(['#top-split > .upload', '#top-split > .preview'], {
      sizes: [50, 50],
      minSize: 150,
      gutterSize: 8,
      direction: 'horizontal',
      gutter: () => {
        const g = document.createElement('div');
        g.className = 'gutter gutter-horizontal';
        return g;
      },
    });

    // Prompt + Chat
    Split(['#bottom-split > .prompt', '#bottom-split > .chat'], {
      sizes: [50, 50],
      minSize: 150,
      gutterSize: 8,
      direction: 'horizontal',
      gutter: () => {
        const g = document.createElement('div');
        g.className = 'gutter gutter-horizontal';
        return g;
      },
    });

    // Top half + Bottom half
    Split(['#top-split', '#bottom-split'], {
      sizes: [50, 50],
      minSize: 150,
      gutterSize: 8,
      direction: 'vertical',
      gutter: () => {
        const g = document.createElement('div');
        g.className = 'gutter gutter-vertical';
        return g;
      },
    });
  }

  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
  }

//   uploadFile() {
//     if (!this.selectedFile) return;

//     this.isUploading = true;
//     const formData = new FormData();
//     formData.append('file', this.selectedFile);

//     this.http.post<any>('http://127.0.0.1:5000/upload', formData).subscribe({
//   next: (res) => {
//     this.isUploading = false;
//     alert(res.message || '✅ Upload and embedding successful!');

//     // Show only last 5 chunks, remove the 'vector' field
//     this.chunkPreview = res.chunks.slice(-5).map((chunk: any) => {
//       const { vector, ...cleanedChunk } = chunk;
//       return cleanedChunk;
//     });
//   },
//   error: (err) => {
//     this.isUploading = false;
//     console.error(err);
//     alert('❌ Upload failed. See console for details.');
//   }
// });

//   }

clearChat() {
  this.chatHistory = [];
}


uploadFile() {
  if (!this.selectedFile) return;

  this.isUploading = true;
  this.uploadSteps = [];
  const formData = new FormData();
  formData.append('file', this.selectedFile);

  // STEP 1 — Upload
  this.http.post<any>('http://127.0.0.1:5000/upload', formData).subscribe({
    next: (res1) => {
      this.uploadSteps.push(res1.message);

      // STEP 2 — Chunk
      this.http.post<any>('http://127.0.0.1:5000/chunk', {
        file_path: res1.file_path,
        filename: res1.filename
      }).subscribe({
        next: (res2) => {
          this.uploadSteps.push(res2.message);

          // STEP 3 — Embed
          this.http.post<any>('http://127.0.0.1:5000/embed', {
            chunks: res2.chunks
          }).subscribe({
            next: (res3) => {
              this.uploadSteps.push(res3.message);

              // STEP 4 — Upsert
              this.http.post<any>('http://127.0.0.1:5000/upsert', {
                chunks: res3.chunks
              }).subscribe({
                next: (res4) => {
                  this.uploadSteps.push(res4.message);
                  this.chunkPreview = res3.chunks.slice(-5);
                  this.isUploading = false;
                },
                error: () => this.uploadSteps.push('❌ Upsert failed')
              });
            },
            error: () => this.uploadSteps.push('❌ Embedding failed')
          });
        },
        error: () => this.uploadSteps.push('❌ Chunking failed')
      });
    },
    error: () => {
      this.uploadSteps.push('❌ Upload failed');
      this.isUploading = false;
    }
  });
}

  

  sendQuery() {
  if (!this.userQuery.trim()) return;

  const userMsg = this.userQuery;
  this.chatHistory.push({ user: userMsg, ai: 'Generating Answer' });
  this.userQuery = '';
  this.generatedPrompt = 'Generating prompt...';

  // Step 1: Fetch prompt only
  this.http.post<any>('http://127.0.0.1:5000/chat', { query: userMsg, send: false }).subscribe({
    next: (res) => {
      this.generatedPrompt = res.prompt;

      // Step 2: Send prompt to LLM after showing it
      this.http.post<any>('http://127.0.0.1:5000/chat', { query: userMsg, send: true }).subscribe({
        next: (res2) => {
          const i = this.chatHistory.length - 1;
          this.chatHistory[i].ai = res2.response || 'No answer.';
        },
        error: () => {
          const i = this.chatHistory.length - 1;
          this.chatHistory[i].ai = 'Error from LLM.';
        }
      });
    },
    error: () => {
      this.generatedPrompt = 'Failed to build prompt.';
    }
  });
}
}
