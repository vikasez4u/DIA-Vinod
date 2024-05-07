import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ParallelexecComponent } from './parallelexec.component';

describe('ParallelexecComponent', () => {
  let component: ParallelexecComponent;
  let fixture: ComponentFixture<ParallelexecComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [ParallelexecComponent]
    });
    fixture = TestBed.createComponent(ParallelexecComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
