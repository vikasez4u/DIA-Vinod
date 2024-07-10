import { Component } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent {
btnActive: string = 'one';
sectionScroll: string = '';

constructor(private router: Router) {
    }

ngOnInit() {}

activeBtn(btnActive: string) {
  this.btnActive = btnActive;
  if(this.btnActive =='three'){
    this.sectionScroll='subContent';
    this.router.navigate( ['home' ], {fragment: 'subContent'});
  }
}

}
