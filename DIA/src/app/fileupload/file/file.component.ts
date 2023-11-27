import { Component, OnInit, ElementRef, ViewChild } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { throwError } from "rxjs";
const uploadURL = "http://localhost:3000/upload_files";
import { read, utils, writeFile } from 'xlsx';

@Component({
  selector: "app-file",
  templateUrl: "./file.component.html",
  styleUrls: ["./file.component.css"],
})
export class FileComponent implements OnInit {
  status: "initial" | "uploading" | "success" | "fail" = "initial"; // Variable to store file status
  file: File | null = null; // Variable to store file
  users: any[] = [];
  constructor(private http: HttpClient) {}
  filename='';
  ngOnInit(): void {
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
