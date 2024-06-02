import { Component, OnInit, Input, ElementRef, ViewChild } from '@angular/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { HttpClient, HttpParams, HttpHeaders } from "@angular/common/http";
import { FormsModule } from "@angular/forms";

@Component({
  selector: 'app-baisedwords',
  templateUrl: './baisedwords.component.html',
  styleUrls: ['./baisedwords.component.css']
})
export class BaisedwordsComponent implements OnInit{

    bWordname= 'Enter Biased Word';
    biasedWord='';
    bword : any;
    GName: any;
    bWorddata: any;
    genName : any;
    editCache: { [key: string]: any } = {};

constructor(private modalService: NgbModal,private http: HttpClient){
}

ngOnInit() {
//alert("Data::"+ this.GName);
this.genderresults();
console.log(this.GName);
//console.debug(this.GName[0].stringify);
this.baisedwordresult();
//this.updateEditCache();
}

genderresults(){
  this.http.get('/genderresults', { responseType: 'json' })
            .subscribe((data: any) => {
              //alert(data['genderresults']);
              console.log(data);
              console.log(data['genderresults']);
              this.GName = data['genderresults'];
            });
}

baisedwordresult(){
this.http.get('/baisedwordresults', { responseType: 'json' })
          .subscribe((data: any) => {
           // alert(JSON.stringify(data));
            this.bWorddata = data['baisedword_results'];
            this.bWorddata.forEach((item:any) => {
                   this.editCache[item.id] = {
                    edit: false,
                    data: { ...item }
              };
            });
          });
}

baisedwordsave(name:any,genderId:any){
const data = new HttpParams()
          .set('biasedWord', name)
          .set('genderID', genderId);
  this.call(data,"/baisedwordsave", "POST");
}

baisedwordupdate(word:any,bId:any){
const data = new HttpParams()
          .set('id', bId)
          .set('word', word);
  this.call(data,"/baisedwordupdate", "POST");
}

baisedworddelete(id:any){
const data = new HttpParams()
          .set('id', id);
  this.call(data,"/baisedworddelete", "POST");
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
              this.baisedwordresult();
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
     const index = this.bWorddata.findIndex((item:any) => item.id === id);
    this.editCache[id] = {
      data: { ...this.bWorddata[index] },
      edit: false
    };
  }

  delete(id: string): void {
     const index = this.bWorddata.findIndex((item:any) => item.id === id);
    Object.assign(this.bWorddata[index], this.editCache[id].data);
    this.editCache[id].edit = false;
   // alert(this.editCache[id].data.BaisedWord);
   //alert(id);
    this.baisedworddelete(id);
  }

  saveEdit(id: string): void {
     const index = this.bWorddata.findIndex((item:any) => item.id === id);
    Object.assign(this.bWorddata[index], this.editCache[id].data);
    this.editCache[id].edit = false;
   // alert(this.editCache[id].data.BaisedWord);
   //alert(id);
    this.baisedwordupdate(this.editCache[id].data.BaisedWord,id);
  }

  updateEditCache(): void {
     this.bWorddata.toPromise().forEach((item:any) => {
      this.editCache[item.id] = {
        edit: false,
        data: { ...item }
      };
    });
  }

}

