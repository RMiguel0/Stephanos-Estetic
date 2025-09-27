import { Link, Routes, Route, NavLink, BrowserRouter} from 'react-router-dom'
import Home from './pages/Home.jsx'
import ServicesPage from './pages/Services.jsx'
import ContactPage from './pages/Contact.jsx'
import SalesPage from './pages/Sales.jsx'
import  Toaster  from 'react-hot-toast'
  
export default function App() {
  return (
    <main style={{ margin: '0 auto', maxWidth: 960, padding: 24 }}>
      <header style={{ display: 'flex', gap: 16, alignItems: 'center', marginBottom: 24 }}>
        <Link to="/" style={{ fontWeight: 700, fontSize: 18, textDecoration: 'none' }}>
          Stephanos Estetic
        </Link>
        <nav style={{ display: 'flex', gap: 12 }}>
          <NavLink to="/services">Servicios</NavLink>
          <NavLink to="/sales">Productos</NavLink>
          <NavLink to="/contact">Contacto</NavLink>
        </nav>
      </header>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/services" element={<ServicesPage />} />
        <Route path="/contact" element={<ContactPage />} />
        <Route path="/sales" element={<SalesPage />} />
        <Route path="*" element={<p>404 — No encontrado</p>} />
      </Routes>
      
    </main>
  )
}
