import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SampleResultComponent } from './sample-result.component';

describe('SampleResultComponent', () => {
  let component: SampleResultComponent;
  let fixture: ComponentFixture<SampleResultComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [SampleResultComponent]
    });
    fixture = TestBed.createComponent(SampleResultComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
