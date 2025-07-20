import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NavigationChat } from './navigation-chat';

describe('NavigationChat', () => {
  let component: NavigationChat;
  let fixture: ComponentFixture<NavigationChat>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NavigationChat]
    })
    .compileComponents();

    fixture = TestBed.createComponent(NavigationChat);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
