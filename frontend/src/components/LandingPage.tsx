import React, { useState, useEffect } from 'react'
import {
  Zap,
  Download,
  CheckCircle,
  ShieldAlert,
  ArrowRight,
  Monitor,
  Apple,
  Terminal,
  Sparkles,
  ChevronDown,
  ExternalLink,
  ShieldCheck,
  TrendingUp,
  Activity,
  Layers,
  Bot,
  Lock,
  Globe,
  Check
} from 'lucide-react'

interface LandingPageProps {
  onGetStarted: () => void
  onOpenAppDirectly: () => void
}

export type OperatingSystem = 'mac' | 'windows' | 'linux'

interface ReleaseAssets {
  macDmg?: string
  windowsMsi?: string
  linuxAppImage?: string
  linuxDeb?: string
  tagName?: string
}

export const LandingPage: React.FC<LandingPageProps> = ({ onGetStarted, onOpenAppDirectly }) => {
  const [detectedOs, setDetectedOs] = useState<OperatingSystem>('windows')
  const [showDownloadDropdown, setShowDownloadDropdown] = useState<boolean>(false)
  const [selectedOs, setSelectedOs] = useState<OperatingSystem>('windows')
  const [releaseAssets, setReleaseAssets] = useState<ReleaseAssets>({})

  // 1. Auto-detect Visitor's Operating System
  useEffect(() => {
    const ua = navigator.userAgent.toLowerCase()
    if (ua.includes('mac') || ua.includes('darwin') || ua.includes('iphone') || ua.includes('ipad')) {
      setDetectedOs('mac')
      setSelectedOs('mac')
    } else if (ua.includes('linux') || ua.includes('x11') || ua.includes('ubuntu')) {
      setDetectedOs('linux')
      setSelectedOs('linux')
    } else {
      setDetectedOs('windows')
      setSelectedOs('windows')
    }
  }, [])

  // 2. Dynamic GitHub Release Fetcher
  useEffect(() => {
    const fetchLatestRelease = async () => {
      try {
        const res = await fetch('https://api.github.com/repos/Shubh-creations/sarvaflow/releases/latest')
        if (res.ok) {
          const data = await res.json()
          const assets: ReleaseAssets = { tagName: data.tag_name || 'v1.0.0' }
          if (Array.isArray(data.assets)) {
            data.assets.forEach((asset: any) => {
              const name = asset.name.toLowerCase()
              if (name.endsWith('.dmg')) assets.macDmg = asset.browser_download_url
              if (name.endsWith('.msi')) assets.windowsMsi = asset.browser_download_url
              if (name.endsWith('.appimage')) assets.linuxAppImage = asset.browser_download_url
              if (name.endsWith('.deb')) assets.linuxDeb = asset.browser_download_url
            })
          }
          setReleaseAssets(assets)
        }
      } catch (err) {
        console.warn('GitHub release query fallback active', err)
      }
    }
    fetchLatestRelease()
  }, [])

  const repoReleaseUrl = 'https://github.com/Shubh-creations/sarvaflow/releases/latest'
  const getDownloadUrl = (os: OperatingSystem) => {
    if (os === 'mac') return releaseAssets.macDmg || repoReleaseUrl
    if (os === 'windows') return releaseAssets.windowsMsi || repoReleaseUrl
    if (os === 'linux') return releaseAssets.linuxAppImage || releaseAssets.linuxDeb || repoReleaseUrl
    return repoReleaseUrl
  }

  return (
    <div className="landing-root">
      {/* Top Brand Header */}
      <header className="landing-nav">
        <div className="landing-nav-brand">
          <div className="landing-logo-icon">
            <Zap size={20} />
          </div>
          <span className="landing-brand-name">SarvaFlow</span>
          <span className="landing-beta-pill">Enterprise Beta</span>
        </div>
        <div className="landing-nav-actions">
          <button className="landing-control-room-btn" onClick={onOpenAppDirectly}>
            Enter Control Room <ArrowRight size={15} />
          </button>
        </div>
      </header>

      {/* Main Hero Container */}
      <section className="landing-hero">
        <div className="landing-pill-tag">
          <Sparkles size={14} /> Autonomous AI CFO & Treasury Operating System
        </div>

        <h1 className="landing-hero-title">
          Unify Cash Forecasting, Working Capital &<br />
          <span className="landing-hero-gradient">India-First Tax Compliance Automatically</span>
        </h1>

        <p className="landing-hero-sub">
          SarvaFlow autonomously ingests financial documents, flags tax anomalies, detects duplicate invoice leaks, and monitors debt covenants in real-time across Web and Desktop.
        </p>

        {/* Dual Primary CTA Container */}
        <div className="landing-cta-group">
          {/* Action 1: Get Started Web */}
          <button className="landing-btn-primary" onClick={onGetStarted}>
            <Zap size={20} />
            <span>Get Started on Web</span>
            <ArrowRight size={18} />
          </button>

          {/* Action 2: Download Desktop */}
          <div className="landing-dropdown-wrapper">
            <button
              className="landing-btn-secondary"
              onClick={() => setShowDownloadDropdown(!showDownloadDropdown)}
            >
              <Download size={18} />
              <span>
                Download for {selectedOs === 'mac' ? 'macOS (.dmg)' : selectedOs === 'windows' ? 'Windows (.msi)' : 'Linux (.AppImage)'}
              </span>
              <ChevronDown size={16} className={showDownloadDropdown ? 'rotate-180' : ''} />
            </button>

            {/* Dropdown Options */}
            {showDownloadDropdown && (
              <div className="landing-dropdown-menu">
                <div className="landing-dropdown-header">Select Platform Installer</div>

                {/* macOS */}
                <a
                  href={getDownloadUrl('mac')}
                  target="_blank"
                  rel="noreferrer"
                  className={`landing-dropdown-item ${selectedOs === 'mac' ? 'active' : ''}`}
                  onClick={() => setSelectedOs('mac')}
                >
                  <div className="item-info">
                    <Apple size={18} color="#e2e8f0" />
                    <div>
                      <div className="item-title">macOS Installer</div>
                      <div className="item-sub">Apple Silicon & Intel (.dmg)</div>
                    </div>
                  </div>
                  {detectedOs === 'mac' && <span className="detected-badge">Detected</span>}
                </a>

                {/* Windows */}
                <a
                  href={getDownloadUrl('windows')}
                  target="_blank"
                  rel="noreferrer"
                  className={`landing-dropdown-item ${selectedOs === 'windows' ? 'active' : ''}`}
                  onClick={() => setSelectedOs('windows')}
                >
                  <div className="item-info">
                    <Monitor size={18} color="#60a5fa" />
                    <div>
                      <div className="item-title">Windows Installer</div>
                      <div className="item-sub">Windows 10/11 x64 (.msi)</div>
                    </div>
                  </div>
                  {detectedOs === 'windows' && <span className="detected-badge">Detected</span>}
                </a>

                {/* Linux */}
                <a
                  href={getDownloadUrl('linux')}
                  target="_blank"
                  rel="noreferrer"
                  className={`landing-dropdown-item ${selectedOs === 'linux' ? 'active' : ''}`}
                  onClick={() => setSelectedOs('linux')}
                >
                  <div className="item-info">
                    <Terminal size={18} color="#34d399" />
                    <div>
                      <div className="item-title">Linux Package</div>
                      <div className="item-sub">.AppImage & .deb Package</div>
                    </div>
                  </div>
                  {detectedOs === 'linux' && <span className="detected-badge">Detected</span>}
                </a>

                <div className="landing-dropdown-footer">
                  <a href={repoReleaseUrl} target="_blank" rel="noreferrer">
                    View all releases on GitHub <ExternalLink size={11} />
                  </a>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Easy Switcher Sublinks */}
        <div className="landing-switch-links">
          <span>
            Prefer web?{' '}
            <button onClick={onGetStarted} className="inline-link-btn">
              Get Started directly on Web
            </button>
          </span>
          <span className="dot-sep">•</span>
          <span>
            Want native desktop app?{' '}
            <button onClick={() => setShowDownloadDropdown(true)} className="inline-link-btn">
              Download Desktop
            </button>
          </span>
        </div>

        {/* Honest Security Note Banner */}
        <div className="landing-security-banner">
          <ShieldAlert size={20} className="security-icon" />
          <div className="security-text">
            <strong>Pre-Release OS Security Note</strong>
            You may see an OS security prompt (Windows SmartScreen / macOS Gatekeeper) on first launch. This is expected for a new beta release and safe to proceed ("Run Anyway" or "Open").
          </div>
        </div>
      </section>

      {/* Product Showcase Window Mockup */}
      <section className="landing-mockup-section">
        <div className="mockup-window">
          <div className="mockup-header">
            <div className="dots">
              <span className="dot red" />
              <span className="dot yellow" />
              <span className="dot green" />
            </div>
            <div className="window-title">SarvaFlow Executive Control Room — Live Dashboard</div>
            <div className="status-live">● System Live</div>
          </div>
          <div className="mockup-body">
            <div className="mockup-grid">
              <div className="mockup-card">
                <div className="card-label">90-DAY PROBABILISTIC CASH RUNWAY</div>
                <div className="card-value">$48,920,000</div>
                <div className="card-sub text-green">↑ +$152,500 Auto-Pilot Yield Captured</div>
              </div>
              <div className="mockup-card">
                <div className="card-label">INDIA GST RECONCILIATION</div>
                <div className="card-value">100% Compliant</div>
                <div className="card-sub text-blue">GSTR-1 / 2B / 3B Verified</div>
              </div>
              <div className="mockup-card">
                <div className="card-label">MULTI-AGENT MESH</div>
                <div className="card-value">4 Active Agents</div>
                <div className="card-sub text-purple">0 Duplicate AP Wire Leaks</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 3-Column Feature Cards */}
      <section className="landing-features">
        <div className="feature-card">
          <div className="feature-icon blue">
            <TrendingUp size={22} />
          </div>
          <h3>90-Day Quantile Forecasting</h3>
          <p>
            Monte Carlo probabilistic modeling projects p10, p50, and p90 cash runways with real-time volatility bounds.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon green">
            <ShieldCheck size={22} />
          </div>
          <h3>India-First GST Compliance</h3>
          <p>
            Instant GSTR-1, 2B, 3B tax audit, HSN/SAC code validation, and duplicate payment leak prevention built into cash workflows.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon purple">
            <Monitor size={22} />
          </div>
          <h3>Tauri Native Cross-Platform</h3>
          <p>
            Wraps exact production web frontend via Tauri v2 with built-in auto-updater. Zero data divergence between Web and Desktop.
          </p>
        </div>
      </section>

      {/* Simple Footer */}
      <footer className="landing-footer">
        <div>© 2026 SarvaFlow Systems. All rights reserved.</div>
        <div className="footer-status">
          <span className="green-dot" /> All Systems Operational (Supabase + Vercel)
        </div>
      </footer>
    </div>
  )
}
