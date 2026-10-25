import type { Metadata } from 'next';
import './globals.css';
import { AppProvider } from '@/components/AppProvider';

export const metadata: Metadata = {
  title: 'PlantSense AI — Research Prototype',
  description: 'Research prototype exploring machine-learning experiments on plant-related audio.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-sage-50 text-[#2d3a25] antialiased">
        <AppProvider>{children}</AppProvider>
      </body>
    </html>
  );
}
