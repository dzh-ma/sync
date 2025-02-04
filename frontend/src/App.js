//import logo from './logo.svg';
//import './App.css';
//
//function App() {
//  return (
//    <div className="App">
//      <header className="App-header">
//        <img src={logo} className="App-logo" alt="logo" />
//        <p>
//          Edit <code>src/App.js</code> and save to reload.
//        </p>
//        <a
//          className="App-link"
//          href="https://reactjs.org"
//          target="_blank"
//          rel="noopener noreferrer"
//        >
//          Learn React
//        </a>
//      </header>
//    </div>
//  );
//}
//
//export default App;

import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login1 from "./screens/login1";
import Login2 from "./screens/login2"; 
import Register from "./screens/register1";
import Register2 from "./screens/register2";
import Register3 from "./screens/register3";
import Dashboard1 from "./screens/dashboard1";
import './App.css';
import { UserProvider } from './UserContext';

function App() {
  return (
    <UserProvider>
      <Router>
        <div style={{ textAlign: "center", margin: "20px" }}>
          <h1>Sync Back-end Testing</h1>
          <Routes>
            <Route path="/" element={<Login1 />} /> 
            <Route path="/dashboard1" element={<Dashboard1 />} />
            <Route path="/login2" element={<Login2 />} /> 
            <Route path="/register1" element={<Register />} />
            <Route path="/register2" element={<Register2 />} />
            <Route path="/register3" element={<Register3 />} />
          </Routes>
        </div>
      </Router>
    </UserProvider>
  );
}

export default App;
