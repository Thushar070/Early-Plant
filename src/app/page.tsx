'use client';

import { useApp } from '@/components/AppProvider';
import { useRouter } from 'next/navigation';
import {
  Sprout,
  Leaf,
  Radio,
  Brain,
  ScanSearch,
  BellRing,
  TreePine,
  Droplets,
  Sun,
  Wind,
  ArrowRight,
  Activity,
} from 'lucide-react';

export default function LandingPage() {
  const { login } = useApp();
  const router = useRouter();

  const handleAuth = () => {
    login();
    router.push('/dashboard');
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-cream-50 via-sage-50/50 to-sage-100/40 flex flex-col justify-center items-center py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Decorative background icons */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden opacity-25 hidden lg:block">
        <Leaf className="absolute top-[10%] left-[12%] text-sage-400 w-16 h-16 -rotate-12" />
        <TreePine className="absolute top-[18%] right-[10%] text-mint-400 w-20 h-20 rotate-6" />
        <Droplets className="absolute bottom-[28%] left-[16%] text-sage-400 w-12 h-12 rotate-12" />
        <Sun className="absolute top-[14%] right-[22%] text-warm-400 w-16 h-16" />
        <Wind className="absolute bottom-[22%] right-[12%] text-sage-400 w-16 h-16 -rotate-6" />
        <Sprout className="absolute bottom-[12%] left-[6%] text-mint-400 w-18 h-18 rotate-12" />
      </div>

      <div className="w-full max-w-5xl mx-auto flex flex-col items-center z-10 flex-grow">
        {/* Brand & Acoustic Concept Badge */}
        <div className="text-center flex flex-col items-center mb-12 pt-6 md:pt-10">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-sage-100/90 border border-sage-200 text-xs font-medium text-sage-700 mb-6 shadow-xs">
            <Activity className="w-3.5 h-3.5 text-sage-600 animate-pulse" />
            <span>Research prototype · sample audio experiments</span>
          </div>

          <div className="flex items-center justify-center space-x-3.5 mb-4">
            <div className="bg-sage-200/80 p-3.5 rounded-2xl shadow-xs border border-sage-300/40">
              <Sprout className="w-9 h-9 text-sage-700" />
            </div>
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold text-sage-900 tracking-tight">
              PlantSense AI
            </h1>
          </div>

          <h2 className="text-lg md:text-2xl font-semibold text-sage-700 max-w-2xl mb-4">
            Exploring Plant-Stress Classification from Audio
          </h2>

          <div className="bg-white/80 border border-sage-200/80 px-6 py-3 rounded-xl shadow-xs mb-8">
            <p className="text-base md:text-lg font-medium text-sage-800 italic">
              &ldquo;A research prototype for exploring plant-related acoustic signals.&rdquo;
            </p>
          </div>

          {/* Acoustic Wave Graphic */}
          <div className="flex items-center gap-1.5 py-2 px-4 rounded-full bg-white/60 border border-sage-200 text-xs text-sage-600 mb-8">
            <span className="w-1.5 h-3 bg-sage-400 rounded-full animate-pulse" />
            <span className="w-1.5 h-5 bg-sage-500 rounded-full animate-pulse [animation-delay:150ms]" />
            <span className="w-1.5 h-7 bg-sage-600 rounded-full animate-pulse [animation-delay:300ms]" />
            <span className="w-1.5 h-4 bg-mint-500 rounded-full animate-pulse [animation-delay:450ms]" />
            <span className="w-1.5 h-2 bg-sage-400 rounded-full animate-pulse [animation-delay:600ms]" />
            <span className="ml-2 font-mono text-[11px] tracking-wider text-sage-500">Illustrative audio concept · no sensor connected</span>
          </div>

          {/* CTA Section */}
          <div className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-4">
            <button
              onClick={handleAuth}
              className="bg-sage-600 hover:bg-sage-700 text-white rounded-xl px-8 py-3.5 font-semibold transition-all flex items-center justify-center shadow-sm hover:shadow"
            >
              Get Started <ArrowRight className="ml-2 w-4 h-4" />
            </button>
            <button
              onClick={handleAuth}
              className="border border-sage-300 text-sage-700 hover:bg-sage-100/70 bg-white/70 rounded-xl px-8 py-3.5 font-semibold transition-all flex items-center justify-center shadow-xs"
            >
              Sign In
            </button>
          </div>
        </div>

        {/* How It Works Section */}
        <div className="w-full mb-12">
          <div className="text-center mb-8">
            <h3 className="text-2xl font-bold text-sage-800">How PlantSense AI Works</h3>
            <p className="text-sm text-sage-500 mt-1">Translating plant acoustics into actionable farm guidance</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {/* Step 1 */}
            <div className="flex flex-col items-center text-center p-5 bg-white/80 rounded-xl shadow-xs border border-sage-200/80 hover:border-sage-300 transition-all">
              <div className="bg-mint-100 w-12 h-12 rounded-xl flex items-center justify-center mb-3 text-mint-600">
                <Sprout className="w-6 h-6" />
              </div>
              <div className="text-[11px] font-bold text-sage-500 uppercase tracking-wider mb-1">Step 1</div>
              <h4 className="font-semibold text-sage-800 text-sm mb-1.5">Plant-related audio is recorded</h4>
              <p className="text-xs text-sage-600 leading-relaxed">
                The project explores whether recorded acoustic signals may contain patterns associated with plant stress.
              </p>
            </div>

            {/* Step 2 */}
            <div className="flex flex-col items-center text-center p-5 bg-white/80 rounded-xl shadow-xs border border-sage-200/80 hover:border-sage-300 transition-all">
              <div className="bg-sage-100 w-12 h-12 rounded-xl flex items-center justify-center mb-3 text-sage-600">
                <Radio className="w-6 h-6" />
              </div>
              <div className="text-[11px] font-bold text-sage-500 uppercase tracking-wider mb-1">Step 2</div>
              <h4 className="font-semibold text-sage-800 text-sm mb-1.5">Sample audio is represented</h4>
              <p className="text-xs text-sage-600 leading-relaxed">
                The current prototype uses a local sample dataset. No sensor or live recording is connected.
              </p>
            </div>

            {/* Step 3 */}
            <div className="flex flex-col items-center text-center p-5 bg-white/80 rounded-xl shadow-xs border border-sage-200/80 hover:border-sage-300 transition-all">
              <div className="bg-cream-200 w-12 h-12 rounded-xl flex items-center justify-center mb-3 text-amber-700">
                <Brain className="w-6 h-6" />
              </div>
              <div className="text-[11px] font-bold text-sage-500 uppercase tracking-wider mb-1">Step 3</div>
              <h4 className="font-semibold text-sage-800 text-sm mb-1.5">ML experiments analyze audio</h4>
              <p className="text-xs text-sage-600 leading-relaxed">
                ML experiments transform audio into features such as log-Mel spectrograms.
              </p>
            </div>

            {/* Step 4 */}
            <div className="flex flex-col items-center text-center p-5 bg-white/80 rounded-xl shadow-xs border border-sage-200/80 hover:border-sage-300 transition-all">
              <div className="bg-warm-100 w-12 h-12 rounded-xl flex items-center justify-center mb-3 text-warm-600">
                <ScanSearch className="w-6 h-6" />
              </div>
              <div className="text-[11px] font-bold text-sage-500 uppercase tracking-wider mb-1">Step 4</div>
              <h4 className="font-semibold text-sage-800 text-sm mb-1.5">Stress pattern is classified</h4>
              <p className="text-xs text-sage-600 leading-relaxed">
                Research experiments compare five target classes; current validation performance is low.
              </p>
            </div>

            {/* Step 5 */}
            <div className="flex flex-col items-center text-center p-5 bg-white/80 rounded-xl shadow-xs border border-sage-200/80 hover:border-sage-300 transition-all">
              <div className="bg-terracotta-100 w-12 h-12 rounded-xl flex items-center justify-center mb-3 text-terracotta-600">
                <BellRing className="w-6 h-6" />
              </div>
              <div className="text-[11px] font-bold text-sage-500 uppercase tracking-wider mb-1">Step 5</div>
              <h4 className="font-semibold text-sage-800 text-sm mb-1.5">Prototype displays sample alerts</h4>
              <p className="text-xs text-sage-600 leading-relaxed">
                The dashboard shows illustrative sample alerts and recommendations, not verified predictions.
              </p>
            </div>
          </div>
        </div>

        {/* Footer Area */}
        <footer className="mt-auto pt-6 pb-4 border-t border-sage-200 w-full text-center">
          <p className="text-xs text-sage-500 font-medium">
            © 2026 PlantSense AI — Research prototype with illustrative sample data
          </p>
        </footer>
      </div>
    </div>
  );
}
