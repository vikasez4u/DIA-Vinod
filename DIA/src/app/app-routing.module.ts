import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { TextresultComponent } from './baised/textresult/textresult.component';
import { ImageresultComponent } from './baised/imageresult/imageresult.component';
import { ParallelexecComponent } from './baised/parallelexec/parallelexec.component';
import { ContactComponent } from './contact/contact.component';
import { FaqComponent } from './faq/faq.component';
import { HelpPageComponent } from './help-page/help-page.component';

const routes : Routes = [
{ path: 'biased/textresult', component: TextresultComponent},
{ path: 'biased/imageresult', component: ImageresultComponent},
{ path: 'biased/parallelexec', component: ParallelexecComponent},
{ path: 'contact', component: ContactComponent},
{ path: 'faq', component: FaqComponent},
{ path: 'help-page', component: HelpPageComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
export const routingComponents = [TextresultComponent, ImageresultComponent, ParallelexecComponent]
