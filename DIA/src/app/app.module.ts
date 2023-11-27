import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import {FormsModule} from '@angular/forms';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BaisedComponent } from './baised/baised.component';
import { FileComponent } from './fileupload/file/file.component';
import { RouterModule, Routes } from '@angular/router';
import { HttpClientModule } from '@angular/common/http';
import { HeaderComponent } from './header/header.component';

const routes : Routes = [
{ path: '', component: BaisedComponent},
{ path: 'fileupload/file', component: FileComponent},
{ path: "**", component: BaisedComponent}
];

@NgModule({
  declarations: [
    AppComponent,
    BaisedComponent,
    FileComponent,
    HeaderComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,
    HttpClientModule,
    RouterModule.forRoot(routes)
  ],
  providers: [],
  bootstrap: [AppComponent],
  exports: [RouterModule]
})
export class AppModule { }
