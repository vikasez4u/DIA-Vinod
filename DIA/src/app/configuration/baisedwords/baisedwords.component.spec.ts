import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BaisedwordsComponent } from './baisedwords.component';

describe('BaisedwordsComponent', () => {
  let component: BaisedwordsComponent;
  let fixture: ComponentFixture<BaisedwordsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BaisedwordsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(BaisedwordsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
