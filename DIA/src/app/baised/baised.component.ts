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

    constructor(private router: Router, private http: HttpClient, private spinnerService: NgxSpinnerService) {
              this.name='';
             this.checkBoxText='';
             this.checkBoxImage='';
    }

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
    if(this.name != null && this.name.length >0 && ( this.checkBoxText != null || this.checkBoxImage!=null) &&
     ( this.checkBoxText !='undefined' || this.checkBoxImage !='undefined') &&
     ( this.checkBoxText !=' ' || this.checkBoxImage !=' ') &&
     ( this.checkBoxText !='' || this.checkBoxImage !='')){
         this.spinnerService.show();
          this.loader = true;
          const data = new HttpParams()
          .set('urlName', this.name)
          .set('Text', this.checkBoxText)
          .set('Image',this.checkBoxImage);

          let self = this;
          function loadTo(Page: any): void {
            if (Page['file'] == 'Text') {
              self.router.navigate(['biased/textresult'], {state: { biased_txt_results: Page['txt_results'], biased_alt_results: Page['alt_results'],
              biased_img_results: Page['txt_img_results'], total_biased_text: Page['total_biased_text'],
              total_biased_alt_text: Page['total_biased_alt_text'],
              total_biased_img_results: Page['total_biased_img_results'],
              text_results_tr_Gender_Count: Page['text_results_tr_Gender_Count'],
              alt_text_results_tr_Gender_Count: Page['alt_text_results_tr_Gender_Count'],
              img_text_results_tr_Gender_Count: Page['img_text_results_tr_Gender_Count']}});
              //window.location.assign('/output');
            }
            else if (Page['file'] == 'Image') {
              //alert(Page['image_results_tr']);
              self.router.navigate(['biased/imageresult'], {state: {image_biased_results: Page['image_results'], image_results_tr: Page['image_results_tr']}});
              //window.location.assign('/imageOp');
            }
            else {
              self.router.navigate(['biased/parallelexec'], {state: { biased_txt_results: Page['txt_results'], biased_alt_results: Page['alt_results'],
              biased_img_results: Page['txt_img_results'], total_biased_text: Page['total_biased_text'],
              total_biased_alt_text: Page['total_biased_alt_text'],
              total_biased_img_results: Page['total_biased_img_results'],
              text_results_tr_Gender_Count: Page['text_results_tr_Gender_Count'],
              alt_text_results_tr_Gender_Count: Page['alt_text_results_tr_Gender_Count'],
              img_text_results_tr_Gender_Count: Page['img_text_results_tr_Gender_Count'],
              image_biased_results: Page['image_results'], image_results_tr: Page['image_results_tr']}});
              //window.location.assign('/parallelexec');
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
              this.name='';
              this.checkBoxText='';
              this.checkBoxImage='';
              alert("error while getting initial data :::  " + err.message);
              console.log("error while getting initial data" + err.message);
            });
        }else{
            alert("Please Enter All mandatory fields");
             this.name='';
             this.checkBoxText='';
             this.checkBoxImage='';
        }
    }

    callCreateRequest(category: any){
        console.log('Vikash');
        this.router.navigate(['fileupload/file']);
      }

}

