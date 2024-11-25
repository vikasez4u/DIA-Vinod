import { Component, OnInit, Injectable  } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';

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

constructor(private router: Router, private activatedRoute: ActivatedRoute){
  let state = this.router.getCurrentNavigation()!.extras.state;

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
  }
}

ngOnInit(): void {}

}
