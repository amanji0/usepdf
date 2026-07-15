import { Link } from 'react-router-dom';
import { Tool } from '../../types';
import styles from './ToolCard.module.css';

interface ToolCardProps {
  tool: Tool;
  index: number;
}

const ToolCard = ({ tool, index }: ToolCardProps) => {
  return (
    <Link
      to={`/tools/${tool.id}`}
      className={styles.card}
      data-category={tool.category}
      style={{ animationDelay: `${index * 0.06}s` }}
    >
      <div className={styles.glow} />
      <div className={styles.content}>
        <div className={styles.iconWrap}>
          <span className={styles.icon}><tool.icon size={28} strokeWidth={1.5} /></span>
        </div>
        <h3 className={styles.title}>{tool.name}</h3>
        <p className={styles.description}>{tool.description}</p>
      </div>
      <div className={styles.arrow}>→</div>
    </Link>
  );
};

export default ToolCard;
