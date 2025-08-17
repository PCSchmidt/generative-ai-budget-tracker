import React, { useMemo } from 'react';
import { Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js';
import { getCategoryMeta } from '../../utils/categories';

ChartJS.register(ArcElement, Tooltip, Legend);

export default function CategoryDonut({ summary }) {
  // summary expected shape: { total_amount, total_count, categories: [{ category, total_amount, count }] }
  const { data, hasData } = useMemo(() => {
    const cats = Array.isArray(summary?.categories) ? summary.categories : [];
    const labels = cats.map(c => c.category);
    const values = cats.map(c => Number(c.total_amount || 0));
    const colors = cats.map(c => getCategoryMeta(c.category).color);
    const bgColors = cats.map(c => getCategoryMeta(c.category).bg);
    return {
      data: {
        labels,
        datasets: [
          {
            label: 'Spending by Category',
            data: values,
            backgroundColor: colors,
            borderColor: bgColors,
            borderWidth: 2,
          },
        ],
      },
      hasData: values.some(v => v > 0),
    };
  }, [summary]);

  if (!hasData) {
    return (
      <div style={styles.empty}>No spending this period</div>
    );
  }

  return (
    <div style={styles.wrap}>
      <Doughnut data={data} options={options} />
    </div>
  );
}

const options = {
  responsive: true,
  plugins: {
    legend: {
      position: 'bottom',
      labels: { boxWidth: 12 },
    },
    tooltip: {
      callbacks: {
        label: (ctx) => {
          const label = ctx.label || '';
          const v = ctx.parsed || 0;
          return `${label}: $${Number(v).toFixed(2)}`;
        }
      }
    }
  },
  cutout: '60%'
};

const styles = {
  wrap: { width: '100%', maxWidth: 420, margin: '0 auto' },
  empty: {
    background: '#fff',
    border: '1px solid #e2e8f0',
    borderRadius: 12,
    padding: 16,
    color: '#94a3b8',
    textAlign: 'center'
  }
};
