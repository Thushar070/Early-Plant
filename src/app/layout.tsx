import type { Metadata } from 'next';
import './globals.css';
import { AppProvider } from '@/components/AppProvider';

export const metadata: Metadata = {
  title: 'PlantSense AI — Early Plant Stress Detection',
  description: 'Detect plant stress before visible symptoms appear using ultrasonic signals and AI.',
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
