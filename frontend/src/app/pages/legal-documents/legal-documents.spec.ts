import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LegalDocuments } from './legal-documents';

describe('LegalDocuments', () => {
  let component: LegalDocuments;
  let fixture: ComponentFixture<LegalDocuments>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LegalDocuments]
    })
    .compileComponents();

    fixture = TestBed.createComponent(LegalDocuments);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
