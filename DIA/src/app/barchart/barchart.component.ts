import { Component, OnInit, Input } from '@angular/core';
import Chart from 'chart.js/auto';

@Component({
  selector: 'app-barchart',
  templateUrl: './barchart.component.html',
  styleUrls: ['./barchart.component.css']
})
export class BarchartComponent implements OnInit {

modelTextFlag : boolean = false;
modelImgFlag : boolean = false;
@Input() contentType: any;
@Input() total_biased_text: any;
@Input() total_biased_alt_text: any;
@Input() total_biased_img_results: any;
@Input() text_results_tr_Gender_Count: any;
@Input() alt_text_results_tr_Gender_Count: any;
@Input() img_text_results_tr_Gender_Count: any;
@Input() image_results_tr: any;

public textChart: any = '';
public textAltChart: any = '';
public textImgChart: any = '';
public imageGenderChart: any = '';

constructor() {
      this.modelTextFlag = false;
      this.modelImgFlag = false;
 }

ngOnInit(): void {

    if(this.contentType == "Text"){
      this.modelTextFlag = true;
      this.modelImgFlag = false;
    }
    else if(this.contentType == "Image"){
     this.modelImgFlag = true;
     this.modelTextFlag = false;
     //this.getImageData();
    }
    else{
      this.modelTextFlag = true;
      this.modelImgFlag = true;
      //this.getImageData();
    }
    this.getData(this.modelTextFlag,this.modelImgFlag);
  }

getData(modelTextFlag: boolean,modelImgFlag : boolean) {
var textLabel: any = [];
var textData: any = [];
var altLabel: any = [];
var altData: any = [];
var imgLabel: any = [];
var imgData: any = [];
var imageLabel: any = [];
var imageData: any = [];

if(modelTextFlag){
  for(var key of this.text_results_tr_Gender_Count){
    textLabel.push(key[0]);
    textData.push(key[1]);
  }

  for(var key of this.alt_text_results_tr_Gender_Count){
    altLabel.push(key[0]);
    altData.push(key[1]);
  }

  for(var key of this.img_text_results_tr_Gender_Count){
    imgLabel.push(key[0]);
    imgData.push(key[1]);
  }
}

if(modelImgFlag){
  for(var key of this.image_results_tr){
    imageLabel.push(key[0]);
    imageData.push(key[1]);
  }
}

this.createChart(textLabel, textData, altLabel, altData, imgLabel, imgData, imageLabel, imageData, modelTextFlag, modelImgFlag);

/*const fetchRes = fetch('/output', { "method": "GET"})

    fetchRes
    .then((res: Response) => res.json())
    .then((d: any) => {
      //this.textGenderCount = d['text_results_tr_Gender_Count'];
      //this.altGenderCount = d['alt_text_results_tr_Gender_Count'];
      //this.imgGenderCount = d['img_text_results_tr_Gender_Count'];
      var textLabel: any = [];
      var textData: any = [];
      var altLabel: any = [];
      var altData: any = [];
      var imgLabel: any = [];
      var imgData: any = [];

      for(var key of d['text_results_tr_Gender_Count']){
        textLabel.push(key[0]);
        textData.push(key[1]);
      }

      for(var key of d['alt_text_results_tr_Gender_Count']){
        altLabel.push(key[0]);
        altData.push(key[1]);
      }

      for(var key of d['img_text_results_tr_Gender_Count']){
        imgLabel.push(key[0]);
        imgData.push(key[1]);
      }

      this.createChart(textLabel, textData, altLabel, altData, imgLabel, imgData);
    },
    err => {
      alert("error while getting initial data :::  " + err.message);
      console.log("error while getting initial data" + err.message);
    });*/
}

getImageData() {
alert("In getImageData method");
var imageLabel: any = [];
var imageData: any = [];

for(var key of this.image_results_tr){
  imageLabel.push(key[0]);
  imageData.push(key[1]);
}
alert(imageLabel);
alert(imageData);
this.createImageChart(imageLabel, imageData);

}

createChart(textLabel:any[], textData:any[], altLabel:any[], altData:any[], imgLabel:any[], imgData:any[], imageLabel:any[], imageData:any[], modelTextFlag: boolean, modelImgFlag:boolean){

    if(modelTextFlag){
        this.textChart = new Chart("TextChart", {
          type: 'bar', //this denotes tha type of chart

          data: {// values on X-Axis
            labels: textLabel,
             datasets: [
              {
                label: "Text Results",
                data: textData,
                backgroundColor: '#FF6961',
                barThickness: 40,
                borderRadius: 3,
                inflateAmount: 'auto',
                pointStyle: 'circle',
              }
            ]
          }
        });

      this.textAltChart = new Chart("AltChart", {
          type: 'bar', //this denotes tha type of chart

          data: {// values on X-Axis
            labels: altLabel,
             datasets: [
              {
                label: "Alt Text Results",
                data: altData,
                backgroundColor: '#836953',
                barThickness: 40,
                borderRadius: 3,
                inflateAmount: 'auto',
                pointStyle: 'circle',
              }
            ]
          }

        });

      this.textImgChart = new Chart("ImgChart", {
          type: 'bar', //this denotes tha type of chart

          data: {// values on X-Axis
            labels: imgLabel,
             datasets: [
              {
                label: "Image Text Results",
                data: imgData,
                backgroundColor: 'Orange',
                barThickness: 40,
                borderRadius: 3,
                inflateAmount: 'auto',
                pointStyle: 'circle',
              }
            ]
          }

        });

        this.imageGenderChart = '';
    }
    if(modelImgFlag){
      this.imageGenderChart = new Chart("ImgGenChart", {
            type: 'bar', //this denotes tha type of chart

            data: {// values on X-Axis
              labels: imageLabel,
               datasets: [
                {
                  label: "Image Results",
                  data: imageData,
                  backgroundColor: '#FF6961',
                  barThickness: 40,
                  borderRadius: 3,
                  inflateAmount: 'auto',
                  pointStyle: 'circle',
                }
              ]
            }
          });
    }
    //alert(this.modelTextFlag);
    //alert(this.modelImgFlag);
    //alert(this.textChart);
    //alert(this.textChart.length);
    //alert(this.textChart.size);
  }

  createImageChart(imageLabel:any[], imageData:any[]){
    alert("In createImageChart method")
    alert(imageLabel);
    alert(imageData);

    this.imageGenderChart = new Chart("ImgGenChart", {
      type: 'bar', //this denotes tha type of chart

      data: {// values on X-Axis
        labels: imageLabel,
	       datasets: [
          {
            label: "Image Results",
            data: imageData,
            backgroundColor: '#FF6961',
            barThickness: 40,
            borderRadius: 3,
            inflateAmount: 'auto',
            pointStyle: 'circle',
          }
        ]
      }
    });
  }

}
