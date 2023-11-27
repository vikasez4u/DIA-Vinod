import { Component, OnInit, Injectable } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { HttpClient, HttpParams } from "@angular/common/http";
import { throwError } from "rxjs";
const uploadURL = "http://localhost:5000/static/";

@Component({
  selector: 'app-baised',
  templateUrl: './baised.component.html',
  styleUrls: ['./baised.component.css']
})

@Injectable({
  providedIn: 'root'
})
export class BaisedComponent implements OnInit {

    url= 'Please Enter URL';
    urlName='';
    name : any;
   // selectedElement='';
    //Text='';
    checkBoxText: any;
    checkBoxImage: any;
    category: any;

    constructor(private router: Router, private http: HttpClient) {}

    ngOnInit(): void {}

    handleClear(){
    this.name='';
   // this.selectedElement= '';
   this.checkBoxText='';
    this.checkBoxImage='';
    }

   /*  types:any[]=[
      {id:-1, Name:'Select any value'},
      {id:1, Name:'Image'},
      {id:2, Name:'Text'}
    ]; */

    onsubmit(){
     // alert(this.name);
     // alert(this.checkBoxText);
     // alert(this.checkBoxImage);

      if (this.name) {
          alert('calling service');
          const headers = { 'content-type': 'application/html'};
          const params = new HttpParams()
          .set('urlName', this.name)
          .set('Text', this.checkBoxText)
          .set('Image',this.checkBoxImage);

          this.http.post(uploadURL,{},{'headers': headers,
    params: params})
      .subscribe(data => {
              alert(data);
                console.log(data);
                let resp = JSON.parse(JSON.stringify(data));
                 alert(resp);
      },
        err => {
          console.log("error while getting initial data" + err.message);
        }
      );
      }
    }


    callCreateRequest(category: any){
        console.log('Vikash');
        this.router.navigate(['fileupload/file']);
      }

}

