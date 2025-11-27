import React, { useEffect, useState, useRef } from 'react';
import { FlowType } from '../types';

const ArchitectureDiagram = ({ activeFlow }) => {
  // Simple animation state
  const [offset, setOffset] = useState(0);
  const containerRef = useRef(null);

  // Tooltip state
  const [tooltip, setTooltip] = useState(null);

  useEffect(() => {
    const interval = setInterval(() => {
      setOffset(prev => (prev + 1) % 20);
    }, 50);
    return () => clearInterval(interval);
  }, []);

  // Token Claims Data
  const tokenClaims = {
    user: {
      "sub": "082b2c00-2d86-460f-9f6d-775bddc1d4ba",
      "aut": "APPLICATION_USER",
      "binding_type": "cookie",
      "iss": "https://localhost:9443/oauth2/token",
      "client_id": "Kp3gcfZCdOVmMqas5VnKjZtKYjoa",
      "aud": "Kp3gcfZCdOVmMqas5VnKjZtKYjoa",
      "nbf": 1764180297,
      "azp": "Kp3gcfZCdOVmMqas5VnKjZtKYjoa",
      "org_id": "10084a8d-113f-4211-a0d5-efe36b082211",
      "scope": "email openid profile query_agent",
      "exp": 1764183897,
      "org_name": "Super",
      "iat": 1764180297,
      "binding_ref": "57523a707ab607a8e246316e2951e823",
      "jti": "620d1ee7-2540-407c-800f-acf249d21561",
      "org_handle": "carbon.super"
    },
    obo: {
      "sub": "082b2c00-2d86-460f-9f6d-775bddc1d4ba",
      "aut": "APPLICATION_USER",
      "iss": "https://localhost:9443/oauth2/token",
      "client_id": "7KafXIoqkfzS6TugWBBtby9A7FYa",
      "aud": "7KafXIoqkfzS6TugWBBtby9A7FYa",
      "nbf": 1764180730,
      "act": { "sub": "fb0dba08-1621-49f6-82e4-d81094c5de54" },
      "azp": "7KafXIoqkfzS6TugWBBtby9A7FYa",
      "org_id": "10084a8d-113f-4211-a0d5-efe36b082211",
      "exp": 1764184330,
      "org_name": "Super",
      "iat": 1764180730,
      "jti": "06b4c534-c78a-4216-9279-52251a3c0a1f",
      "org_handle": "carbon.super"
    },
    agent: {
      "sub": "fb0dba08-1621-49f6-82e4-d81094c5de54",
      "aut": "AGENT",
      "iss": "https://localhost:9443/oauth2/token",
      "client_id": "7KafXIoqkfzS6TugWBBtby9A7FYa",
      "aud": "7KafXIoqkfzS6TugWBBtby9A7FYa",
      "nbf": 1764180914,
      "azp": "7KafXIoqkfzS6TugWBBtby9A7FYa",
      "org_id": "10084a8d-113f-4211-a0d5-efe36b082211",
      "scope": "openid",
      "exp": 1764184514,
      "org_name": "Super",
      "iat": 1764180914,
      "jti": "5996c775-d66c-4921-9540-412f460915f6",
      "org_handle": "carbon.super"
    }
  };

  const handleMouseEnter = (e, type) => {
    if (tooltip?.pinned) return;
    if (!containerRef.current) return;

    const target = e.currentTarget;
    const rect = target.getBoundingClientRect();
    const containerRect = containerRef.current.getBoundingClientRect();

    const relativeLeft = rect.left - containerRect.left;
    const relativeTop = rect.top - containerRect.top;

    // Check if element is in the right half of the container
    const isRightSide = relativeLeft > containerRect.width / 2;

    setTooltip({
      visible: true,
      x: isRightSide ? relativeLeft : relativeLeft + rect.width,
      y: relativeTop,
      content: JSON.stringify(tokenClaims[type], null, 2),
      title: type === 'user' ? 'User Token' : type === 'agent' ? 'Agent Token' : 'OBO Token',
      align: isRightSide ? 'right' : 'left',
      pinned: false
    });
  };

  const handleMouseLeave = () => {
    if (tooltip?.pinned) return;
    setTooltip(null);
  };

  const handleTokenClick = (e, type) => {
    e.stopPropagation();
    if (!containerRef.current) return;

    const target = e.currentTarget;
    const rect = target.getBoundingClientRect();
    const containerRect = containerRef.current.getBoundingClientRect();

    const relativeLeft = rect.left - containerRect.left;
    const relativeTop = rect.top - containerRect.top;

    const isRightSide = relativeLeft > containerRect.width / 2;

    setTooltip({
      visible: true,
      x: isRightSide ? relativeLeft : relativeLeft + rect.width,
      y: relativeTop,
      content: JSON.stringify(tokenClaims[type], null, 2),
      title: type === 'user' ? 'User Token' : type === 'agent' ? 'Agent Token' : 'OBO Token',
      align: isRightSide ? 'right' : 'left',
      pinned: true
    });
  };

  // Colors
  const colors = {
    user: '#f97316', // Orange-500
    spa: '#e2e8f0', // Slate-200
    agent: '#cbd5e1', // Slate-300
    server: '#fef08a', // Yellow-100
    auth: '#ffedd5', // Orange-100 (Identity)
    linkDirect: '#3b82f6', // Blue-500
    linkAgent: '#8b5cf6', // Violet-500
    linkAuth: '#f59e0b', // Amber-500
    linkOBO: '#ec4899', // Pink-500 (Consent Flow)
    tokenUser: '#ea580c', // Orange-600
    tokenAgent: '#c026d3', // Fuchsia-600
    tokenOBO: '#ad0c4fff', // Pink-700
    tokenAuth: '#d97706', // Amber-600
  };

  const isDirect = activeFlow === FlowType.DIRECT;
  const isAgent = activeFlow === FlowType.AGENT;
  const isOBO = activeFlow === FlowType.OBO;

  return (
    <div ref={containerRef}
      className="w-full h-full min-h-[500px] flex items-center justify-center bg-white rounded-xl shadow-sm border border-slate-200 p-4 relative cursor-default"
    >
      <style>{`
        @keyframes flow {
          to { stroke-dashoffset: -20; }
        }
        .flow-anim {
          animation: flow 1s linear infinite;
        }
        @keyframes flow-reverse {
          to { stroke-dashoffset: 20; }
        }
        .flow-anim-reverse {
          animation: flow-reverse 1s linear infinite;
        }
        @keyframes token-drop {
            0% { transform: translateY(0); opacity: 0; }
            20% { opacity: 1; }
            80% { transform: translateY(110px); opacity: 1; }
            100% { transform: translateY(110px); opacity: 0; }
        }
        .token-drop-anim {
            animation: token-drop 2s ease-in-out infinite;
        }
        .token-hover-group {
          cursor: pointer;
          transition: filter 0.2s;
        }
        .token-hover-group:hover rect {
          stroke: #333;
          stroke-width: 2px;
          filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.2));
        }
      `}</style>

      {/* Tooltip Overlay */}
      {tooltip && (
        <div
          className={`absolute z-50 ${tooltip.pinned ? 'pointer-events-auto' : 'pointer-events-none'}`}
          style={{
            top: tooltip.y,
            left: tooltip.align === 'left' ? tooltip.x + 10 : 'auto',
            right: tooltip.align === 'right' ? (containerRef.current?.offsetWidth || 0) - tooltip.x + 10 : 'auto',
          }}
        >
          <div className="bg-[#1e293b] text-slate-300 text-[11px] p-4 rounded-md shadow-2xl font-mono border border-slate-700 max-w-md overflow-hidden bg-opacity-95">
            <div className="font-bold border-b border-slate-700 pb-2 mb-2 text-yellow-500 flex justify-between items-center tracking-wide">
              <span>{tooltip.title}</span>
              <div className="flex items-center gap-2">
                <span className="text-[10px] text-slate-500 font-normal">JWT Claims</span>
                {tooltip.pinned && (
                  <button
                    onClick={() => setTooltip(null)}
                    className="text-slate-500 hover:text-white cursor-pointer"
                    style={{ background: 'none', border: 'none', fontSize: '14px', lineHeight: '1' }}
                  >
                    ✕
                  </button>
                )}
              </div>
            </div>
            <pre className="whitespace-pre-wrap break-all leading-relaxed">
              {tooltip.content}
            </pre>
          </div>
        </div>
      )}
      <svg width="850" height="450" viewBox="0 0 850 450" className="w-full max-w-5xl">

        {/* --- DEFINITIONS --- */}
        <defs>
          <marker id="arrowhead-blue" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill={colors.linkDirect} />
          </marker>
          <marker id="arrowhead-violet" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill={colors.linkAgent} />
          </marker>
          <marker id="arrowhead-amber" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill={colors.linkAuth} />
          </marker>
          <marker id="arrowhead-pink" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill={colors.linkOBO} />
          </marker>
          <marker id="arrowhead-gray" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#64748b" />
          </marker>
        </defs>

        {/* --- NODES --- */}

        {/* Identity Server (Asgardeo) - Top Center */}
        <g transform="translate(260, 60)">
          {/* Auth Connection Lines (Behind nodes) */}
          <path d="M0 40 L0 120" stroke={colors.linkAuth} strokeWidth="2" strokeDasharray="4 4" className={isOBO ? "" : "flow-anim"} opacity={isOBO ? 0.3 : 1} />

          <rect x="-70" y="-30" width="150" height="70" rx="4" fill={colors.auth} stroke={colors.linkAuth} strokeWidth="2" />
          <text x="0" y="-5" textAnchor="middle" className="text-xs font-bold fill-amber-800">WSO2 IAM</text>
          <text x="0" y="15" textAnchor="middle" className="text-[10px] fill-amber-700">(Auth Server)</text>

          {/* Lock Icon */}
          <path d="M-8 -35 L8 -35 L8 -42 Q8 -50 0 -50 Q-8 -50 -8 -42 Z" fill="none" stroke={colors.linkAuth} strokeWidth="2" />
          <rect x="-10" y="-35" width="20" height="14" rx="2" fill="white" stroke={colors.linkAuth} strokeWidth="2" />
        </g>

        {/* User - Left */}
        <g transform="translate(60, 260)">
          <circle cx="0" cy="0" r="30" fill={colors.user} />
          <path d="M-10 -5 Q0 -20 10 -5 M-10 10 Q0 25 10 10" stroke="white" strokeWidth="3" fill="none" />
          <circle cx="0" cy="-12" r="8" fill="white" />
          <text x="0" y="45" textAnchor="middle" className="text-xs font-bold fill-slate-700">User</text>
        </g>

        {/* SPA (Clinical Compass) - Center */}
        <g transform="translate(260, 260)">
          <rect x="-70" y="-80" width="140" height="160" rx="4" fill="#fdf4f0" stroke="#94a3b8" strokeWidth="1" />
          <text x="0" y="-60" textAnchor="middle" className="text-sm font-semibold fill-slate-700">Clinical Compass</text>
          <text x="0" y="-45" textAnchor="middle" className="text-xs fill-slate-500">(SPA)</text>

          {/* Internal Client Node */}
          <rect x="-60" y="40" width="120" height="30" rx="4" fill="white" stroke={colors.linkDirect} strokeWidth="2" />
          <text x="0" y="60" textAnchor="middle" className="text-xs fill-slate-700 font-mono">MCP Client</text>
        </g>

        {/* Agent (Trial Site Advisor) - Right Top */}
        <g transform="translate(580, 140)">
          <rect x="-70" y="-50" width="140" height="100" rx="8" fill="#e2e8f0" stroke="#64748b" strokeWidth="1" />
          <text x="0" y="-30" textAnchor="middle" className="text-sm font-semibold fill-slate-700">Trial Site Advisor</text>
          <text x="0" y="-15" textAnchor="middle" className="text-xs fill-slate-600">Agent</text>
          {/* Internal Client Node */}
          <rect x="-60" y="10" width="120" height="30" rx="4" fill="white" stroke={colors.linkAgent} strokeWidth="2" />
          <text x="0" y="30" textAnchor="middle" className="text-xs fill-slate-700 font-mono">MCP Client</text>
        </g>

        {/* AI Model - Above Agent */}
        <g transform="translate(580, 30)">
          <rect x="-65" y="-25" width="130" height="50" rx="6" fill="#f0f9ff" stroke="#0ea5e9" strokeWidth="2" />
          <text x="0" y="-5" textAnchor="middle" className="text-sm font-semibold fill-slate-700">AI Model</text>
          <text x="0" y="10" textAnchor="middle" className="text-[10px] fill-slate-600">(Gemini)</text>
        </g>

        {/* MCP Server 1 - Far Right Top */}
        <g transform="translate(800, 200)">
          <rect x="-60" y="-30" width="120" height="60" rx="2" fill={colors.server} stroke="#d4d4d8" strokeWidth="1" />
          <text x="0" y="-5" textAnchor="middle" className="text-xs font-semibold fill-slate-700">MCP Server 1</text>
          <text x="0" y="15" textAnchor="middle" className="text-[10px] fill-slate-500">(Demographics)</text>
        </g>

        {/* MCP Server 2 - Far Right Bottom */}
        <g transform="translate(800, 340)">
          <rect x="-60" y="-30" width="120" height="60" rx="2" fill={colors.server} stroke="#d4d4d8" strokeWidth="1" />
          <text x="0" y="-5" textAnchor="middle" className="text-xs font-semibold fill-slate-700">MCP Server 2</text>
          <text x="0" y="15" textAnchor="middle" className="text-[10px] fill-slate-500">(Performance)</text>
        </g>

        {/* --- LINKS & FLOWS --- */}

        {/* Agent -> AI Model Link (visible in all flows, animated only in Agent/OBO modes) */}
        <line x1="580" y1="90" x2="580" y2="55" stroke="#246f2cff" strokeWidth="1" strokeDasharray="4 4" className={isAgent || isOBO ? "flow-anim" : ""} markerEnd="url(#arrowhead-green)" />

        {/* User -> SPA */}
        <line x1="90" y1="260" x2="190" y2="260" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrowhead-gray)" />

        {/* User -> Auth Server (Authenticate/Authorize) - Visible in all flows */}
        <path
          d="M 60 230 Q 60 60 190 60"
          stroke={colors.linkAuth}
          strokeWidth="2"
          fill="none"
          strokeDasharray="4 4"
          className="flow-anim"
          markerEnd="url(#arrowhead-amber)"
        />
        <text x="110" y="120" textAnchor="middle" className="text-[9px] fill-amber-600 font-bold bg-white rounded">Authenticate/Authorize</text>

        {/* SPA -> Auth Server (Request) - Normal OAuth Flow */}
        {!isOBO && (
          <g transform="translate(260, 80)">
            <g className="token-drop-anim">
              <circle r="8" fill={colors.tokenAuth} />
              <text y="4" textAnchor="middle" fill="white" fontSize="10" fontWeight="bold">T</text>
            </g>
            {/* <text x="20" y="50" className="text-[9px] fill-amber-700 font-medium opacity-80">OAuth2</text> */}
          </g>
        )}

        {/* --- OBO FLOW VISUALS --- */}
        {isOBO && (
          <>
            {/* 1. Return Link: Agent -> SPA */}
            <path
              d="M 510 140 L 330 200"
              stroke={colors.linkOBO}
              strokeWidth="2"
              fill="none"
              strokeDasharray="5,5"
              className="flow-anim"
              markerEnd="url(#arrowhead-pink)"
            />
            {/* 2. Return Link: SPA -> User */}
            <path
              d="M 190 265 L 90 265"
              stroke={colors.linkOBO}
              strokeWidth="2"
              fill="none"
              strokeDasharray="5,5"
              className="flow-anim"
              markerEnd="url(#arrowhead-pink)"
            />
            <text x="140" y="278" textAnchor="middle" className="text-[9px] fill-pink-600 font-bold bg-white p-1">Authz Request</text>

            {/* 4. Auth Server -> Agent (Token Delivery) */}
            <path
              d="M 330 60 Q 450 60 510 100"
              stroke={colors.linkAuth}
              strokeWidth="3"
              fill="none"
              strokeDasharray="4 4"
              className="flow-anim"
              markerEnd="url(#arrowhead-amber)"
            />
            {/* OBO Token Animation - Auth to Agent */}
            <circle r="6" fill={colors.tokenOBO}>
              <animateMotion
                dur="1.5s"
                repeatCount="indefinite"
                path="M 330 60 Q 450 60 510 100"
                keyPoints="0;1"
                keyTimes="0;1"
                calcMode="linear"
              />
              <text y="3" textAnchor="middle" fill="white" fontSize="8" fontWeight="bold">T</text>
            </circle>
            {/* OBO Token Label */}
            <g
              onMouseEnter={(e) => handleMouseEnter(e, 'obo')}
              onMouseLeave={handleMouseLeave}
              onClick={(e) => handleTokenClick(e, 'obo')}
              className="token-hover-group"
            >
              <rect x="400" y="40" width="60" height="14" rx="2" fill={colors.tokenOBO} fillOpacity="0.9" />
              <text x="430" y="50" textAnchor="middle" className="text-[8px] fill-white font-bold pointer-events-none">OBO Token</text>
            </g>
          </>
        )}


        {/* Agent -> Auth (Only if Agent Mode - steady state) */}
        {isAgent && (
          <>
            {/* Connection Line Agent <-> Auth */}
            <path
              d="M340 60 C 420 60, 460 140, 500 140"
              fill="none"
              stroke={colors.linkAuth}
              strokeWidth="1.5"
              strokeDasharray="4 4"
            />
            {/* Token moving from Auth to Agent */}
            <circle r="6" fill={colors.tokenAgent}>
              <animateMotion
                dur="2s"
                repeatCount="indefinite"
                path="M340 60 C 420 60, 460 140, 500 140"
                keyPoints="0;1"
                keyTimes="0;1"
                calcMode="linear"
              />
              <text y="3" textAnchor="middle" fill="white" fontSize="8" fontWeight="bold">A</text>
            </circle>
            {/* Agent Token Label (Renamed from OBO) */}
            <g
              onMouseEnter={(e) => handleMouseEnter(e, 'agent')}
              onMouseLeave={handleMouseLeave}
              onClick={(e) => handleTokenClick(e, 'agent')}
              className="token-hover-group"
            >
              <rect x="380" y="70" width="65" height="14" rx="2" fill={colors.tokenAgent} fillOpacity="0.9" />
              <text x="412" y="80" textAnchor="middle" className="text-[8px] fill-white font-bold pointer-events-none">Agent Token</text>
            </g>
          </>
        )}


        {/* SPA -> MCP Servers (Flow 1: Direct) */}
        <path
          d="M320 315 L600 315 L740 210"
          stroke={isDirect ? colors.linkDirect : '#e2e8f0'}
          strokeWidth={isDirect ? 3 : 1}
          fill="none"
          strokeDasharray={isDirect ? "10,5" : "0"}
          className={isDirect ? "flow-anim" : ""}
          markerEnd={isDirect ? "url(#arrowhead-blue)" : ""}
        />
        <path
          d="M320 315 L600 315 L740 340"
          stroke={isDirect ? colors.linkDirect : '#e2e8f0'}
          strokeWidth={isDirect ? 3 : 1}
          fill="none"
          strokeDasharray={isDirect ? "10,5" : "0"}
          className={isDirect ? "flow-anim" : ""}
          markerEnd={isDirect ? "url(#arrowhead-blue)" : ""}
        />

        {/* SPA -> Agent (Flow 2: Agent) */}
        <path
          d="M330 200 L510 140"
          stroke={isAgent ? colors.linkDirect : '#e2e8f0'}
          strokeWidth={isAgent ? 3 : 1}
          fill="none"
          strokeDasharray={isAgent ? "10,5" : "0"}
          className={isAgent ? "flow-anim" : ""}
          markerEnd={isAgent ? "url(#arrowhead-blue)" : ""}
        />

        {/* Agent -> MCP Servers (Flow 2: Agent & Flow 3: OBO) */}
        <path
          d="M650 160 L700 160 L740 190"
          stroke={(isAgent || isOBO) ? colors.linkAgent : '#e2e8f0'}
          strokeWidth={(isAgent || isOBO) ? 3 : 1}
          fill="none"
          strokeDasharray={(isAgent || isOBO) ? "10,5" : "0"}
          className={(isAgent || isOBO) ? "flow-anim" : ""}
          markerEnd={(isAgent || isOBO) ? "url(#arrowhead-violet)" : ""}
        />
        <path
          d="M650 160 L700 160 L700 320 L740 340"
          stroke={(isAgent || isOBO) ? colors.linkAgent : '#e2e8f0'}
          strokeWidth={(isAgent || isOBO) ? 3 : 1}
          fill="none"
          strokeDasharray={(isAgent || isOBO) ? "10,5" : "0"}
          className={(isAgent || isOBO) ? "flow-anim" : ""}
          markerEnd={(isAgent || isOBO) ? "url(#arrowhead-violet)" : ""}
        />

        {/* Token Animation for Agent -> MCP (Active in Agent or OBO) */}
        {(isAgent || isOBO) && (
          <>
            <circle r="5" fill={isOBO ? colors.tokenOBO : colors.tokenAgent}>
              <animateMotion
                dur="1.5s"
                repeatCount="indefinite"
                path="M650 160 L700 160 L740 190"
                begin="0.5s"
              />
              {isOBO && <text y="3" textAnchor="middle" fill="white" fontSize="6" fontWeight="bold">T</text>}
            </circle>
            <circle r="5" fill={isOBO ? colors.tokenOBO : colors.tokenAgent}>
              <animateMotion
                dur="1.8s"
                repeatCount="indefinite"
                path="M650 160 L700 160 L700 320 L740 340"
                begin="0.7s"
              />
              {isOBO && <text y="3" textAnchor="middle" fill="white" fontSize="6" fontWeight="bold">T</text>}
            </circle>
          </>
        )}

        {/* --- CONTEXT LABELS --- */}

        {/* Token Labels */}
        {!isOBO && (
          <g
            onMouseEnter={(e) => handleMouseEnter(e, 'obo')}
            onMouseLeave={handleMouseLeave}
            onClick={(e) => handleTokenClick(e, 'obo')}
            className="token-hover-group"
          >
            <rect x="220" y="140" width="80" height="20" rx="4" fill="white" stroke={colors.linkAuth} strokeWidth="1" />
            <text x="260" y="154" textAnchor="middle" className="text-[10px] fill-amber-600 font-bold pointer-events-none">User Token</text>
          </g>
        )}

        {isDirect && (
          <g
            onMouseEnter={(e) => handleMouseEnter(e, 'user')}
            onMouseLeave={handleMouseLeave}
            onClick={(e) => handleTokenClick(e, 'user')}
            className="token-hover-group"
          >
            <rect x="450" y="295" width="80" height="20" rx="4" fill={colors.tokenUser} />
            <text x="490" y="309" textAnchor="middle" className="text-[10px] fill-white font-bold pointer-events-none">User Token</text>
          </g>
        )}

        {isAgent && (
          <>
            <g
              onMouseEnter={(e) => handleMouseEnter(e, 'user')}
              onMouseLeave={handleMouseLeave}
              onClick={(e) => handleTokenClick(e, 'user')}
              className="token-hover-group"
            >
              <rect x="380" y="150" width="80" height="20" rx="4" fill={colors.tokenUser} />
              <text x="420" y="164" textAnchor="middle" className="text-[10px] fill-white font-bold pointer-events-none">User Token</text>
            </g>
            <g
              onMouseEnter={(e) => handleMouseEnter(e, 'agent')}
              onMouseLeave={handleMouseLeave}
              onClick={(e) => handleTokenClick(e, 'agent')}
              className="token-hover-group"
            >
              <rect x="660" y="120" width="80" height="20" rx="4" fill={colors.tokenAgent} />
              <text x="700" y="134" textAnchor="middle" className="text-[10px] fill-white font-bold pointer-events-none">Agent Token</text>
            </g>
          </>
        )}

        {isOBO && (
          <g
            onMouseEnter={(e) => handleMouseEnter(e, 'obo')}
            onMouseLeave={handleMouseLeave}
            onClick={(e) => handleTokenClick(e, 'obo')}
            className="token-hover-group"
          >
            <rect x="660" y="120" width="80" height="20" rx="4" fill={colors.tokenOBO} />
            <text x="700" y="134" textAnchor="middle" className="text-[10px] fill-white font-bold pointer-events-none">OBO Token</text>
          </g>
        )}

      </svg>

      {/* Legend Overlay */}
      {/* <div className="absolute top-4 left-4 bg-white/90 p-3 rounded-lg border border-slate-200 text-xs shadow-sm">
        <div className="flex items-center gap-2 mb-1">
          <div className="w-3 h-3 rounded bg-amber-500"></div>
          <span>Identity / Auth</span>
        </div>
        <div className="flex items-center gap-2 mb-1">
          <div className="w-3 h-3 rounded bg-blue-500"></div>
          <span>Direct Flow</span>
        </div>
        <div className="flex items-center gap-2 mb-1">
          <div className="w-3 h-3 rounded bg-violet-500"></div>
          <span>Agent Flow</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-pink-500"></div>
          <span>OBO Consent</span>
        </div>
      </div> */}
    </div>
  );
};

export default ArchitectureDiagram;