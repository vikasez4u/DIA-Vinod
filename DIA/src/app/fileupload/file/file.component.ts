import { Component, OnInit, ElementRef, ViewChild } from "@angular/core";
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { HttpClient } from "@angular/common/http";
import { throwError } from "rxjs";
const uploadURL = "http://localhost:3000/upload_files";
import { read, utils, writeFile } from 'xlsx';
import { Router, ActivatedRoute } from '@angular/router';

@Component({
  selector: "app-file",
  templateUrl: "./file.component.html",
  styleUrls: ["./file.component.css"],
})
export class FileComponent implements OnInit {
  status: "initial" | "uploading" | "success" | "fail" = "initial"; // Variable to store file status
  file: File | null = null; // Variable to store file
  users: any[] = [];
  defaultwords: any[] = [];
  constructor(private modalService: NgbModal, private http: HttpClient, route:ActivatedRoute) {
    /* route.params.subscribe(val => {
      this.http.get('assets/defaultwords.xlsx', { responseType: 'blob' })
          .subscribe((data: any) => {
           // alert(data);
            const reader: FileReader = new FileReader();
            reader.readAsArrayBuffer(data);
            reader.onload = (event: any) => {
            //alert(event);
              const wb =read(event.target.result);
              const sheets = wb.SheetNames;

              if(sheets.length){
                const rows = utils.sheet_to_json(wb.Sheets[sheets[0]]);
                this.defaultwords =rows;
                //alert("called");
              }
            };
          });
    }); */

  }

  filename='';
  ngOnInit(){
      this.http.get('/baisedwordresults', { responseType: 'json' })
          .subscribe((data: any) => {
           // alert(JSON.stringify(data));
            this.defaultwords = data['baisedword_results'];
           // alert(data);
          });
    this.readexcel();
  }

 readexcel(){
  this.http.get('/readExcel', { responseType: 'json' })
          .subscribe((data: any) => {
           // alert(JSON.stringify(data));
            this.users = data['excel_data'];
           // alert(data);
          });
}
  // On file Select
  onChange(event: any) {
    const files = event.target.files;

    if (files.length) {
      this.status = "initial";
      const file = files[0];
      if(file.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'){
        this.file = file;
        const reader = new FileReader();
        reader.onload = (event: any) => {
          const wb =read(event.target.result);
          const sheets = wb.SheetNames;

          if(sheets.length){
            const rows = utils.sheet_to_json(wb.Sheets[sheets[0]]);
            this.users =rows;
          }
        };
        reader.readAsArrayBuffer(file);
      }else{
        alert("Please Upload Excel File only");
        this.filename='';
        this.file= null;
      }
    }
  }

  onDownload() {
    const workbook = utils.table_to_book(this.table.nativeElement)
    writeFile(workbook,'gender_biased_words.xlsx')
  }

  @ViewChild("table")table !: ElementRef

  onUpload() {
        if (this.file) {

          const reader = new FileReader();
          const formData = new FormData();

          formData.append('file', this.file, this.file.name);

          const upload$ = this.http.post(uploadURL, formData);

          this.status = 'uploading';

          upload$.subscribe({
            next: (res) => {
              //alert(res);
              this.status = 'success';
            },
            error: (error: any) => {
              //alert(error[0]);
              this.status = 'fail';
              return throwError(() => error);
            },
          });
        }
  }
}
