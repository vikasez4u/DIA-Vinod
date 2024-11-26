import { Component, OnInit, AfterViewInit, Input, ElementRef, ViewChild } from '@angular/core';
import Chart from 'chart.js/auto';
import ChartDataLabels from 'chartjs-plugin-datalabels';

@Component({
  selector: 'app-barchart',
  templateUrl: './barchart.component.html',
  styleUrls: ['./barchart.component.css']
})

export class BarchartComponent implements OnInit, AfterViewInit {
@ViewChild('Chart') ChartRef !: ElementRef;

@Input() data: any;
@Input() chartType!: String;

public Analysis_chart: any = '';

constructor() {}

ngOnInit(): void {}

ngAfterViewInit(){
  Chart.register(ChartDataLabels);
  this.generateChart();
}

generateChart() {
  var Label: any = [];
  var Count: any = [];

  for(var key of this.data){
    Label.push(key[0]);
    Count.push(key[1]);
  }

  const total = Count.reduce((sum: number, count:number) => sum + count, 0); // Calculate total sum of Count

  const percentages = Count.map((count: number) => Math.round((count / total) * 100)); // Calculate percentage for each count

  var d3 = require("d3-scale-chromatic");
  const colorScale = d3.interpolateInferno;

  const colorRangeInfo = {
    colorStart: 0.2,
    colorEnd: 1,
    useEndAsStart: false,
  };

  var Color = this.interpolateColors(percentages.length, colorScale, colorRangeInfo);

  // Check for different chart types and set the configuration accordingly
  if (this.chartType === 'radial-bar') {
    this.Analysis_chart = new Chart(this.ChartRef.nativeElement.getContext('2d'), {
      type: 'doughnut', //this denotes tha type of chart
      data: { // values on X-Axis
        labels: Label,
        datasets: [
          {
            label: "Text Results",
            data: percentages,
            backgroundColor: Color,
            hoverBackgroundColor: Color,
            hoverOffset: 4,
          }
        ]
      },
      options: {
        responsive: true,
        cutout: '70%',
        plugins :{
          legend: {
            position: 'right',
            align: 'start',
            labels: {
              pointStyle: 'circle',
              boxWidth: 2,
              padding: 6,
              usePointStyle: true,
              font: {
                size: 12,
                weight: 'bold'
              },
            }
          },
          datalabels: {
            anchor: 'center',
            align: 'center',
            color: 'white',
            font: {
              size: 14,
              weight: 'bold'
            },
            formatter: (value) => {
              return value+'%';
            }
          }
        },
        layout: {
          padding: {
            left: 0,
            right: 10,
            top: 5,
            bottom: 5
          }
        },
        interaction: {
          mode: 'nearest',
          axis: 'x',
          intersect: false,
        },
      }
    });
  }
else if (this.chartType === 'semi-donut') {
      this.Analysis_chart = new Chart(this.ChartRef.nativeElement.getContext('2d'), {
        type: 'doughnut',
        data: {
          labels: Label,
          datasets: [{
            label: "Results",
            data: percentages,
            backgroundColor: Color,
            hoverBackgroundColor: Color,
          }]
        },
        options: {
          responsive: true,
          cutout: '70%',
          circumference: 180,
          rotation: 270,
          plugins: {
            legend: {
                position: 'right',
                align: 'start',
                labels: {
                  pointStyle: 'circle',
                  boxWidth: 2,
                  padding: 6,
                  usePointStyle: true,
                  font: {
                    size: 12,
                    weight: 'bold'
                  },
                }
            },
            datalabels: {
              anchor: 'center',
              align: 'center',
              color: 'white',
              font: { size: 14, weight: 'bold' },
              formatter: (value) => value + '%'
            }
          },
          interaction: {
            mode: 'nearest',
            axis: 'x',
            intersect: false,
          },
        }
      });
} else{
       this.Analysis_chart = new Chart(this.ChartRef.nativeElement.getContext('2d'), {
          type: 'doughnut', //this denotes tha type of chart

          data: {// values on X-Axis
            labels: Label,
             datasets: [
              {
                label: "Text Results",
                data: percentages,
                backgroundColor: Color,
                hoverBackgroundColor: Color,
                hoverOffset: 4,
              }
            ]
          },
          options: {
            responsive: true,
            plugins :{
              legend: {
                position: 'right',
                align: 'start',
                labels: {
                  pointStyle: 'circle',
                  boxWidth: 2,
                  padding: 6,
                  usePointStyle: true,
                  font: {
                    size: 12,
                    weight: 'bold'
                  },
                }
              },
              datalabels: {
                anchor: 'center',
                align: 'center',
                color: 'white',
                font: {
                  size: 14,
                  weight: 'bold'
                },
                formatter: (value) => {
                  return value+'%';
                }
              }
            },
            layout: {
              padding: {
                left: 0,
                right: 10,
                top: 5,
                bottom: 5
              }
            },
            interaction: {
              mode: 'nearest',
              axis: 'x',
              intersect: false,
            },
          }
       });
    }
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

}
