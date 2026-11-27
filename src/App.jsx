import { useCallback, useEffect, useRef, useState } from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import Projects, { ProjectDetailsModal } from './components/Projects';
import SecondaryProjects from './components/SecondaryProjects';
import Skills from './components/Skills';
import Credentials from './components/Credentials';
import Footer from './components/Footer';
import CommandPalette from './components/CommandPalette';
import LiveDemoModal from './components/LiveDemoModal';
import Toast from './components/Toast';
import BackToTop from './components/BackToTop';
import { profileData } from './data/portfolioData';

export default function App() {
  const [activeCategory, setActiveCategory] = useState('all');
  const [activeSkill, setActiveSkill] = useState(null);
  const [paletteOpen, setPaletteOpen] = useState(false);
  const [paletteDetailsProject, setPaletteDetailsProject] = useState(null);
  const [paletteDemoProject, setPaletteDemoProject] = useState(null);
  const [toastMessage, setToastMessage] = useState('');
  const toastTimerRef = useRef(null);

  const showToast = useCallback((msg) => {
    setToastMessage(msg);
    if (toastTimerRef.current) clearTimeout(toastTimerRef.current);
    toastTimerRef.current = setTimeout(() => setToastMessage(''), 2400);
  }, []);

  useEffect(() => {
    return () => {
      if (toastTimerRef.current) clearTimeout(toastTimerRef.current);
    };
  }, []);

  useEffect(() => {
    const onKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setPaletteOpen((prev) => !prev);
      }
    };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, []);

  const handleCategoryChange = useCallback((nextCategory) => {
    setActiveCategory(nextCategory);
    setActiveSkill(null);
  }, []);

  const handleSelectSkill = useCallback(
    (skill) => {
      setActiveCategory('all');
      setActiveSkill((prev) => {
        const next = prev === skill ? null : skill;
        if (next) {
          document.getElementById('projects')?.scrollIntoView?.({
            behavior: 'smooth',
            block: 'start',
          });
          showToast(`Filtered projects by "${next}"`);
        } else {
          showToast('Cleared skill filter');
        }
        return next;
      });
    },
    [showToast]
  );

  const handleCopyEmail = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(profileData.email);
      showToast(`Copied ${profileData.email} to clipboard`);
    } catch {
      window.location.href = `mailto:${profileData.email}`;
    }
  }, [showToast]);

  const handleSelectSection = useCallback((href) => {
    const id = href.replace('#', '');
    document.getElementById(id)?.scrollIntoView?.({
      behavior: 'smooth',
      block: 'start',
    });
  }, []);

  return (
    <div className="min-h-screen bg-[#09090B] text-zinc-100">
      <Navbar onOpenPalette={() => setPaletteOpen(true)} />
      <main>
        <Hero onNotify={showToast} />
        <Projects
          activeCategory={activeCategory}
          onCategoryChange={handleCategoryChange}
          activeSkill={activeSkill}
          onClearSkill={() => setActiveSkill(null)}
          onNotify={showToast}
        />
        <SecondaryProjects
          activeCategory={activeCategory}
          onResetFilter={() => {
            setActiveCategory('all');
            setActiveSkill(null);
          }}
          activeSkill={activeSkill}
          onClearSkill={() => setActiveSkill(null)}
          onNotify={showToast}
        />
        <Skills activeSkill={activeSkill} onSelectSkill={handleSelectSkill} />
        <Credentials />
      </main>
      <Footer onNotify={showToast} />

      <CommandPalette
        open={paletteOpen}
        onClose={() => setPaletteOpen(false)}
        onOpenProjectDetails={(project) => setPaletteDetailsProject(project)}
        onOpenLiveDemo={(project) => setPaletteDemoProject(project)}
        onCopyEmail={handleCopyEmail}
        onSelectSection={handleSelectSection}
      />

      <ProjectDetailsModal
        project={paletteDetailsProject}
        onClose={() => setPaletteDetailsProject(null)}
        onLaunchDemo={(project) => {
          setPaletteDetailsProject(null);
          setPaletteDemoProject({ ...project, id: project.demoId });
        }}
        onNotify={showToast}
      />

      <LiveDemoModal
        project={paletteDemoProject}
        onClose={() => setPaletteDemoProject(null)}
      />

      <Toast message={toastMessage} onDismiss={() => setToastMessage('')} />
      <BackToTop />
    </div>
  );
}
