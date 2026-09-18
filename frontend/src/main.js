import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/Css/Home.css'
import './assets/Css/EventDetail.css'


// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyBkbobfl8Psq2rSn42BGTjrY82QDZENiOg",
  // En prod, la popup OAuth passe par notre domaine (nginx proxifie /__/auth/ vers Firebase),
  // sinon Safari et Firefox bloquent le retour de connexion (cookies tiers)
  authDomain: import.meta.env.PROD ? "events.leaballester.com" : "my-events-68dbd.firebaseapp.com",
  projectId: "my-events-68dbd",
  storageBucket: "my-events-68dbd.firebasestorage.app",
  messagingSenderId: "643202876060",
  appId: "1:643202876060:web:6d075d24eeb9dbc8a26359",
};

// Initialize Firebase
initializeApp(firebaseConfig);

const app = createApp(App);

app.use(router);

app.mount("#app");
