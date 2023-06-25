import { Component } from '@angular/core';
import {Router} from '@angular/router';

@Component({
  selector: 'app-baised',
  templateUrl: './baised.component.html',
  styleUrls: ['./baised.component.css']
})
export class BaisedComponent {

    url= 'Please Enter URL';
    urlName='';
    name='';
    selectedElement='';

    handleClear(){
    this.name='';
    this.selectedElement= '';
    }

    types:any[]=[
      {id:0, Name:'Select any value'},
      {id:1, Name:'Image'},
      {id:2, Name:'Text'}
    ];
}

