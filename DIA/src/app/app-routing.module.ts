import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { TextresultComponent } from './baised/textresult/textresult.component';
import { ImageresultComponent } from './baised/imageresult/imageresult.component';

const routes : Routes = [
{ path: 'biased/textresult', component: TextresultComponent},
{ path: 'biased/imageresult', component: ImageresultComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
export const routingComponents = [TextresultComponent, ImageresultComponent]
