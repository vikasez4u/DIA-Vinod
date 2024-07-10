import { Component, OnInit, Injectable } from '@angular/core';
import { MenuItem, MessageService } from 'primeng/api';
import { Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { GenderComponent } from './gender/gender.component';
import { BaisedwordsComponent } from './baisedwords/baisedwords.component';
import { FileComponent } from '../fileupload/file/file.component';
import {  HttpClient, HttpParams, HttpHeaders } from "@angular/common/http";

@Component({
  selector: 'app-configuration',
  templateUrl: './configuration.component.html',
  styleUrls: ['./configuration.component.css'],
    providers: [MessageService]
})

@Injectable({
  providedIn: 'root'
})

export class ConfigurationComponent implements OnInit{
selectedSection: string = 'gender';
constructor(private router: Router,private modalService: NgbModal,private http: HttpClient){}

gfg: MenuItem[] = [];
//gName : any[] = [];

  ngOnInit() {
    this.gfg = [
      {
        label: 'Configurations',
         icon: 'pi pi-desktop',
        items: [
          {
            label: 'Gender Configuration',
             icon: 'pi pi-server',
             id: 'genderconfigid'
          },
          {
            label: 'Default Biased Word Configuration',
            icon: 'pi pi-server',
            id: 'biasedwordconfigid'
          },
          {
            label: 'Upload File',
            icon: 'pi pi-server',
            id: 'uploadfileconfigid'
          }
        ]
      }
    ];

  }
activeMenu(event:any) {
//alert(event.target['id']);
if(event.target['id'] == 'genderconfigid')
  this.modalService.open(GenderComponent);
else if(event.target['id'] == 'biasedwordconfigid'){
  const modalRef = this.modalService.open(BaisedwordsComponent, {windowClass :"popup"});
 // alert("configdata:"+this.gName);
 // modalRef.componentInstance.GName = this.gName;
}else {
  this.modalService.open(FileComponent);
}
}
/*alert("Entered Active Menu");
alert("event::"+ event.label);
alert("event.target::"+event.route);
let node;
if (event.target.tagName === "A") {
  node = event.target;
} else {
  node = event.target.parentNode;
}
let menuitem = document.getElementsByClassName("ui-menuitem-link");
for (let i = 0; i < menuitem.length; i++) {
  menuitem[i].classList.remove("active");
}
node.classList.add("active")
}*/

selectSection(section: string) {
    this.selectedSection = section;
  }
}
