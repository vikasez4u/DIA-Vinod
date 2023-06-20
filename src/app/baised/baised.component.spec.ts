import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BaisedComponent } from './baised.component';

describe('BaisedComponent', () => {
  let component: BaisedComponent;
  let fixture: ComponentFixture<BaisedComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [BaisedComponent]
    });
    fixture = TestBed.createComponent(BaisedComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
