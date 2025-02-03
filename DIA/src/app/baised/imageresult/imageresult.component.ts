import { Component, OnInit, Injectable, Input } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { HttpClient } from "@angular/common/http";
import {NgbModal, ModalDismissReasons}  from '@ng-bootstrap/ng-bootstrap';
import Swiper from 'swiper';
import { Navigation, Pagination } from 'swiper/modules';

//declare function runImage(): void;

Swiper.use([Navigation, Pagination]);

@Component({
  selector: 'app-imageresult',
  templateUrl: './imageresult.component.html',
  styleUrls: ['./imageresult.component.css']
})

@Injectable({
  providedIn: 'root'
})

export class ImageresultComponent implements OnInit{
//@Input() marginTop: string = '70px'; // Default value
modelType: any;
image_biased_results: any;
image_results_Count: any;
image_results_Gender_Count: any[] = [];
image_results_Confidence_Count: any[] = [];
image_results_Skin_Color_Count: any[] = [];
image_results_Race_Count: any[] = [];

maxImgGenderCount: number = 0;  // For maximum biased gender count
maxImgGender: string = '';  // For the gender associated with the maximum count
maxImgGenderPercentage: number = 0;  // For the percentage of the maximum biased count

maxImgConfidenceCount: number = 0;  // For maximum biased confidence count
maxImgConfidence: string = '';  // For the confidence associated with the maximum count
maxImgConfidencePercentage: number = 0;  // For the percentage of the maximum biased count

maxImgSkinColorCount: number = 0;  // For maximum biased skin color count
maxImgSkinColor: string = '';  // For the skin color associated with the maximum count
maxImgSkinColorPercentage: number = 0;  // For the percentage of the maximum biased count

maxImgRaceCount: number = 0;  // For maximum biased race count
maxImgRace: string = '';  // For the race associated with the maximum count
maxImgRacePercentage: number = 0;  // For the percentage of the maximum biased count

users: any[] = [];
defaultWords: any[] = [];
closeResult = '';

resultSection: string = '';

constructor(private router: Router, private activatedRoute: ActivatedRoute, private http: HttpClient, private modalService: NgbModal){
  let state = this.router.getCurrentNavigation()?.extras.state;

  if (state) {
    //this.modelType = state['modelType'];
    this.modelType = "Image";
    this.image_biased_results = state['image_biased_results'];
    this.image_results_Count = state['image_results_Count'];
    this.image_results_Gender_Count = state['image_results_Gender_Count'];
    this.image_results_Confidence_Count = state['image_results_Confidence_Count'];
    this.image_results_Skin_Color_Count = state['image_results_Skin_Color_Count'];
    this.image_results_Race_Count = state['image_results_Race_Count'];
  }
}

ngOnInit(): void {
  //runImage();
  const swiper = new Swiper('.swiper-container', {
      loop: true,
      slidesPerView: 1,
      spaceBetween: 10,
      navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
      },
      pagination: {
        el: '.swiper-pagination',
        clickable: true,
      },
      modules: [Navigation, Pagination]
  });

  // Calculate max gender count and corresponding gender
  if (this.image_results_Gender_Count && this.image_results_Gender_Count.length > 0) {
    const totalImgGenderCount = this.image_results_Gender_Count.reduce((sum: number, current: [string, number]) => sum + current[1], 0);  // Total count of all genders

    const maxImgGenderEntry = this.image_results_Gender_Count.reduce((max: [string, number], current: [string, number]) => {
      return current[1] > max[1] ? current : max;
    });
    this.maxImgGenderCount = maxImgGenderEntry[1];  // The maximum biased count
    this.maxImgGender = maxImgGenderEntry[0];  // The corresponding gender (Male/Female)

    // Calculate the percentage of the maximum biased count
    this.maxImgGenderPercentage = (this.maxImgGenderCount !== 0 && totalImgGenderCount !== 0) ? Math.round((this.maxImgGenderCount / totalImgGenderCount) * 100): 0;
  }

  // Calculate max confidence count and corresponding confidence
  if (this.image_results_Confidence_Count && this.image_results_Confidence_Count.length > 0) {
    const totalImgConfidenceCount = this.image_results_Confidence_Count.reduce((sum: number, current: [string, number]) => sum + current[1], 0);  // Total count of all confidence

    const maxImgConfidenceEntry = this.image_results_Confidence_Count.reduce((max: [string, number], current: [string, number]) => {
      return current[1] > max[1] ? current : max;
    });
    this.maxImgConfidenceCount = maxImgConfidenceEntry[1];  // The maximum biased count
    this.maxImgConfidence = maxImgConfidenceEntry[0];  // The corresponding confidence

    // Calculate the percentage of the maximum biased count
    this.maxImgConfidencePercentage = Math.round((this.maxImgConfidenceCount / totalImgConfidenceCount) * 100);
  }

  // Calculate max skin color count and corresponding skin color
  if (this.image_results_Skin_Color_Count && this.image_results_Skin_Color_Count.length > 0) {
    const totalImgColorCount = this.image_results_Skin_Color_Count.reduce((sum: number, current: [string, number]) => sum + current[1], 0);  // Total count of all skin color

    const maxImgColorEntry = this.image_results_Skin_Color_Count.reduce((max: [string, number], current: [string, number]) => {
      return current[1] > max[1] ? current : max;
    });
    this.maxImgSkinColorCount = maxImgColorEntry[1];  // The maximum biased count
    this.maxImgSkinColor = maxImgColorEntry[0];  // The corresponding skin color

    // Calculate the percentage of the maximum biased count
    this.maxImgSkinColorPercentage = Math.round((this.maxImgSkinColorCount / totalImgColorCount) * 100);
  }

  // Calculate max race count and corresponding race
  if (this.image_results_Race_Count && this.image_results_Race_Count.length > 0) {
    const totalImgRaceCount = this.image_results_Race_Count.reduce((sum: number, current: [string, number]) => sum + current[1], 0);  // Total count of all genraceders

    const maxImgRaceEntry = this.image_results_Race_Count.reduce((max: [string, number], current: [string, number]) => {
      return current[1] > max[1] ? current : max;
    });
    this.maxImgRaceCount = maxImgRaceEntry[1];  // The maximum biased count
    this.maxImgRace = maxImgRaceEntry[0];  // The corresponding race

    // Calculate the percentage of the maximum biased count
    this.maxImgRacePercentage = Math.round((this.maxImgRaceCount / totalImgRaceCount) * 100);
  }

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
