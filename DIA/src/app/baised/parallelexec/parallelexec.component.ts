import { Component, OnInit, Injectable } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-parallelexec',
  templateUrl: './parallelexec.component.html',
  styleUrls: ['./parallelexec.component.css']
})

@Injectable({
  providedIn: 'root'
})

export class ParallelexecComponent implements OnInit {
selectedTab: number = 1;
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
image_biased_results: any;
image_results_Count: any;
image_results_Gender_Count: any[] = [];
image_results_Confidence_Count: any[] = [];
image_results_Skin_Color_Count: any[] = [];
image_results_Race_Count: any[] = [];
//parallelexecScript: HTMLScriptElement;

constructor(private router: Router, private activatedRoute: ActivatedRoute){
  let state = this.router.getCurrentNavigation()?.extras.state;

  if (state) {
    this.modelType = state['modelType'];
    this.biased_txt_results = state['biased_txt_results'];
    this.biased_alt_results = state['biased_alt_results'];
    this.biased_img_results = state['biased_img_results'];
    this.total_biased_text = state['total_biased_text'];
    this.total_biased_alt_text = state['total_biased_alt_text'];
    this.total_biased_img_results = state['total_biased_img_results'];
    this.text_results_tr_Gender_Count = state['text_results_tr_Gender_Count'];
    this.alt_text_results_tr_Gender_Count = state['alt_text_results_tr_Gender_Count'];
    this.img_text_results_tr_Gender_Count = state['img_text_results_tr_Gender_Count'];
    this.image_biased_results = state['image_biased_results'];
    this.image_results_Count = state['image_results_Count'];
    this.image_results_Gender_Count = state['image_results_Gender_Count'];
    this.image_results_Confidence_Count = state['image_results_Confidence_Count'];
    this.image_results_Skin_Color_Count = state['image_results_Skin_Color_Count'];
    this.image_results_Race_Count = state['image_results_Race_Count'];
  }

  /**this.parallelexecScript = document.createElement("script");
  this.parallelexecScript.src = "src/assets/parallelexecScript.js";
  document.body.appendChild(this.parallelexecScript);**/
}

ngOnInit(): void {}

}


