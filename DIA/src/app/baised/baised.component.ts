import { Component } from '@angular/core';
import {Router} from '@angular/router';

@Component({
  selector: 'app-baised',
  templateUrl: './baised.component.html',
  styleUrls: ['./baised.component.css']
})
export class BaisedComponent {
     url= 'Please Enter URL';

     name='';
     selectedElement={id:-1, Name:''};

     handleClear(){
      this.name='';
      this.selectedElement= {id:-1, Name:'Select...'};
     }

    types:any[]=[
      {id:-1, Name:'Select...'},
      {id:1, Name:'Image'},
      {id:2, Name:'Text'}
    ];

}

