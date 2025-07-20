import { Routes } from '@angular/router';
import { HomeComponent } from './pages/home/home';
import { NavigationChatComponent } from './pages/navigation-chat/navigation-chat';
import { LegalDocumentsComponent } from './pages/legal-documents/legal-documents';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'navigation-chat', component: NavigationChatComponent },
  { path: 'legal-documents', component: LegalDocumentsComponent }
];