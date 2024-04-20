import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TextresultComponent } from './textresult.component';

describe('TextresultComponent', () => {
  let component: TextresultComponent;
  let fixture: ComponentFixture<TextresultComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [TextresultComponent]
    });
    fixture = TestBed.createComponent(TextresultComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
