import React, { useEffect, useState } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

const CUBE_API_URL = import.meta.env.VITE_CUBE_API_URL || 'http://localhost:4000/cubejs-api/v1';
const CUBE_TOKEN = import.meta.env.VITE_CUBE_TOKEN || '';

async function cubeLoad(query) {
  const response = await fetch(`${CUBE_API_URL}/load`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(CUBE_TOKEN ? { Authorization: CUBE_TOKEN } : {}),
    },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    throw new Error(`Cube API failed: ${response.status}`);
  }

  const payload = await response.json();
  return payload.data || [];
}

function normalizeRows(rows, dimension) {
  return rows.map((row) => ({
    name: row[dimension],
    students: Number(row['ArtworkEngagement.studentCount'] || 0),
    artworks: Number(row['ArtworkEngagement.artworkCount'] || 0),
    views: Number(row['ArtworkEngagement.views'] || 0),
    likes: Number(row['ArtworkEngagement.likes'] || 0),
    avgGrade: Number(row['ArtworkEngagement.avgGrade'] || 0).toFixed(1),
  }));
}

export default function App() {
  const [selectedExhibition, setSelectedExhibition] = useState(null);
  const [rows, setRows] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    const dimension = selectedExhibition ? 'ArtworkEngagement.ageGroup' : 'ArtworkEngagement.exhibitionId';
    const query = {
      measures: [
        'ArtworkEngagement.studentCount',
        'ArtworkEngagement.artworkCount',
        'ArtworkEngagement.views',
        'ArtworkEngagement.likes',
        'ArtworkEngagement.avgGrade',
      ],
      dimensions: [dimension],
      filters: selectedExhibition
        ? [{ member: 'ArtworkEngagement.exhibitionId', operator: 'equals', values: [selectedExhibition] }]
        : [],
      order: { 'ArtworkEngagement.views': 'desc' },
    };

    cubeLoad(query)
      .then((data) => {
        setRows(normalizeRows(data, dimension));
        setError('');
      })
      .catch((loadError) => setError(loadError.message));
  }, [selectedExhibition]);

  return (
    <main className="shell">
      <section className="hero">
        <div>
          <p className="eyebrow">Embedded analytics</p>
          <h1>Онлайн-галерея юных художников</h1>
          <p className="lead">
            Semantic layer отделяет бизнес-метрики от таблиц ClickHouse. Drill-down показывает путь
            от выставки к возрастной группе авторов.
          </p>
        </div>
        <button className="ghost" onClick={() => setSelectedExhibition(null)}>
          Все выставки
        </button>
      </section>

      {selectedExhibition && (
        <div className="drilldown">Drill-down: выставка <strong>{selectedExhibition}</strong> → возрастные группы</div>
      )}

      {error && <div className="error">{error}</div>}

      <section className="card">
        <ResponsiveContainer width="100%" height={360}>
          <BarChart data={rows} onClick={(event) => event?.activeLabel && setSelectedExhibition(event.activeLabel)}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="views" fill="#0f766e" name="Просмотры" />
            <Bar dataKey="likes" fill="#f97316" name="Лайки" />
          </BarChart>
        </ResponsiveContainer>
      </section>

      <section className="grid">
        {rows.map((row) => (
          <article className="metric" key={row.name} onClick={() => !selectedExhibition && setSelectedExhibition(row.name)}>
            <span>{row.name}</span>
            <strong>{row.views.toLocaleString('ru-RU')}</strong>
            <small>
              {row.students} художников, {row.artworks} работ, средний балл {row.avgGrade}
            </small>
          </article>
        ))}
      </section>
    </main>
  );
}
