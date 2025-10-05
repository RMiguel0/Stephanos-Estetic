import { Heart, ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

export default function Home() {
  return (
    <section className="gradient-bg text-center py-24">
      <div className="max-w-2xl mx-auto px-4">
        <div className="inline-flex items-center gap-2 text-[var(--color-brand-600)] font-medium mb-6">
          <Heart className="h-5 w-5 fill-[var(--color-brand-500)] text-[var(--color-brand-500)]" />
          Beauty • Wellness • Transformation
        </div>

        <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight text-gray-900">
          Welcome to <span className="text-[var(--color-brand-600)]">Stephanos Estetic</span>
        </h1>

        <p className="mt-4 text-gray-600 text-lg">
          Your sanctuary for beauty, wellness, and personal transformation.  
          Discover a world where self-care meets excellence.
        </p>

        <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
          <Link to="/contact" className="btn-primary">
            Book a Session
            <ArrowRight className="h-4 w-4" />
          </Link>
          <Link to="/products" className="btn-ghost">
            Explore Products
          </Link>
        </div>
      </div>
    </section>
  );
}
