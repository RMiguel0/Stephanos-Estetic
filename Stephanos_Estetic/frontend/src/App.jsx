// src/App.jsx
import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import Footer from "./components/Footer.jsx";
import Home from "./pages/Home.jsx";
import Services from "./pages/Services.jsx";
import Products from "./pages/Products.jsx";
import Contact from "./pages/Contact.jsx";
import Personalization from "./pages/Personalization.jsx";
import Cart from "./pages/Cart.jsx";

export default function App() {
  return (
    <div className="min-h-screen flex flex-col bg-white">
      <Navbar />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/services" element={<div className="site-container py-8"><Services /></div>} />
          <Route path="/products" element={<div className="site-container py-8"><Products /></div>} />
          <Route path="/contact" element={<div className="site-container py-8"><Contact /></div>} />
          <Route path="/personalization" element={<div className="site-container py-8"><Personalization /></div>} />
          <Route path="/cart" element={<div className="site-container py-8"><Cart /></div>} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}
