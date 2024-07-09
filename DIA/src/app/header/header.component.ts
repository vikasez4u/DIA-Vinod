import { Component } from '@angular/core';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent {
btnActive: string = 'one';

constructor() {}

ngOnInit() {}

activeBtn(btnActive: string) {
  this.btnActive = btnActive;
}

}
