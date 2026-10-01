import React, { useState, useRef, useEffect } from 'react';
import { 
  Bot, 
  X, 
  Send, 
  Sparkles, 
  Trash2, 
  ChevronDown, 
  ArrowRight,
  TrendingDown,
  ShieldCheck,
  Zap,
  MessageSquare
} from 'lucide-react';
import { 
  CountryCode, 
  StructuralMetrics, 
  PolicyParameters, 
  ScenarioPreset,
  Language,
  AppTheme
} from '../../types';
import { COUNTRY_PROFILES } from '../../data/mockData';
import { t, tList } from '../../utils/i18n';
import { playHoloClick } from '../../utils/audioSynth';
import { 
  sendCopilotMessageApi, 
  fetchCopilotHistoryApi, 
  clearCopilotHistoryApi, 
  CopilotHistoryItem 
} from '../../services/api';

interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
  source?: string;
  flowId?: string;
  action?: {
    label: string;
    scenario?: ScenarioPreset;
  };
}

interface AIChatbotModalProps {
  country: CountryCode;
  month: number;
  metrics: StructuralMetrics;
  policyParams: PolicyParameters;
  scenario: ScenarioPreset;
  onSelectScenario: (s: ScenarioPreset) => void;
  language: Language;
  theme: AppTheme;
  isOpen?: boolean;
  onClose?: () => void;
  onOpen?: () => void;
}

export const AIChatbotModal: React.FC<AIChatbotModalProps> = ({
  country,
  month,
  metrics,
  policyParams,
  scenario,
  onSelectScenario,
  language,
  theme,
  isOpen: controlledIsOpen,
  onClose,
  onOpen,
}) => {
  const [internalIsOpen, setInternalIsOpen] = useState(false);
  const isOpen = controlledIsOpen !== undefined ? controlledIsOpen : internalIsOpen;

  const handleOpen = () => {
    if (onOpen) onOpen();
    setInternalIsOpen(true);
  };

  const handleClose = () => {
    if (onClose) onClose();
    setInternalIsOpen(false);
  };

  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const countryData = COUNTRY_PROFILES[country];

  const getInitialWelcomeMessage = (): ChatMessage => {
    const isEn = language === 'en';
    return {
      id: 'welcome-msg',
      sender: 'assistant',
      text: isEn
        ? `Hello! I am your AI Labor Economics Advisor. Currently analyzing **${countryData.name}** at Month ${month} (Informality rate: **${metrics.informalityRate.toFixed(1)}%**, Decent Work: **${metrics.decentWorkIndex}/100**). How can I assist your policy formulation today?`
        : `¡Hola! Soy tu Asistente de Economía Laboral con IA. Actualmente analizando **${countryData.name}** en el Mes ${month} (Tasa de informalidad: **${metrics.informalityRate.toFixed(1)}%**, Empleo Decente: **${metrics.decentWorkIndex}/100**). ¿En qué intervención de política puedo orientarte?`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
  };

  const [messages, setMessages] = useState<ChatMessage[]>([getInitialWelcomeMessage()]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }, [isOpen, messages, isTyping]);

  // Update initial message when language or country changes if chat has only 1 message
  useEffect(() => {
    if (messages.length === 1 && messages[0].sender === 'assistant') {
      setMessages([getInitialWelcomeMessage()]);
    }
  }, [language, country]);

  // Sincronización bidireccional con PostgreSQL (recupera historial persistido)
  useEffect(() => {
    if (!isOpen) return;

    let isMounted = true;
    const loadPostgresHistory = async () => {
      try {
        const hist = await fetchCopilotHistoryApi(`react-session-${country}`, 30);
        if (isMounted && hist && hist.length > 0) {
          const loaded: ChatMessage[] = [];
          hist.forEach((item) => {
            loaded.push({
              id: `user-${item.id}`,
              sender: 'user',
              text: item.user_message,
              timestamp: item.created_at ? new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '',
            });
            loaded.push({
              id: `ai-${item.id}`,
              sender: 'assistant',
              text: item.assistant_response,
              source: item.source,
              flowId: item.flow_id,
              timestamp: item.created_at ? new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '',
            });
          });
          setMessages(loaded);
        }
      } catch (err) {
        console.debug('Historial de PostgreSQL aún no inicializado o sin registros previos:', err);
      }
    };

    loadPostgresHistory();
    return () => {
      isMounted = false;
    };
  }, [isOpen, country]);

  // Dynamic intelligent response generator
  const generateAIResponse = (userQuery: string): { text: string; action?: { label: string; scenario?: ScenarioPreset } } => {
    const q = userQuery.toLowerCase();
    const isEn = language === 'en';
    const cName = countryData.name;
    const curInf = metrics.informalityRate.toFixed(1);

    if (q.includes('costo') || q.includes('cost') || q.includes('registr') || q.includes('ventanilla')) {
      return {
        text: isEn
          ? `Based on empirical calibration for **${cName}**, administrative barriers represent 38% of initial formalization friction. Slashing registration costs by **80%** typically accelerates firm transition by **14-16%** over a 24-month horizon while generating positive net fiscal returns by Year 3.`
          : `Según la calibración empírica para **${cName}**, las trabas administrativas explican el 38% de la fricción inicial. Reducir los costos de registro un **80%** acelera la transición de microempresas en un **14-16%** en un horizonte de 24 meses, logrando superávit fiscal neto a partir del tercer año.`,
        action: {
          label: isEn ? 'Apply Single-Window Reform' : 'Aplicar Reforma Ventanilla Única',
          scenario: 'SCENARIO_A_REGISTRATION',
        },
      };
    }

    if (q.includes('subsid') || q.includes('mipyme') || q.includes('sme') || q.includes('empleo') || q.includes('salari')) {
      return {
        text: isEn
          ? `Direct payroll co-financing (e.g. $80-$120 USD/mo per formalized worker) produces an immediate reduction in precarious employment. In **${cName}**, our model projects formal job creation increasing by **+22%**, though sustained fiscal sustainability requires pairing with productivity upskilling.`
          : `El cofinanciamiento directo de planillas ($80-$120 USD/mes por trabajador formalizado) genera un descenso inmediato del empleo precario. En **${cName}**, el modelo proyecta un incremento del **+22%** en puestos formales, aunque su sostenibilidad fiscal exige complementarse con programas de capacitación técnica.`,
        action: {
          label: isEn ? 'Apply Progressive Subsidy' : 'Aplicar Subsidio al Empleo',
          scenario: 'SCENARIO_B_WORKER_SUBSIDY',
        },
      };
    }

    if (q.includes('auto') || q.includes('ia') || q.includes('ai') || q.includes('tecnol') || q.includes('shock') || q.includes('choque')) {
      return {
        text: isEn
          ? `⚠️ **Automation Shock Assessment**: Displacing routine manual and clerical tasks without social safety nets pushes displaced formal workers back into vulnerable informal gig or street retail work. Informality in **${cName}** could surge by **+8.5 to +11.2 percentage points**.`
          : `⚠️ **Evaluación de Choque Tecnológico**: Desplazar puestos rutinarios sin un colchón de protección social devuelve a trabajadores formales vulnerables al comercio informal o subsistencia. La informalidad en **${cName}** podría repuntar entre **+8.5 y +11.2 puntos porcentuales**.`,
        action: {
          label: isEn ? 'Simulate Automation Shock' : 'Simular Choque de Automatización',
          scenario: 'SCENARIO_E_AUTOMATION_SHOCK',
        },
      };
    }

    if (q.includes('oit') || q.includes('ilo') || q.includes('decente') || q.includes('decent')) {
      return {
        text: isEn
          ? `The **ILO Decent Work Index** (currently **${metrics.decentWorkIndex}/100**) combines 4 key pillars: (1) Social security contribution compliance, (2) Wage ratio relative to the national minimum living basket, (3) Safe occupational conditions, and (4) Contractual predictability. Would you like to inspect the ILO Matrix modal?`
          : `El **Índice de Empleo Decente OIT** (actualmente **${metrics.decentWorkIndex}/100**) pondera 4 pilares: (1) Afiliación efectiva a salud y pensiones, (2) Relación salarial frente a la canasta de vida digna, (3) Condiciones y seguridad en el trabajo, y (4) Previsibilidad contractual.`,
      };
    }

    if (q.includes('gini') || q.includes('desigualdad') || q.includes('inequality')) {
      return {
        text: isEn
          ? `Current **Gini coefficient** in **${cName}** is **${metrics.giniIndex.toFixed(3)}**. Because the wage gap between formal ($${metrics.avgFormalWageUSD.toFixed(1)}/day) and informal ($${metrics.avgInformalWageUSD.toFixed(1)}/day) is over 3x, transitioning workers into formal enterprises directly closes the inequality gap by up to 0.05 points.`
          : `El coeficiente de **Gini** actual en **${cName}** se ubica en **${metrics.giniIndex.toFixed(3)}**. Dado que la brecha salarial formal ($${metrics.avgFormalWageUSD.toFixed(1)}/día) versus informal ($${metrics.avgInformalWageUSD.toFixed(1)}/día) supera una proporción de 3 a 1, la formalización estructurada es la vía más rápida para reducir la desigualdad en hasta 0.05 puntos.`,
      };
    }

    // Default dynamic context-aware answer
    return {
      text: isEn
        ? `In **${cName}**, with informality at **${curInf}%** at Month ${month}:
- **Priority 1**: Combine digital single-window registration (-50% cost) with skills training to lower formalization friction.
- **Priority 2**: Target micro-enterprises with temporary social security tax grace periods to prevent relapse into the informal sector.
Would you like to test one of the macro preset scenarios?`
        : `En **${cName}**, con una tasa de informalidad actual de **${curInf}%** en el Mes ${month}:
- **Prioridad 1**: Reducir barreras de entrada mediante ventanilla digital y subsidios directos a costos notariales.
- **Prioridad 2**: Fomentar la capacitación vocacional en microempresas para elevar su productividad antes de exigir aportes contributivos plenos.
¿Deseas activar alguno de los escenarios de reforma estructural?`,
      action: {
        label: isEn ? 'Simulate Single-Window Reform' : 'Simular Reforma Ventanilla Única',
        scenario: 'SCENARIO_A_REGISTRATION',
      },
    };
  };

  const handleSendMessage = async (textToSend?: string) => {
    const message = textToSend || inputMessage;
    if (!message.trim() || isTyping) return;

    playHoloClick(950);
    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: message.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputMessage('');
    setIsTyping(true);

    try {
      const result = await sendCopilotMessageApi({
        message: message.trim(),
        country,
        scenario,
        month,
        policy_params: policyParams,
        session_id: `react-session-${country}`,
      });

      playHoloClick(1150);
      const assistantMsg: ChatMessage = {
        id: `ai-${Date.now()}`,
        sender: 'assistant',
        text: result.response,
        source: result.source,
        flowId: result.flow_id,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      console.warn('[Copilot Error]', err);
      const assistantMsg: ChatMessage = {
        id: `ai-err-${Date.now()}`,
        sender: 'assistant',
        text: `⚠️ **Aviso:** ${err.message || 'No se pudo conectar con el servicio del Copiloto en FastAPI / Langflow.'}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleClearChat = async () => {
    playHoloClick(600);
    try {
      await clearCopilotHistoryApi(`react-session-${country}`);
    } catch (err) {
      console.warn('Error al limpiar historial en PostgreSQL:', err);
    }
    setMessages([getInitialWelcomeMessage()]);
  };

  const isLight = theme === 'light';

  return (
    <>
      {/* 1. FLOATING ACTION BUTTON (FAB) */}
      {!isOpen && (
        <div className="fixed bottom-5 right-5 z-40 flex items-center gap-2 pointer-events-auto">
          <div className={`hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-mono-hud shadow-lg backdrop-blur-md border animate-bounce ${
            isLight
              ? 'bg-white/90 text-slate-800 border-sky-300 shadow-sky-500/10'
              : 'bg-slate-900/90 text-cyan-300 border-cyan-500/40 shadow-cyan-500/20'
          }`}>
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>{language === 'en' ? 'AI Advisor' : 'Asistente IA'}</span>
          </div>

          <button
            onClick={() => {
              playHoloClick(1000);
              handleOpen();
            }}
            aria-label="Abrir Asistente IA"
            className={`w-13 h-13 rounded-full flex items-center justify-center cursor-pointer shadow-2xl transition-all duration-300 hover:scale-105 active:scale-95 border ${
              isLight
                ? 'bg-sky-600 hover:bg-sky-500 text-white border-sky-400 shadow-sky-600/30'
                : 'bg-cyan-500 hover:bg-cyan-400 text-slate-950 border-cyan-300 glow-cyan shadow-cyan-500/40'
            }`}
          >
            <Bot className="w-6 h-6" />
            <span className="absolute -top-1 -right-1 w-3.5 h-3.5 rounded-full bg-emerald-400 border-2 border-slate-950 animate-pulse" />
          </button>
        </div>
      )}

      {/* 2. FLOATING CONVERSATIONAL CHAT WINDOW (w-80 sm:w-96 h-[460px]) */}
      {isOpen && (
        <div 
          onPointerDown={(e) => e.stopPropagation()}
          onWheel={(e) => e.stopPropagation()}
          className={`fixed bottom-5 right-5 z-40 w-[92vw] max-w-[384px] h-[480px] rounded-2xl flex flex-col shadow-2xl border transition-all duration-300 overflow-hidden pointer-events-auto animate-in fade-in slide-in-from-bottom-3 ${
            isLight
              ? 'bg-slate-50/95 border-slate-300 text-slate-800 shadow-slate-900/20'
              : 'bg-slate-950/95 border-cyan-500/40 text-slate-100 shadow-cyan-950/50 hud-glass-solid'
          }`}
        >
          {/* Header */}
          <div className={`px-4 py-3 border-b flex items-center justify-between select-none ${
            isLight
              ? 'bg-white border-slate-200'
              : 'bg-slate-900/80 border-cyan-500/25'
          }`}>
            <div className="flex items-center gap-2.5">
              <div className={`w-8 h-8 rounded-xl flex items-center justify-center border ${
                isLight
                  ? 'bg-sky-100 border-sky-300 text-sky-600'
                  : 'bg-cyan-500/20 border-cyan-400 text-cyan-300 glow-cyan'
              }`}>
                <Bot className="w-4 h-4" />
              </div>
              <div>
                <div className="flex items-center gap-1.5">
                  <h3 className="text-xs font-display font-bold leading-tight">
                    {t('chatTitle', language)}
                  </h3>
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                </div>
                <div className="flex items-center gap-2 text-[10px] font-mono-hud text-slate-400">
                  <span>{countryData.flag} {countryData.name}</span>
                  <span>•</span>
                  <span className="inline-flex items-center gap-1 text-emerald-400 font-medium">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                    Langflow Desktop & PostgreSQL
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-1">
              <button
                onClick={handleClearChat}
                title={t('chatClear', language)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-colors cursor-pointer"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => {
                  playHoloClick(700);
                  handleClose();
                }}
                title={t('close', language)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Quick suggestions strip */}
          <div className={`px-3 py-1.5 border-b overflow-x-auto flex gap-1.5 no-scrollbar ${
            isLight ? 'bg-slate-100/80 border-slate-200' : 'bg-slate-900/40 border-slate-800'
          }`}>
            {tList('chatQuickPrompts', language).slice(0, 3).map((prompt, idx) => (
              <button
                key={idx}
                onClick={() => handleSendMessage(prompt)}
                className={`whitespace-nowrap px-2.5 py-1 rounded-full text-[10px] font-mono-hud transition-all cursor-pointer border ${
                  isLight
                    ? 'bg-white hover:bg-sky-50 text-slate-700 border-slate-300 hover:border-sky-400'
                    : 'bg-slate-900 hover:bg-cyan-950 text-slate-300 border-cyan-500/30 hover:border-cyan-400 hover:text-cyan-300'
                }`}
              >
                {prompt}
              </button>
            ))}
          </div>

          {/* Message List */}
          <div className="flex-1 overflow-y-auto p-3 space-y-3 font-sans text-xs">
            {messages.map((msg) => {
              const isUser = msg.sender === 'user';
              return (
                <div
                  key={msg.id}
                  className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 shadow-sm leading-relaxed ${
                      isUser
                        ? isLight
                          ? 'bg-sky-600 text-white rounded-br-xs'
                          : 'bg-cyan-500 text-slate-950 font-medium rounded-br-xs'
                        : isLight
                          ? 'bg-white text-slate-800 border border-slate-200 rounded-bl-xs'
                          : 'bg-slate-900/90 text-slate-200 border border-slate-800 rounded-bl-xs'
                    }`}
                  >
                    <div className="whitespace-pre-wrap">{msg.text}</div>

                    {/* Optional Interactive Scenario Action button */}
                    {msg.action && (
                      <div className="mt-2.5 pt-2 border-t border-cyan-500/20">
                        <button
                          onClick={() => {
                            if (msg.action?.scenario) {
                              playHoloClick(1100);
                              onSelectScenario(msg.action.scenario);
                            }
                          }}
                          className={`w-full py-1.5 px-2.5 rounded-lg font-mono-hud text-[11px] font-semibold flex items-center justify-center gap-1.5 transition-all cursor-pointer ${
                            isLight
                              ? 'bg-sky-50 hover:bg-sky-100 text-sky-700 border border-sky-300'
                              : 'bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 glow-cyan'
                          }`}
                        >
                          <Zap className="w-3 h-3" />
                          <span>{msg.action.label}</span>
                          <ArrowRight className="w-3 h-3" />
                        </button>
                      </div>
                    )}

                    {/* AI Engine & PostgreSQL Provenance Badge */}
                    {!isUser && msg.source && (
                      <div className="mt-2 pt-1.5 border-t border-slate-700/30 flex items-center justify-between gap-2 text-[9px] font-mono-hud">
                        <div className="flex items-center gap-1">
                          {msg.source === 'langflow' ? (
                            <span className="inline-flex items-center gap-1 text-emerald-400 font-semibold bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">
                              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                              Langflow • Gemini 3.1
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 text-cyan-400 font-semibold bg-cyan-500/10 px-1.5 py-0.5 rounded border border-cyan-500/20">
                              <Zap className="w-2.5 h-2.5" />
                              Motor Econométrico Autónomo
                            </span>
                          )}
                        </div>
                        <span className="text-[8px] text-slate-500">PostgreSQL sync</span>
                      </div>
                    )}
                  </div>
                  <span className="text-[9px] font-mono text-slate-400 mt-1 px-1">
                    {msg.timestamp}
                  </span>
                </div>
              );
            })}

            {/* Typing Indicator */}
            {isTyping && (
              <div className="flex flex-col items-start">
                <div className={`rounded-2xl rounded-bl-xs px-3.5 py-2 flex items-center gap-2 border ${
                  isLight
                    ? 'bg-white text-slate-600 border-slate-200'
                    : 'bg-slate-900 text-cyan-300 border-cyan-500/30'
                }`}>
                  <div className="flex gap-1 items-center">
                    <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-bounce [animation-delay:-0.3s]" />
                    <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-bounce [animation-delay:-0.15s]" />
                    <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-bounce" />
                  </div>
                  <span className="text-[10px] font-mono-hud text-slate-400">
                    {t('chatTyping', language)}
                  </span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Chat Input Bar */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className={`p-2.5 border-t flex items-center gap-2 ${
              isLight ? 'bg-white border-slate-200' : 'bg-slate-900/90 border-cyan-500/25'
            }`}
          >
            <input
              ref={inputRef}
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder={t('chatPlaceholder', language)}
              className={`flex-1 text-xs px-3 py-2 rounded-xl border focus:outline-none transition-all ${
                isLight
                  ? 'bg-slate-100 text-slate-800 border-slate-300 focus:border-sky-500 focus:bg-white placeholder:text-slate-400'
                  : 'bg-slate-950 text-slate-100 border-slate-800 focus:border-cyan-400 placeholder:text-slate-500'
              }`}
            />
            <button
              type="submit"
              disabled={!inputMessage.trim() || isTyping}
              className={`p-2 rounded-xl transition-all cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed ${
                isLight
                  ? 'bg-sky-600 text-white hover:bg-sky-500 shadow-md shadow-sky-600/20'
                  : 'bg-cyan-500 text-slate-950 font-bold hover:bg-cyan-400 glow-cyan'
              }`}
              title={t('chatSend', language)}
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      )}
    </>
  );
};
