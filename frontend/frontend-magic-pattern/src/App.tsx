import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { Home } from './pages/Home';
import { Dashboard } from './pages/Dashboard';
import { NewsProvider } from './context/NewsContext';
export function App() {
  return <BrowserRouter>
      <NewsProvider>
        <div className="flex w-full min-h-screen bg-[#FBF9F6]">
          <Sidebar />
          <main className="flex-1 ml-44">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/dashboard" element={<Dashboard />} />
            </Routes>
          </main>
        </div>
      </NewsProvider>
    </BrowserRouter>;
}