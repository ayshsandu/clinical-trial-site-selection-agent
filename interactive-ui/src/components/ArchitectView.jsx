import { useState } from 'react';
import ArchitectureDiagram from './ArchitectureDiagram';
import { FlowType } from '../types';
import './ArchitectView.css';

const ArchitectView = () => {
    const [activeFlow, setActiveFlow] = useState(FlowType.DIRECT);

    return (
        <div className="architect-view">
            {/* Main Content */}
            <main className="architect-main">
                <div className="architect-grid">
                    {/* Left Column: Interactive Diagram */}
                    <div className="architect-diagram-column">
                        {/* Control Bar */}
                        <div className="architect-control-bar">
                            <div>
                                <h2 className="control-bar-title">Architecture Flow</h2>
                                <p className="control-bar-subtitle">Visualize token propagation and service interaction.</p>
                            </div>

                            <div className="flow-toggle-group">
                                <button
                                    onClick={() => setActiveFlow(FlowType.DIRECT)}
                                    className={`flow-toggle-btn ${activeFlow === FlowType.DIRECT ? 'active-direct' : ''
                                        }`}
                                >
                                    Direct Client
                                </button>
                                <button
                                    onClick={() => setActiveFlow(FlowType.AGENT)}
                                    className={`flow-toggle-btn ${activeFlow === FlowType.AGENT ? 'active-agent' : ''
                                        }`}
                                >
                                    Agent Flow
                                </button>
                                <button
                                    onClick={() => setActiveFlow(FlowType.OBO)}
                                    className={`flow-toggle-btn ${activeFlow === FlowType.OBO ? 'active-obo' : ''
                                        }`}
                                >
                                    OBO Flow
                                </button>
                            </div>
                        </div>

                        {/* Diagram Viewport */}
                        <ArchitectureDiagram activeFlow={activeFlow} />

                        {/* Explainer Text */}
                        <div className={`explainer-box ${activeFlow === FlowType.OBO ? 'explainer-obo' : 'explainer-default'
                            }`}>
                            <h3 className={`explainer-title ${activeFlow === FlowType.OBO ? 'explainer-title-obo' : 'explainer-title-default'
                                }`}>
                                <svg className="explainer-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                System Logic
                            </h3>
                            <p className={`explainer-text ${activeFlow === FlowType.OBO ? 'explainer-text-obo' : 'explainer-text-default'
                                }`}>
                                {activeFlow === FlowType.DIRECT && (
                                    <>
                                        In <strong>Direct Mode</strong>, the Single Page Application (SPA) authenticates the user directly.
                                        It obtains a <strong>User Token</strong> which is passed directly to the MCP Servers (Demographics, Site Performance)
                                        via the local MCP Client. This represents a standard secure interaction where the user's identity is maintained end-to-end.
                                    </>
                                )}
                                {activeFlow === FlowType.AGENT && (
                                    <>
                                        In <strong>Agent Mode</strong>, the SPA invokes the "Trial Site Advisor" Agent to perform complex analysis tasks.
                                        The Agent has its own credentials and can authenticate with the Authorization server to obtain an <strong>Agent Token</strong> with its own permissions.
                                        The Agent receives the <strong>User Token</strong> along with the incoming requests, but when communicating with backend MCP services, it uses its own <strong>Agent Token</strong>
                                        to perform to interact with MCP servers.
                                    </>
                                )}
                                {activeFlow === FlowType.OBO && (
                                    <>
                                        In <strong>OBO Flow Mode</strong>, the Agent requires elevated privileges or a refreshed delegation from the user.
                                        It initiates a reverse flow, requesting the User (via SPA) to re-authenticate or consent.
                                        The User authenticates by submitting credentials directly to the Identity Server (or SSO if session exists), which then issues a specialized <strong>OBO Token</strong>
                                        directly to the Agent, bypassing the client for enhanced security.
                                        The Agent then uses this <strong>OBO Token</strong> to perform actions on behalf of the User.
                                    </>
                                )}
                            </p>
                        </div>
                    </div>

                    {/* Right Column: Information Panel */}
                    <div className="architect-info-column">
                        <div className="info-panel">
                            <h2 className="info-panel-title">
                                <span className="info-icon">📐</span>
                                Architecture Overview
                            </h2>
                            <p className="info-panel-text">
                                This interactive diagram visualizes the Clinical Compass architecture and demonstrates
                                how authentication tokens flow through the system in different modes.
                            </p>

                            <div className="info-section">
                                <h3 className="info-section-title">Key Components</h3>
                                <ul className="info-list">
                                    <li><strong>Identity Server / Asgardeo:</strong> Handles authentication and token issuance</li>
                                    <li><strong>Clinical Compass SPA:</strong> The user-facing web application</li>
                                    <li><strong>Trial Site Advisor Agent:</strong> AI-powered agent for complex analysis</li>
                                    <li><strong>MCP Servers:</strong> Backend services providing tools and resources</li>
                                </ul>
                            </div>

                            <div className="info-section">
                                <h3 className="info-section-title">Flow Types</h3>
                                <div className="flow-type-card">
                                    <div className="flow-type-badge badge-direct">Direct</div>
                                    <p className="flow-type-desc">User directly interacts with MCP servers through the SPA with users delegated token</p>
                                </div>
                                <div className="flow-type-card">
                                    <div className="flow-type-badge badge-agent">Agent</div>
                                    <p className="flow-type-desc">Agent obtains a token from the Auth Server by verifying its own identity and uses it to interact with MCP servers</p>
                                </div>
                                <div className="flow-type-card">
                                    <div className="flow-type-badge badge-obo">OBO</div>
                                    <p className="flow-type-desc">Agent obtain a delegated token from the Auth Server On-behalf-of the user and uses it to interact with MCP servers</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default ArchitectView;
