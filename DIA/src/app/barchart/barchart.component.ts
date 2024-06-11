import { Component, OnInit, AfterViewInit, Input, ElementRef, ViewChild } from '@angular/core';
import Chart from 'chart.js/auto';

@Component({
  selector: 'app-barchart',
  templateUrl: './barchart.component.html',
  styleUrls: ['./barchart.component.css']
})

export class BarchartComponent implements OnInit, AfterViewInit {
@ViewChild('ImgGenChart') imgGenChartRef !: ElementRef;
@ViewChild('TextChart') txtChartRef !: ElementRef;
@ViewChild('AltChart') altChartRef !: ElementRef;
@ViewChild('ImgChart') imgChartRef !: ElementRef;

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

ngOnInit(): void {}

ngAfterViewInit(){
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
  imageLabel.push('Male','Female');
  for(var key of this.image_results_tr){
    imageData.push(key[0]);
    imageData.push(key[1]);
  }
}

this.createChart(textLabel, textData, altLabel, altData, imgLabel, imgData, imageLabel, imageData, modelTextFlag, modelImgFlag);

}

calculatePoint(i: number, intervalSize: any, colorRangeInfo: any) {
  var { colorStart, colorEnd, useEndAsStart } = colorRangeInfo;
  return (useEndAsStart
    ? (colorEnd - (i * intervalSize))
    : (colorStart + (i * intervalSize)));
}

interpolateColors(dataLength: number, colorScale: any, colorRangeInfo: any) {
  var { colorStart, colorEnd } = colorRangeInfo;
  var colorRange = colorEnd - colorStart;
  var intervalSize = colorRange / dataLength;
  var i, colorPoint;
  var colorArray = [];

  for (i = 0; i < dataLength; i++) {
    colorPoint = this.calculatePoint(i, intervalSize, colorRangeInfo);
    colorArray.push(colorScale(colorPoint));
  }

  return colorArray;
}

createChart(textLabel:any[], textData:any[], altLabel:any[], altData:any[], imgLabel:any[], imgData:any[], imageLabel:any[], imageData:any[], modelTextFlag: boolean, modelImgFlag:boolean){
var d3 = require("d3-scale-chromatic");
const colorScale = d3.interpolateInferno;

const colorRangeInfo = {
  colorStart: 0.2,
  colorEnd: 1,
  useEndAsStart: false,
};

var txtColor = this.interpolateColors(textData.length, colorScale, colorRangeInfo);
var altColor = this.interpolateColors(altData.length, colorScale, colorRangeInfo);
var imgColor = this.interpolateColors(imgData.length, colorScale, colorRangeInfo);
var imageColor = this.interpolateColors(imageData.length, colorScale, colorRangeInfo);

    if(modelTextFlag){
        this.textChart = new Chart(this.txtChartRef.nativeElement.getContext('2d'), {
          type: 'pie', //this denotes tha type of chart

          data: {// values on X-Axis
            labels: textLabel,
             datasets: [
              {
                label: "Text Results",
                data: textData,
                backgroundColor: txtColor,
                hoverBackgroundColor: txtColor,
                //barThickness: 40,
                //borderRadius: 3,
                //inflateAmount: 'auto',
                //pointStyle: 'circle',
                hoverOffset: 4,
              }
            ]
          },
          options: {
            plugins: {
              title: {
                display: true,
                text: 'Text Results'
              }
            }
          }
        });

      this.textAltChart = new Chart(this.altChartRef.nativeElement.getContext('2d'), {
          type: 'pie', //this denotes tha type of chart

          data: {// values on X-Axis
            labels: altLabel,
             datasets: [
              {
                label: "Alt Text Results",
                data: altData,
                backgroundColor: altColor,
                hoverBackgroundColor: altColor,
                //barThickness: 40,
                //borderRadius: 3,
                //inflateAmount: 'auto',
                //pointStyle: 'circle',
                hoverOffset: 4,
              }
            ]
          },
          options: {
            plugins: {
              title: {
                display: true,
                text: 'Alt Text Results'
              }
            }
          }
        });

      this.textImgChart = new Chart(this.imgChartRef.nativeElement.getContext('2d'), {
          type: 'pie', //this denotes tha type of chart

          data: {// values on X-Axis
            labels: imgLabel,
             datasets: [
              {
                label: "Image Text Results",
                data: imgData,
                backgroundColor: imgColor,
                hoverBackgroundColor: imgColor,
                //barThickness: 40,
                //borderRadius: 3,
                //inflateAmount: 'auto',
                //pointStyle: 'circle',
                hoverOffset: 4,
              }
            ]
          },
          options: {
            plugins: {
              title: {
                display: true,
                text: 'Image Text Results'
              }
            }
          }
        });
    }
    if(modelImgFlag){
      this.imageGenderChart = new Chart(this.imgGenChartRef.nativeElement.getContext('2d'), {
            type: 'pie', //this denotes tha type of chart

            data: {// values on X-Axis
              labels: imageLabel,
               datasets: [
                {
                  label: "Image Results",
                  data: imageData,
                  backgroundColor: imageColor,
                  hoverBackgroundColor: imageColor,
                  //barThickness: 40,
                  //borderRadius: 3,
                  //inflateAmount: 'auto',
                  //pointStyle: 'circle',
                  hoverOffset: 4,
                }
              ]
            },
            options: {
              plugins: {
                title: {
                  display: true,
                  text: 'Image Results'
                }
              }
          }
      });
    }
  }
}
