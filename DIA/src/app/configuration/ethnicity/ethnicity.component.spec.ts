import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EthnicityComponent } from './ethnicity.component';

describe('EthnicityComponent', () => {
  let component: EthnicityComponent;
  let fixture: ComponentFixture<EthnicityComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [EthnicityComponent]
    });
    fixture = TestBed.createComponent(EthnicityComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
