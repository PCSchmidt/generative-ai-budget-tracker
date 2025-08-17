import React, { useMemo } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

// props: expenses (array), month (YYYY-MM optional)
export default function MonthlyTrend({ expenses = [], month }) {
  const { data, hasData } = useMemo(() => {
    // Bucket by day for the selected month (or month of first expense)
    const map = new Map();
    const dateKey = (d) => `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;

    const monthPrefix = month || (() => {
      const first = expenses[0]?.expense_date || expenses[0]?.created_at;
      if (!first) return null;
      const d = new Date(first);
      if (isNaN(d)) return null;
      return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}`;
    })();

    expenses.forEach(e => {
      const raw = e.expense_date || e.created_at;
      if (!raw) return;
      const d = new Date(raw);
      if (isNaN(d)) return;
      const ym = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}`;
      if (monthPrefix && ym !== monthPrefix) return;
      const key = dateKey(d);
      map.set(key, (map.get(key) || 0) + Number(e.amount || 0));
    });

    // Generate label list for the days present
    const labels = Array.from(map.keys()).sort();
    const values = labels.map(k => map.get(k));

    return {
      data: {
        labels,
        datasets: [
          {
            label: 'Daily Spend',
            data: values,
            borderColor: '#2563eb',
            backgroundColor: 'rgba(37, 99, 235, 0.2)',
            tension: 0.3,
            pointRadius: 2,
          }
        ]
      },
      hasData: values.length > 0
    };
  }, [expenses, month]);

  if (!hasData) {
    return <div style={styles.empty}>No daily spend data</div>;
  }

  return (
    <div style={styles.wrap}>
      <Line data={data} options={options} />
    </div>
  );
}

const options = {
  responsive: true,
  plugins: {
    legend: { position: 'bottom' },
    tooltip: {
      callbacks: {
        label: (ctx) => `$${Number(ctx.parsed.y || 0).toFixed(2)}`
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        callback: (v) => `$${Number(v).toFixed(0)}`
      }
    }
  }
};

const styles = {
  wrap: { width: '100%', maxWidth: 640, margin: '0 auto' },
  empty: {
    background: '#fff',
    border: '1px solid #e2e8f0',
    borderRadius: 12,
    padding: 16,
    color: '#94a3b8',
    textAlign: 'center'
  }
};
