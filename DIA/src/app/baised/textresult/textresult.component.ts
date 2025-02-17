import { Component, OnInit, Injectable  } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { HttpClient } from "@angular/common/http";
import {NgbModal, ModalDismissReasons}  from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'app-textresult',
  templateUrl: './textresult.component.html',
  styleUrls: ['./textresult.component.css']
})

@Injectable({
  providedIn: 'root'
})

export class TextresultComponent implements OnInit {
// This variable will hold the currently selected radio button value
selectedTextOption: string = 'textContent';  // Default is "Text Content"
selectedAltOption: string = 'textContent';
selectedImgTxtOption: string = 'textContent';

modelType: any;
biased_txt_results: any;
biased_alt_results: any;
biased_img_results: any
total_biased_text: any;
total_biased_alt_text: any;
total_biased_img_results: any;
text_results_tr_Gender_Count: any;
alt_text_results_tr_Gender_Count: any;
img_text_results_tr_Gender_Count: any;
overall_gender_count: any;
textmodel_counts: any;
total_Ethnicity_Count: any;
total_GeoLocation_Count: any;
text_results_Ethnicity_Count: any;
alt_text_results_Ethnicity_Count: any;
img_text_results_Ethnicity_Count: any;
text_results_GeoLocation_Count : any;
alt_text_results_GeoLocation_Count: any;
img_text_results_GeoLocation_Count: any;
total_Ethnicity_text: any;
total_Ethnicity_alt_text: any;
total_Ethnicity_img_text: any;
total_GeoLocation_text: any;
total_GeoLocation_alt_text: any;
total_GeoLocation_img_text: any;


maxTextValue: number = 0;
maxAltValue: number = 0;
maxImgTxtValue: number = 0;
maxGenderCount: number = 0;  // For maximum biased gender count
maxGender: string = '';  // For the gender associated with the maximum count
maxGenderPercentage: number = 0;  // For the percentage of the maximum biased count

maxTextEthValue: number = 0;
maxAltEthValue: number = 0;
maxImgTxtEthValue: number = 0;
maxEthnicityCount: number = 0;  // For maximum biased ethnicity count
maxEthnicity: string = '';  // For the city associated with the maximum count
maxEthnicityPercentage: number = 0;  // For the percentage of the maximum biased count

maxTextGeoValue: number = 0;
maxAltGeoValue: number = 0;
maxImgTxtGeoValue: number = 0;
maxGeoCount: number = 0;  // For maximum biased geo location count
maxGeo: string = '';  // For the country associated with the maximum count
maxGeoPercentage: number = 0;  // For the percentage of the maximum biased count

totalModelCount: number = 0;

selectedAnalysis: string = 'textContent';
analysisTitle : string = 'Overall Gender Analysis'

users: any[] = [];
defaultWords: any[] = [];
closeResult = '';

resultSection: string = '';

constructor(private router: Router, private activatedRoute: ActivatedRoute, private http: HttpClient, private modalService: NgbModal){
  let state = this.router.getCurrentNavigation()?.extras.state;

  if (state) {
    this.modelType = "Text";
    this.biased_txt_results = state['biased_txt_results'];
    this.biased_alt_results = state['biased_alt_results'];
    this.biased_img_results = state['biased_img_results'];
    this.total_biased_text = state['total_biased_text'];
    this.total_biased_alt_text = state['total_biased_alt_text'];
    this.total_biased_img_results = state['total_biased_img_results'];
    this.text_results_tr_Gender_Count = state['text_results_Gender_Count'];
    this.alt_text_results_tr_Gender_Count = state['alt_text_results_Gender_Count'];
    this.img_text_results_tr_Gender_Count = state['img_text_results_Gender_Count'];
    this.overall_gender_count = state['overall_gender_count'];
    this.textmodel_counts = state['textmodel_counts'];
    this.total_Ethnicity_Count = state['total_Ethnicity_Count'];
    this.total_GeoLocation_Count = state['total_GeoLocation_Count'];
    this.text_results_Ethnicity_Count = state['text_results_Ethnicity_Count'];
    this.alt_text_results_Ethnicity_Count = state['alt_text_results_Ethnicity_Count'];
    this.img_text_results_Ethnicity_Count = state['img_text_results_Ethnicity_Count'];
    this.text_results_GeoLocation_Count = state['text_results_GeoLocation_Count'];
    this.alt_text_results_GeoLocation_Count = state['alt_text_results_GeoLocation_Count'];
    this.img_text_results_GeoLocation_Count = state['img_text_results_GeoLocation_Count'];
    this.total_Ethnicity_text = state['total_Ethnicity_text'];
    this.total_Ethnicity_alt_text = state['total_Ethnicity_alt_text'];
    this.total_Ethnicity_img_text = state['total_Ethnicity_img_text'];
    this.total_GeoLocation_text = state['total_GeoLocation_text'];
    this.total_GeoLocation_alt_text = state['total_GeoLocation_alt_text'];
    this.total_GeoLocation_img_text = state['total_GeoLocation_img_text'];
  }
}

selectOption(option: string){
  this.selectedTextOption = option;
  }

selectOptionForALtText(option:string){
  this.selectedAltOption = option
  }

selectOptionForImage(option:string){
  this.selectedImgTxtOption = option
  }

 selectAnalysis(type: string): void {
    this.selectedAnalysis = type;
    if(this.selectedAnalysis == "textContent"){
        this.analysisTitle = 'Overall Gender Analysis'
      }
    else if(this.selectedAnalysis == "ethnicity"){
        this.analysisTitle = 'Overall Ethnicity Analysis'
      }
    else if(this.selectedAnalysis == "geoLocation"){
       this.analysisTitle = 'Overall GeoLocation Analysis'
      }
  }

ngOnInit(): void {
  // Calculate maxValue after the data has been assigned to text_results_tr_Gender_Count
  if (this.text_results_tr_Gender_Count && this.text_results_tr_Gender_Count.length > 0) {
    this.maxTextValue = Math.max(...this.text_results_tr_Gender_Count.map((item: [string, number]) => item[1]));
  }
  // Calculate maxValue after the data has been assigned to alt_text_results_tr_Gender_Count
  if (this.alt_text_results_tr_Gender_Count && this.alt_text_results_tr_Gender_Count.length > 0) {
    this.maxAltValue = Math.max(...this.alt_text_results_tr_Gender_Count.map((item: [string, number]) => item[1]));
  }
  // Calculate maxValue after the data has been assigned to img_text_results_tr_Gender_Count
  if (this.img_text_results_tr_Gender_Count && this.img_text_results_tr_Gender_Count.length > 0) {
    this.maxImgTxtValue = Math.max(...this.img_text_results_tr_Gender_Count.map((item: [string, number]) => item[1]));
  }

  // Calculate max gender count and corresponding gender
  if (this.overall_gender_count && this.overall_gender_count.length > 0) {
    const totalCount = this.overall_gender_count.reduce((sum: number, current: [string, number]) => sum + current[1], 0);  // Total count of all genders

    const maxEntry = this.overall_gender_count.reduce((max: [string, number], current: [string, number]) => {
      return current[1] > max[1] ? current : max;
    });
    this.maxGenderCount = maxEntry[1];  // The maximum biased count
    this.maxGender = maxEntry[0];  // The corresponding gender (Male/Female)

    // Calculate the percentage of the maximum biased count
    this.maxGenderPercentage = (this.maxGenderCount !== 0 && totalCount !== 0) ? Math.round((this.maxGenderCount/ totalCount)*100): 0;
  }

  // Calculate maxValue after the data has been assigned to text_results_Ethnicity_Count
  if (this.text_results_Ethnicity_Count && this.text_results_Ethnicity_Count.length > 0) {
    this.maxTextEthValue = Math.max(...this.text_results_Ethnicity_Count.map((item: [string, number]) => item[1]));
  }
  // Calculate maxValue after the data has been assigned to alt_text_results_Ethnicity_Count
  if (this.alt_text_results_Ethnicity_Count && this.alt_text_results_Ethnicity_Count.length > 0) {
    this.maxAltEthValue = Math.max(...this.alt_text_results_Ethnicity_Count.map((item: [string, number]) => item[1]));
  }
  // Calculate maxValue after the data has been assigned to img_text_results_Ethnicity_Count
  if (this.img_text_results_Ethnicity_Count && this.img_text_results_Ethnicity_Count.length > 0) {
    this.maxImgTxtEthValue = Math.max(...this.img_text_results_Ethnicity_Count.map((item: [string, number]) => item[1]));
  }

  // Calculate max ethnicity count and corresponding city
  if (this.total_Ethnicity_Count && this.total_Ethnicity_Count.length > 0) {
    const totalEthCount = this.total_Ethnicity_Count.reduce((sum: number, current: [string, number]) => sum + current[1], 0);  // Total count of all ethnicities

    const maxEthEntry = this.total_Ethnicity_Count.reduce((max: [string, number], current: [string, number]) => {
      return current[1] > max[1] ? current : max;
    });
    this.maxEthnicityCount = maxEthEntry[1];  // The maximum biased count
    this.maxEthnicity = maxEthEntry[0];  // The corresponding Ethnicity

    // Calculate the percentage of the maximum biased count
    this.maxEthnicityPercentage = Math.round((this.maxEthnicityCount / totalEthCount) * 100);
  }

  // Calculate maxValue after the data has been assigned to text_results_GeoLocation_Count
  if (this.text_results_GeoLocation_Count && this.text_results_GeoLocation_Count.length > 0) {
    this.maxTextGeoValue = Math.max(...this.text_results_GeoLocation_Count.map((item: [string, number]) => item[1]));
  }
  // Calculate maxValue after the data has been assigned to alt_text_results_GeoLocation_Count
  if (this.alt_text_results_GeoLocation_Count && this.alt_text_results_GeoLocation_Count.length > 0) {
    this.maxAltGeoValue = Math.max(...this.alt_text_results_GeoLocation_Count.map((item: [string, number]) => item[1]));
  }
  // Calculate maxValue after the data has been assigned to img_text_results_GeoLocation_Count
  if (this.img_text_results_GeoLocation_Count && this.img_text_results_GeoLocation_Count.length > 0) {
    this.maxImgTxtGeoValue = Math.max(...this.img_text_results_GeoLocation_Count.map((item: [string, number]) => item[1]));
  }

  // Calculate max GeoLocation count and corresponding country
  if (this.total_GeoLocation_Count && this.total_GeoLocation_Count.length > 0) {
    const totalGeoCount = this.total_GeoLocation_Count.reduce((sum: number, current: [string, number]) => sum + current[1], 0);  // Total count of all locations

    const maxGeoEntry = this.total_GeoLocation_Count.reduce((max: [string, number], current: [string, number]) => {
      return current[1] > max[1] ? current : max;
    });
    this.maxGeoCount = maxGeoEntry[1];  // The maximum geo location count
    this.maxGeo = maxGeoEntry[0];  // The corresponding country location

    // Calculate the percentage of the maximum biased count
    this.maxGeoPercentage = Math.round((this.maxGeoCount / totalGeoCount) * 100);
  }

  this.totalModelCount = this.textmodel_counts.reduce((sum: number, current: [string, number]) => sum + current[1], 0);  // Total count of all text results type

  this.http.get('/baisedwordresults', { responseType: 'json' })
          .subscribe((data: any) => {
           // alert(JSON.stringify(data));
            this.defaultWords = data['baisedword_results'];
           // alert(data);
          });

    this.http.get('/readExcel', { responseType: 'json' })
          .subscribe((data: any) => {
           // alert(JSON.stringify(data));
            this.users = data['excel_data'];
           // alert(data);
          });

 }

 activeTab(content:any,sectionName:string) {
 this.resultSection=sectionName;
this.modalService.open(content,
   {ariaLabelledBy: 'modal-basic-title'}).result.then((result)=> {
      this.closeResult = `Closed with: ${result}`;
    }, (reason) => {
      this.closeResult =
         `Dismissed ${this.getDismissReason(reason)}`;
    });
}

private getDismissReason(reason: any): string {
    if (reason === ModalDismissReasons.ESC) {
      return 'by pressing ESC';
    } else if (reason === ModalDismissReasons.BACKDROP_CLICK) {
      return 'by clicking on a backdrop';
    } else {
      return `with: ${reason}`;
    }
  }

}
