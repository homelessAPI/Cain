import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useState } from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
  Cell
} from "recharts";
import './App.css'

import Home from "../pages/home"
import Review from "../pages/review"

function App() {
  return (
      <BrowserRouter>
    <Routes>
      
      <Route path="/" element={<Home />} />
      <Route path="/Review" element={<Review />} />

    </Routes>
    </BrowserRouter>
  )
}

export default App;