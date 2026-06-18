// firebaseConfig.js
// Configuración de Firebase para la persistencia del dron explorador.
 
import { initializeApp } from "firebase/app";
import { getDatabase } from "firebase/database";
 
const firebaseConfig = {
  apiKey: "AIzaSyDCxXngPqWhiAUWg9QuDBVMeHSQZUd7NSE",
  authDomain: "taller-semana-15---4.firebaseapp.com",
  databaseURL: "https://taller-semana-15---4-default-rtdb.firebaseio.com",
  projectId: "taller-semana-15---4",
  storageBucket: "taller-semana-15---4.firebasestorage.app",
  messagingSenderId: "168056280073",
  appId: "1:168056280073:web:ab97a2fab7423b9a6f14d8",
  measurementId: "G-QL6ER3PLS2",
};
 
// Initialize Firebase
const app = initializeApp(firebaseConfig);
 
// Exportamos la referencia a Realtime Database — esto es lo que
// usa useDronePersistence.js para leer y guardar la posición del dron.
export const db = getDatabase(app);