'use client';

interface SummaryCardProps {
  title: string;
  value: number | string;
  icon: React.ReactNode;
  color: 'sage' | 'mint' | 'warm' | 'rose';
}

const bgColors = {
  sage: 'bg-sage-100',
  mint: 'bg-mint-100',
  warm: 'bg-warm-100',
  rose: 'bg-rose-100',
};

const iconColors = {
  sage: 'text-sage-600',
  mint: 'text-mint-500',
  warm: 'text-warm-500',
  rose: 'text-rose-400',
};

export function SummaryCard({ title, value, icon, color }: SummaryCardProps) {
  return (
    <div className="bg-white rounded-xl border border-sage-200 p-5 shadow-sm">
      <div className="flex items-start gap-4">
        <div className={`flex-shrink-0 w-10 h-10 rounded-lg ${bgColors[color]} ${iconColors[color]} flex items-center justify-center`}>
          {icon}
        </div>
        <div>
          <p className="text-sm font-medium text-sage-500">{title}</p>
          <p className="text-2xl font-bold text-sage-800 mt-1">{value}</p>
        </div>
      </div>
    </div>
  );
}
