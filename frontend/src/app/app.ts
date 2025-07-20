import { Component } from '@angular/core';
import { bootstrapApplication } from '@angular/platform-browser';
import { provideRouter } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';
import { routes } from './app.routes';
import { RouterModule } from '@angular/router'; // ✅ add this!

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterModule], // ✅ fix here
  template: `<router-outlet></router-outlet>`
})
export class App {}

bootstrapApplication(App, {
  providers: [provideRouter(routes), provideHttpClient()]
});