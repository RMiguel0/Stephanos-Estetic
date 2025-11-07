import { Heart, Sparkles, Users, Award, CrownIcon } from "lucide-react";
import { useNavigate, Link } from "react-router-dom";
import logo from "../assets/logo_SE.svg";

export default function Home() {
  const navigate = useNavigate();
  const features = [
    {
      icon: Heart,
      title: "¿Quiénes Somos?",
      description:
        "Somos personas que, al igual que muchos, hemos enfrentado enfermedades que transforman cuerpo y espíritu. En Dios Todopoderoso encontramos la fortaleza, la paz y la esperanza para seguir adelante, cuidando la vida como un regalo sagrado.",
    },
    {
      icon: Sparkles,
      title: "Nuestra Misión",
      description:
        "Servir con amor y excelencia a través de la estética integral y oncológica. Queremos que cada persona descubra en su reflejo no solo belleza exterior, sino también la victoria interior que proviene de la fe y la esperanza.",
    },
    {
      icon: Users,
      title: "¿Por Qué Elegirnos?",
      description:
        "Porque unimos ciencia, empatía y fe. Nuestros tratamientos son seguros, personalizados y humanizados, diseñados para acompañarte en cuerpo, mente y espíritu, recordándote que eres obra perfecta de Dios.",
    },
    {
      icon: CrownIcon,
      title: "El Significado de Stephanos",
      description:
        "‘Stephanos’ en griego significa corona de victoria. Representa las recompensas espirituales que Dios promete a quienes perseveran con fe, amor y buen testimonio. Cada servicio busca reflejar esa victoria en tu piel, tu ánimo y tu corazón.",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-pink-50">
      {/* HERO */}
      <section className="relative overflow-hidden">
        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-32">
          <div className="text-center">
            <div className="inline-flex items-center justify-center">
              <img
                src={logo}
                alt="Stephanos Estetic logo"
                className="block mx-auto h-auto w-full max-w-[40rem] md:max-w-[48rem]"
              />
            </div>
            <h1 className="text-5xl lg:text-7xl font-bold text-gray-900 mb-6 leading-tight">
              Bienvenido a{" "}
              <span className="bg-gradient-to-r from-pink-500 to-pink-600 bg-clip-text text-transparent">
                Stephanos Estetic
              </span>
            </h1>
            <p className="text-xl lg:text-2xl text-gray-600 mb-10 max-w-3xl mx-auto leading-relaxed">
              Belleza y victoria en uno.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={() => navigate("/services")}
                className="px-8 py-4 bg-gradient-to-r from-pink-500 to-pink-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-200"
              >
                Reserva una sesión
              </button>

              <button
                onClick={() => navigate("/products")}
                className="px-8 py-4 bg-gradient-to-r from-pink-500 to-pink-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-200"
              >
                Explora productos
              </button>
            </div>
          </div>
        </div>

        {/* background blobs */}
        <div className="pointer-events-none absolute -z-10 top-20 left-10 w-72 h-72 bg-pink-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"></div>
        <div className="pointer-events-none absolute -z-10 top-40 right-10 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-2000"></div>
        <div className="pointer-events-none absolute -z-10 bottom-20 left-1/2 w-72 h-72 bg-pink-100 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-4000"></div>
      </section>

      {/* FEATURES */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
            Sobre{" "}
            <span className="bg-gradient-to-r from-pink-500 to-pink-600 bg-clip-text text-transparent"> 
              Nosotros
            </span>
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Combinamos experiencia, pasión y dedicación para ofrecer
            vivencias excepcionales.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-white p-8 rounded-2xl shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1 border border-gray-100"
            >
              <div className="inline-flex items-center justify-center w-14 h-14 bg-gradient-to-br from-pink-100 to-pink-200 rounded-xl mb-6">
                <feature.icon className="h-7 w-7 text-pink-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                {feature.title}
              </h3>
              <p className="text-gray-600 leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* CALL TO ACTION */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="bg-gradient-to-r from-pink-500 to-pink-600 rounded-3xl p-12 lg:p-16 text-center shadow-2xl">
          <h2 className="text-4xl lg:text-5xl font-bold text-white mb-6">
            ¿Quieres ayudarnos con esta tarea?
          </h2>
          <p className="text-xl text-pink-100 mb-10 max-w-2xl mx-auto">
            Si nuestra visión y misión resuenan contigo, te invitamos a ser
            parte de nuestra comunidad. Ya sea como cliente, colaborador o
            socio, juntos podemos lograr una transformación significativa.
            ¡Contáctanos hoy!
          </p>
          <button
            onClick={() => navigate("/contact")}
            className="px-10 py-4 bg-white text-pink-600 rounded-xl font-semibold shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-200"
          >
            Ponte en contacto
          </button>
        </div>
      </section>
    </div>
  );
}
