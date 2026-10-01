import React, { StrictMode, Component, ErrorInfo, ReactNode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  public props: ErrorBoundaryProps;
  public state: ErrorBoundaryState = { hasError: false, error: null };

  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.props = props;
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('[LaborTwin App Error]', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="w-screen h-screen bg-[#05070c] text-white flex flex-col items-center justify-center p-6 text-center space-y-4 font-mono">
          <div className="w-16 h-16 rounded-2xl bg-rose-500/20 border border-rose-500 flex items-center justify-center text-rose-400 text-2xl font-bold">
            !
          </div>
          <h1 className="text-xl font-bold text-slate-100 font-display">
            Error de Inicialización en Interfaz
          </h1>
          <p className="text-xs text-slate-400 max-w-md">
            {this.state.error?.message || 'Se produjo una interrupción inesperada al renderizar los componentes.'}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="px-5 py-2.5 rounded-xl bg-cyan-400 text-slate-950 text-xs font-bold font-mono hover:bg-cyan-300 transition-all cursor-pointer shadow-lg shadow-cyan-500/20"
          >
            Recargar Aplicación (F5)
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>,
);
