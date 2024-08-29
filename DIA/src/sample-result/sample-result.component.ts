import { Component ,OnInit} from '@angular/core';

@Component({
  selector: 'app-sample-result',
  templateUrl: './sample-result.component.html',
  styleUrls: ['./sample-result.component.css']
})
export class SampleResultComponent implements OnInit {
  screenshots = [
    { url: 'screenshot1.png', description: 'Screenshot 1' },
    { url: 'screenshot2.png', description: 'Screenshot 2' },
    { url: 'screenshot3.png', description: 'Screenshot 3' },
    { url: 'screenshot4.png', description: 'Screenshot 4' },
    { url: 'screenshot5.png', description: 'Screenshot 5' },
    { url: 'screenshot6.png', description: 'Screenshot 6' },
    { url: 'screenshot7.png', description: 'Screenshot 7' },
    { url: 'screenshot8.png', description: 'Screenshot 8' },
    { url: 'screenshot9.png', description: 'Screenshot 9' },
    { url: 'screenshot10.png', description: 'Screenshot 10' },
    { url: 'screenshot11.png', description: 'Screenshot 11' },
    { url: 'screenshot12.png', description: 'Screenshot 12' },
    { url: 'screenshot13.png', description: 'Screenshot 13' },
    { url: 'screenshot14.png', description: 'Screenshot 14' },
    { url: 'screenshot15.png', description: 'Screenshot 15' },
    { url: 'screenshot16.png', description: 'Screenshot 16' },
    { url: 'screenshot17.png', description: 'Screenshot 17' },
    { url: 'screenshot18.png', description: 'Screenshot 18' },
    { url: 'screenshot19.png', description: 'Screenshot 19' },
    { url: 'screenshot20.png', description: 'Screenshot 20' },
//     { url: 'screenshot21.png', description: 'Screenshot 21' },
//     { url: 'screenshot22.png', description: 'Screenshot 22' },
//     { url: 'screenshot23.png', description: 'Screenshot 23' },
//     { url: 'screenshot24.png', description: 'Screenshot 24' },
//     { url: 'screenshot25.png', description: 'Screenshot 25' },
//     { url: 'screenshot26.png', description: 'Screenshot 26' },
//     { url: 'screenshot27.png', description: 'Screenshot 27' },
//     { url: 'screenshot28.png', description: 'Screenshot 28' },
//     { url: 'screenshot29.png', description: 'Screenshot 29' },
//     { url: 'screenshot30.png', description: 'Screenshot 30' },
  ];


  constructor() { }

  ngOnInit(): void {
  }
}

