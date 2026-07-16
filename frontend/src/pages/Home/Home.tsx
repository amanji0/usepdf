import { useState } from 'react';
import { TOOLS } from '../../data/tools';
import { ToolCategory } from '../../types';
import ToolCard from '../../components/ToolCard/ToolCard';
import { LayoutGrid, Layers, Zap, RefreshCw, Shield, Edit3, Sparkles } from 'lucide-react';
import styles from './Home.module.css';

const CATEGORIES: { id: ToolCategory | 'all'; label: string; icon: any }[] = [
  { id: 'all', label: 'All Tools', icon: LayoutGrid },
  { id: 'organize', label: 'Organize', icon: Layers },
  { id: 'optimize', label: 'Optimize', icon: Zap },
  { id: 'convert', label: 'Convert', icon: RefreshCw },
  { id: 'edit', label: 'Edit', icon: Edit3 },
  { id: 'security', label: 'Security', icon: Shield },
  { id: 'intelligence', label: 'Intelligence', icon: Sparkles },
];

const Home = () => {
  const [activeCategory, setActiveCategory] = useState<ToolCategory | 'all'>('all');

  const filteredTools = TOOLS.filter(
    tool => activeCategory === 'all' || tool.category === activeCategory
  );

  return (
    <div className={styles.home}>
      {/* Hero */}
      <section className={styles.hero}>
        <div className={styles.heroGlow} />
        <p className={styles.eyebrow}>Self-hosted PDF toolkit</p>
        <h1 className={styles.title}>
          Every tool you need <br />
          <span className="text-gradient">to work with PDFs</span>
        </h1>
        <p className={styles.subtitle}>
          Merge, split, compress, convert, protect — all free, all private,
          all running on <em>your</em> server.
        </p>
      </section>

      {/* Filter + Grid */}
      <section className={styles.toolsSection}>
        <div className={styles.filterBar}>
          {CATEGORIES.map(cat => (
            <button
              key={cat.id}
              className={`${styles.filterBtn} ${activeCategory === cat.id ? styles.active : ''}`}
              onClick={() => setActiveCategory(cat.id)}
              data-category={cat.id !== 'all' ? cat.id : undefined}
            >
              <span className={styles.filterIcon}><cat.icon size={16} strokeWidth={2} /></span>
              {cat.label}
            </button>
          ))}
        </div>

        <div className={styles.grid}>
          {filteredTools.map((tool, index) => (
            <ToolCard key={tool.id} tool={tool} index={index} />
          ))}
        </div>
      </section>
    </div>
  );
};

export default Home;
