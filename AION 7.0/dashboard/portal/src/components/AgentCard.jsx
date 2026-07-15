import { Link } from 'react-router-dom';

export default function AgentCard({ id, icon, title, description, tags = [] }) {
  return (
    <Link to={`/agent/${id}`} className="agent-card">
      <div className="agent-icon">{icon}</div>
      <h3>{title}</h3>
      <p>{description}</p>
      {tags.length > 0 && (
        <div className="agent-tags">
          {tags.map((t) => (
            <span key={t} className="tag">{t}</span>
          ))}
        </div>
      )}
    </Link>
  );
}
