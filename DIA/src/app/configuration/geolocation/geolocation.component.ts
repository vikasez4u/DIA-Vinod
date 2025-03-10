import { Component, OnInit } from '@angular/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import {  HttpClient, HttpParams, HttpHeaders } from "@angular/common/http";

@Component({
  selector: 'app-geolocation',
  templateUrl: './geolocation.component.html',
  styleUrls: ['./geolocation.component.css']
})
export class GeolocationComponent implements OnInit {
gename= 'Enter Geolocation Name';
    geolocationName='';
    name : any;
    gName: any[] = [];
    editCache: { [key: string]: any } = {};
constructor(private modalService: NgbModal,private http: HttpClient){

}

ngOnInit() {
this.geolocationResults();
}

geolocationResults(){
this.http.get('/geolocationresults', { responseType: 'json' })
          .subscribe((data: any) => {
           // alert(JSON.stringify(data));
            this.gName = data['geolocationresults'];
            this.gName.forEach((item:any) => {
                   this.editCache[item.id] = {
                    edit: false,
                    data: { ...item }
              };
            });
          });
}
geolocationsave(name:any){
const data = new HttpParams()
          .set('geolocationName', name);
  this.call(data,"/geolocationsave", "POST");
}

geolocationupdate(name:any,Id:any){
const data = new HttpParams()
          .set('id', Id)
          .set('name', name);
  this.call(data,"/geolocationupdate", "POST");
}

geolocationdelete(id:any){
const data = new HttpParams()
          .set('id', id);
  this.call(data,"/geolocationdelete", "POST");
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
              this.geolocationResults();
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
    this.geolocationdelete(id);
  }

  saveEdit(id: string): void {
     const index = this.gName.findIndex((item:any) => item.id === id);
    Object.assign(this.gName[index], this.editCache[id].data);
    this.editCache[id].edit = false;
   // alert(this.editCache[id].data.BaisedWord);
   //alert(id);
    this.geolocationupdate(this.editCache[id].data.GeolocationName,id);
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
