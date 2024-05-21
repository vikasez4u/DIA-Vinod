import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { FileComponent } from '../fileupload/file/file.component';
import { FileUploadRoutingModule } from './fileupload-routing. module';
import { RouterModule, Routes } from '@angular/router';
import { BaisedComponent } from './baised/baised.component';
const routes: Routes = [
  { path: 'file', component: FileComponent, outlet: 'file'},
  { path: 'home', component: BaisedComponent, outlet: 'home'}
];


@NgModule({
  declarations: [
  FileComponent,
  BaisedComponent
  ],
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    RouterModule.forRoot(routes)
  ],
  exports: [RouterModule]
})
export class FileUploadModule { }
