import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ImageresultComponent } from './imageresult.component';

describe('ImageresultComponent', () => {
  let component: ImageresultComponent;
  let fixture: ComponentFixture<ImageresultComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [ImageresultComponent]
    });
    fixture = TestBed.createComponent(ImageresultComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
