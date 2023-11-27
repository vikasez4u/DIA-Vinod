import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { FileComponent } from '../fileupload/file/file.component';
import { FileUploadRoutingModule } from './fileupload-routing. module';
import { RouterModule, Routes } from '@angular/router';

const routes: Routes = [
  { path: 'file', component: FileComponent, outlet: 'file'}
];


@NgModule({
  declarations: [
  FileComponent
  ],
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    RouterModule.forChild(routes)
  ],
  exports: [RouterModule]
})
export class FileUploadModule { }
