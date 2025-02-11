import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { AppRoutingModule, routingComponents } from './app-routing.module';
import { AppComponent } from './app.component';
import { BaisedComponent } from './baised/baised.component';
import { FileComponent } from './fileupload/file/file.component';
import { RouterModule, Routes } from '@angular/router';
import { HttpClientModule } from '@angular/common/http';
import { HeaderComponent } from './header/header.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { NgxSpinnerModule } from 'ngx-spinner';
import {APP_BASE_HREF} from '@angular/common';
import { BarchartComponent } from './barchart/barchart.component';
import { TextresultComponent } from './baised/textresult/textresult.component';
import { ImageresultComponent } from './baised/imageresult/imageresult.component';
import { ParallelexecComponent } from './baised/parallelexec/parallelexec.component';
import { ConfigurationComponent } from './configuration/configuration.component';
import { PanelMenuModule } from 'primeng/panelmenu';
import { GenderComponent } from './configuration/gender/gender.component';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { BaisedwordsComponent } from './configuration/baisedwords/baisedwords.component';
import { ContactComponent } from './contact/contact.component';
import { FaqComponent } from './faq/faq.component';
import { AccordionModule } from 'primeng/accordion';
import { BadgeModule } from 'primeng/badge';
import { AboutComponent } from './about/about.component';
import { FooterComponent } from './footer/footer.component';
import { SampleResultComponent } from '../sample-result/sample-result.component';
import { EthnicityComponent } from './configuration/ethnicity/ethnicity.component';
import { GeolocationComponent } from './configuration/geolocation/geolocation.component';

const routes : Routes = [
{ path: 'home', component: BaisedComponent},
{ path: 'fileupload/file', component: FileComponent},
{ path: 'config', component: ConfigurationComponent},
{ path: 'gender', component: GenderComponent},
{ path: 'baisedwords', component: BaisedwordsComponent},
{ path: 'faq', component: FaqComponent},
{ path: 'contact', component : ContactComponent},
{ path: 'about', component : AboutComponent},
{ path: 'report',component: SampleResultComponent},
{ path: "**", component: BaisedComponent}
];

@NgModule({
  declarations: [
    AppComponent,
    BaisedComponent,
    FileComponent,
    HeaderComponent,
    BarchartComponent,
    TextresultComponent,
    ImageresultComponent,
    ParallelexecComponent,
    routingComponents,
    ConfigurationComponent,
    GenderComponent,
    BaisedwordsComponent,
    ContactComponent,
    FaqComponent,
    AboutComponent,
    FooterComponent,
    SampleResultComponent,
    EthnicityComponent,
    GeolocationComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,
    BrowserAnimationsModule,
    NgxSpinnerModule,
    HttpClientModule,
    PanelMenuModule,
    NgbModule,
    AccordionModule,
    BadgeModule,
    RouterModule.forRoot(routes)
  ],
  providers: [{provide: APP_BASE_HREF, useValue: '/dia/'}],
  bootstrap: [AppComponent],
  exports: [RouterModule]
})
export class AppModule { }
