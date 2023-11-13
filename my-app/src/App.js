import React from 'react';
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import LogIn from "./pages/LogIn";
import CreateAccount from "./pages/CreateAccount";
import NoPage from "./pages/NoPage";
import Dashboard from "./pages/Dashboard";
import Project from "./pages/Project";
import Profile from "./pages/Profile";
import UserSearch from "./pages/UserSearch";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />}>
          <Route path="/login" element={<LogIn />} />
          <Route path="/createaccount" element={<CreateAccount />} />
        </Route>
        <Route path="*" element={<NoPage />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/project/:id" element={<Project />} />
        <Route path="/profile/:username" element={<Profile />} />
        <Route path="/search/:query" element={<UserSearch />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
