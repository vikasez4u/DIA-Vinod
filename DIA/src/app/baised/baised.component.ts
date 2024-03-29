import { Component, OnInit, Injectable } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { HttpClient, HttpParams, HttpHeaders } from "@angular/common/http";
import { throwError } from "rxjs";
import { NgxSpinnerService } from 'ngx-spinner';
const uploadURL = "http://localhost:5000/output/";

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
    loader = false;
   // selectedElement='';
    //Text='';
    checkBoxText: any;
    checkBoxImage: any;
    category: any;

    constructor(private router: Router, private http: HttpClient, private spinnerService: NgxSpinnerService) {}

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

    onSubmit(){
    if(this.name != null && ( this.checkBoxText != null || this.checkBoxImage!=null)){
         this.spinnerService.show();
          this.loader = true;
          const data = new HttpParams()
          .set('urlName', this.name)
          .set('Text', this.checkBoxText)
          .set('Image',this.checkBoxImage);

          function loadTo(Page: any): void {
            if (Page['file'] == 'output.html') {
              window.location.assign('/output');
            }
            else if (Page['file'] == 'imageOp.html') {
              window.location.assign('/imageOp');
            }
            else {
              window.location.assign('/parallelexec');
            }
          }

           const fetchRes = fetch('/result', {
            "method": "POST",
            "body": JSON.stringify(data),
            "headers": {
              "Content-Type": "application/json",
            },
        })

          fetchRes
            .then((res: Response) => res.json())
            .then((d: any) => {
              loadTo(d);
              this.spinnerService.hide();
              this.loader = false;
            },
            err => {
              this.spinnerService.hide();
              this.loader = false;
              alert("error while getting initial data :::  " + err.message);
              console.log("error while getting initial data" + err.message);
            });
        }else{
            alert("Please Enter All mandatory fields");
        }
    }

    callCreateRequest(category: any){
        console.log('Vikash');
        this.router.navigate(['fileupload/file']);
      }

}

