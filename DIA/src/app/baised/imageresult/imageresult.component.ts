import { Component, OnInit, Injectable } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-imageresult',
  templateUrl: './imageresult.component.html',
  styleUrls: ['./imageresult.component.css']
})

@Injectable({
  providedIn: 'root'
})

export class ImageresultComponent implements OnInit{

modelType: any;
image_biased_results: any;
image_results_tr: any;

constructor(private router: Router, private activatedRoute: ActivatedRoute){
  let state = this.router.getCurrentNavigation()!.extras.state;

  if (state) {
    this.modelType = state['modelType'];
    this.image_biased_results = state['image_biased_results'];
    this.image_results_tr = state['image_results_tr'];
  }
}

ngOnInit(): void {}

}
