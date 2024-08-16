import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrl: './app.component.sass'
})
export class AppComponent implements OnInit {
  title = 'Rag Chatbot';
  query = "";
  chat_response = ""; 
  backendHost = '10.0.0.128';
  backend_url = '/api';

  constructor(private http: HttpClient) {}

  ngOnInit() {
   this.http.get('/assets/config.json').subscribe((config: any) => {
       this.backendHost = config.backendHost;
   });
  }

  submit(){
    const predict_url = this.backendHost + this.backend_url + "/predict"
    this.http.post(predict_url, {'query' : this.query}).subscribe(
          (response: any) => {
            console.log(response);
            this.chat_response = response.chat_response;
          },
          (error) => {
            console.log('Error sending data:', error);
          }
        );
  }  
}
