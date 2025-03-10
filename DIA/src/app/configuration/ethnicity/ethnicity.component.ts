import { Component, OnInit } from '@angular/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import {  HttpClient, HttpParams, HttpHeaders } from "@angular/common/http";

@Component({
  selector: 'app-ethnicity',
  templateUrl: './ethnicity.component.html',
  styleUrls: ['./ethnicity.component.css']
})
export class EthnicityComponent implements OnInit {
gename= 'Enter Ethnicity Name';
    ethnicityName='';
    name : any;
    gName: any[] = [];
    editCache: { [key: string]: any } = {};
constructor(private modalService: NgbModal,private http: HttpClient){

}

ngOnInit() {
this.ethnicityResults();
}

ethnicityResults(){
this.http.get('/ethnicityresults', { responseType: 'json' })
          .subscribe((data: any) => {
           // alert(JSON.stringify(data));
            this.gName = data['ethnicityresults'];
            this.gName.forEach((item:any) => {
                   this.editCache[item.id] = {
                    edit: false,
                    data: { ...item }
              };
            });
          });
}
ethnicitysave(name:any){
const data = new HttpParams()
          .set('ethnicityName', name);
  this.call(data,"/ethnicitysave", "POST");
}

ethnicityupdate(name:any,Id:any){
const data = new HttpParams()
          .set('id', Id)
          .set('name', name);
  this.call(data,"/ethnicityupdate", "POST");
}

ethnicitydelete(id:any){
const data = new HttpParams()
          .set('id', id);
  this.call(data,"/ethnicitydelete", "POST");
}

call(data:any,urlname:any, methodname:any){

  const fetchRes = fetch(urlname, {
            "method": methodname,
            "body": JSON.stringify(data),
            "headers": {
              "Content-Type": "application/json",
            },
        })

          fetchRes
            .then((res: Response) => res.json())
            .then((d: any) => {
              this.ethnicityResults();
              alert(d['result']);
            },
            err => {
              alert("error while getting initial data :::  " + err.message);
              console.log("error while getting initial data" + err.message);
            });
}

startEdit(id: string): void {
    this.editCache[id].edit = true;
  }

  cancelEdit(id: string): void {
     const index = this.gName.findIndex((item:any) => item.id === id);
    this.editCache[id] = {
      data: { ...this.gName[index] },
      edit: false
    };
  }

  delete(id: string): void {
     const index = this.gName.findIndex((item:any) => item.id === id);
    Object.assign(this.gName[index], this.editCache[id].data);
    this.editCache[id].edit = false;
   // alert(this.editCache[id].data.BaisedWord);
   //alert(id);
    this.ethnicitydelete(id);
  }

  saveEdit(id: string): void {
     const index = this.gName.findIndex((item:any) => item.id === id);
    Object.assign(this.gName[index], this.editCache[id].data);
    this.editCache[id].edit = false;
   // alert(this.editCache[id].data.BaisedWord);
   //alert(id);
    this.ethnicityupdate(this.editCache[id].data.EthnicityName,id);
  }

  updateEditCache(): void {
     this.gName.forEach((item:any) => {
      this.editCache[item.id] = {
        edit: false,
        data: { ...item }
      };
    });
  }
}

