import { Component, OnInit, Injectable } from '@angular/core';
import { Router, ActivatedRoute, NavigationStart, NavigationEnd } from '@angular/router';
import { HttpClient, HttpParams, HttpHeaders } from "@angular/common/http";
import { throwError } from "rxjs";
import { NgxSpinnerService } from 'ngx-spinner';
import { Location, PopStateEvent } from "@angular/common";
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
    showForm:boolean = false;
    sectionScroll: any = '';
    lastPoppedUrl: any;
    constructor(private router: Router, private http: HttpClient, private spinnerService: NgxSpinnerService, private location: Location) {
              this.name='';
             this.checkBoxText='';
             this.checkBoxImage='';

    }

    ngOnInit() {
      this.location.subscribe((ev:PopStateEvent) => {
            this.lastPoppedUrl = ev.url;
        });
      this.router.events.subscribe((evt:any) => {
         // if (evt instanceof NavigationStart) {
                    if(evt.url == '/home#subContent')
                    {
                        this.sectionScroll = 'subContent';
                        this.doScroll();
                        this.sectionScroll= null;
                    }
          //  }
        /* if (!(evt instanceof NavigationEnd)) {
          return;
        } */

      });
    }

    doScroll() {

      if (!this.sectionScroll) {
        return;
      }
      try {
        var elements = document.getElementById(this.sectionScroll);
            if(elements != null)
            elements.scrollIntoView();
      }
      finally{
        this.sectionScroll = null;
      }
    }

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
              self.router.navigate(['biased/textresult'],
              {state: { biased_txt_results: Page['txt_results'], biased_alt_results: Page['alt_results'],
              biased_img_results: Page['txt_img_results'], total_biased_text: Page['total_biased_text'],
              total_biased_alt_text: Page['total_biased_alt_text'],
              total_biased_img_results: Page['total_biased_img_results'],
              text_results_Gender_Count: Page['text_results_Gender_Count'],
              alt_text_results_Gender_Count: Page['alt_text_results_Gender_Count'],
              img_text_results_Gender_Count: Page['img_text_results_Gender_Count'],
              overall_gender_count: Page['overall_gender_count'],
              textmodel_counts: Page['textmodel_counts'],
              total_Ethnicity_Count: Page['total_Ethnicity_Count'],
              total_GeoLocation_Count: Page['total_GeoLocation_Count'],
              text_results_Ethnicity_Count: Page['text_results_Ethnicity_Count'],
              alt_text_results_Ethnicity_Count: Page['alt_text_results_Ethnicity_Count'],
              img_text_results_Ethnicity_Count: Page['img_text_results_Ethnicity_Count'],
              text_results_GeoLocation_Count : Page['text_results_GeoLocation_Count'],
              alt_text_results_GeoLocation_Count: Page['alt_text_results_GeoLocation_Count'],
              img_text_results_GeoLocation_Count: Page['img_text_results_GeoLocation_Count'],
              total_Ethnicity_text: Page['total_Ethnicity_text'],
              total_Ethnicity_alt_text: Page['total_Ethnicity_alt_text'],
              total_Ethnicity_img_text: Page['total_Ethnicity_img_text'],
              total_GeoLocation_text: Page['total_GeoLocation_text'],
              total_GeoLocation_alt_text: Page['total_GeoLocation_alt_text'],
              total_GeoLocation_img_text: Page['total_GeoLocation_img_text']
              }});
              //window.location.assign('/output');
            }
            else if (Page['file'] == 'Image') {
              //alert(Page['image_results_tr']);
              self.router.navigate(['biased/imageresult'], {state: {image_biased_results: Page['image_results'],
              image_results_Count: Page['image_results_Count'],
              image_results_Gender_Count: Page['image_results_Gender_Count'],
              image_results_Confidence_Count: Page['image_results_Confidence_Count'],
              image_results_Skin_Color_Count: Page['image_results_Skin_Color_Count'],
              image_results_Race_Count: Page['image_results_Race_Count']}});
              //window.location.assign('/imageOp');
            }
            else {
              self.router.navigate(['biased/parallelexec'],
              {state: { biased_txt_results: Page['txt_results'], biased_alt_results: Page['alt_results'],
              biased_img_results: Page['txt_img_results'], total_biased_text: Page['total_biased_text'],
              total_biased_alt_text: Page['total_biased_alt_text'],
              total_biased_img_results: Page['total_biased_img_results'],
              text_results_Gender_Count: Page['text_results_Gender_Count'],
              alt_text_results_Gender_Count: Page['alt_text_results_Gender_Count'],
              img_text_results_Gender_Count: Page['img_text_results_Gender_Count'],
              overall_gender_count: Page['overall_gender_count'],
              textmodel_counts: Page['textmodel_counts'],
              total_Ethnicity_Count: Page['total_Ethnicity_Count'],
              total_GeoLocation_Count: Page['total_GeoLocation_Count'],
              text_results_Ethnicity_Count: Page['text_results_Ethnicity_Count'],
              alt_text_results_Ethnicity_Count: Page['alt_text_results_Ethnicity_Count'],
              img_text_results_Ethnicity_Count: Page['img_text_results_Ethnicity_Count'],
              text_results_GeoLocation_Count : Page['text_results_GeoLocation_Count'],
              alt_text_results_GeoLocation_Count: Page['alt_text_results_GeoLocation_Count'],
              img_text_results_GeoLocation_Count: Page['img_text_results_GeoLocation_Count'],
              total_Ethnicity_text: Page['total_Ethnicity_text'],
              total_Ethnicity_alt_text: Page['total_Ethnicity_alt_text'],
              total_Ethnicity_img_text: Page['total_Ethnicity_img_text'],
              total_GeoLocation_text: Page['total_GeoLocation_text'],
              total_GeoLocation_alt_text: Page['total_GeoLocation_alt_text'],
              total_GeoLocation_img_text: Page['total_GeoLocation_img_text'],
              image_biased_results: Page['image_results'],
              image_results_Count: Page['image_results_Count'],
              image_results_Gender_Count: Page['image_results_Gender_Count'],
              image_results_Confidence_Count: Page['image_results_Confidence_Count'],
              image_results_Skin_Color_Count: Page['image_results_Skin_Color_Count'],
              image_results_Race_Count: Page['image_results_Race_Count']
              }});
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

    getStartedWithForm(){
      this.showForm = true;
      }

    startVideo(){
      this.showForm =false}

  navigateTo(route: string) {
    this.router.navigate([route]);

  }
}

