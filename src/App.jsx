import { useState } from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import Projects from './components/Projects';
import SecondaryProjects from './components/SecondaryProjects';
import Skills from './components/Skills';
import Credentials from './components/Credentials';
import Footer from './components/Footer';

export default function App() {
  const [activeCategory, setActiveCategory] = useState('all');

  return (
    <div className="min-h-screen bg-[#09090B] text-zinc-100">
      <Navbar />
      <main>
        <Hero />
        <Projects activeCategory={activeCategory} onCategoryChange={setActiveCategory} />
        <SecondaryProjects activeCategory={activeCategory} onResetFilter={() => setActiveCategory('all')} />
        <Skills />
        <Credentials />
      </main>
      <Footer />
    </div>
  );
}
