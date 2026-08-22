import React, { useState, useEffect } from 'react'
import {
  ArrowRight,
  Download,
  ChevronDown,
  ExternalLink,
  Shield,
  Monitor,
  Apple,
  Terminal,
  Layers,
  Cpu,
  ArrowUpRight
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
      {/* Navigation Header */}
      <header className="landing-nav">
        <div className="landing-nav-brand">
          <span className="landing-brand-name">SarvaFlow</span>
          <span className="landing-beta-pill">v1.0-beta</span>
        </div>
        <div className="landing-nav-actions">
          <button className="landing-control-room-btn" onClick={onOpenAppDirectly}>
            Open Control Room <ArrowUpRight size={14} />
          </button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="landing-hero">
        <div className="landing-pill-tag">
          AUTONOMOUS TREASURY & CFO OPERATING SYSTEM
        </div>

        <h1 className="landing-hero-title">
          Unified cash forecasting and automated compliance for modern finance.
        </h1>

        <p className="landing-hero-sub">
          Continuous financial document ingestion, 90-day probabilistic runway modeling, real-time GST tax reconciliation, and automated wire clearing across Web and Desktop.
        </p>

        {/* Primary Action Buttons */}
        <div className="landing-cta-group">
          <button className="landing-btn-primary" onClick={onGetStarted}>
            Get Started on Web <ArrowRight size={16} />
          </button>

          <div className="landing-dropdown-wrapper">
            <button
              className="landing-btn-secondary"
              onClick={() => setShowDownloadDropdown(!showDownloadDropdown)}
            >
              <Download size={15} />
              <span>
                Download for {selectedOs === 'mac' ? 'macOS (.dmg)' : selectedOs === 'windows' ? 'Windows (.msi)' : 'Linux (.AppImage)'}
              </span>
              <ChevronDown size={14} />
            </button>

            {/* Dropdown Options */}
            {showDownloadDropdown && (
              <div className="landing-dropdown-menu">
                <div className="landing-dropdown-header">Select Architecture Installer</div>

                {/* macOS */}
                <a
                  href={getDownloadUrl('mac')}
                  target="_blank"
                  rel="noreferrer"
                  className={`landing-dropdown-item ${selectedOs === 'mac' ? 'active' : ''}`}
                  onClick={() => setSelectedOs('mac')}
                >
                  <div className="item-info">
                    <Apple size={16} />
                    <div>
                      <div className="item-title">macOS</div>
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
                    <Monitor size={16} />
                    <div>
                      <div className="item-title">Windows</div>
                      <div className="item-sub">Windows 10 / 11 x64 (.msi)</div>
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
                    <Terminal size={16} />
                    <div>
                      <div className="item-title">Linux</div>
                      <div className="item-sub">.AppImage & .deb Packages</div>
                    </div>
                  </div>
                  {detectedOs === 'linux' && <span className="detected-badge">Detected</span>}
                </a>

                <div className="landing-dropdown-footer">
                  <a href={repoReleaseUrl} target="_blank" rel="noreferrer">
                    Release notes & checksums on GitHub <ExternalLink size={10} />
                  </a>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Mode Switch Sublinks */}
        <div className="landing-switch-links">
          <span>
            Deploy in browser:{' '}
            <button onClick={onGetStarted} className="inline-link-btn">
              Direct Web App
            </button>
          </span>
          <span className="dot-sep">•</span>
          <span>
            Offline-capable runtime:{' '}
            <button onClick={() => setShowDownloadDropdown(true)} className="inline-link-btn">
              Desktop Tauri Build
            </button>
          </span>
        </div>

        {/* Security Notice */}
        <div className="landing-security-banner">
          <Shield size={16} className="security-icon" />
          <div className="security-text">
            <strong>Pre-Release Binary Verification</strong>
            Installer packages are compiled with automated GitHub Release CI checksums. Unsigned beta warnings (SmartScreen / Gatekeeper) on initial launch are safe to proceed.
          </div>
        </div>
      </section>

      {/* Live Data View Preview */}
      <section className="landing-mockup-section">
        <div className="mockup-window">
          <div className="mockup-header">
            <div className="dots">
              <span className="dot" />
              <span className="dot" />
              <span className="dot" />
            </div>
            <div className="window-title">SARVAFLOW_CFO_CONTROL_ROOM — LIVE LEDGER ENGINE</div>
            <div className="status-live">● ENGINE LIVE</div>
          </div>
          <div className="mockup-body">
            <div className="mockup-grid">
              <div className="mockup-card">
                <div className="card-label">90-DAY CASH RUNWAY (P50)</div>
                <div className="card-value">$48,920,000</div>
                <div className="card-sub text-green">+ $152.5k Auto-Pilot Yield Captured</div>
              </div>
              <div className="mockup-card">
                <div className="card-label">INDIA GST RECONCILIATION</div>
                <div className="card-value">100%</div>
                <div className="card-sub">GSTR-1, 2B & 3B Audit Clear</div>
              </div>
              <div className="mockup-card">
                <div className="card-label">MULTI-AGENT MESH</div>
                <div className="card-value">4 ACTIVE</div>
                <div className="card-sub">0 AP Duplicate Wire Leaks</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 3-Column Architectural Pillars */}
      <section className="landing-features">
        <div className="feature-card">
          <h3>Probabilistic Forecasting</h3>
          <p>
            Monte Carlo quantile projection modeling p10, p50, and p90 treasury positions with live bank feed telemetry and payment terms variance.
          </p>
        </div>

        <div className="feature-card">
          <h3>India-First Tax Sentinel</h3>
          <p>
            Automated GSTR-1, 2B, and 3B reconciliation, HSN/SAC code classification, and duplicate payment protection embedded directly into payment rails.
          </p>
        </div>

        <div className="feature-card">
          <h3>Unified Desktop Runtime</h3>
          <p>
            Built on Tauri v2 with automatic background updates, native OS hardware security, and zero data divergence between Web and Desktop.
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div>SarvaFlow Financial Technologies. All rights reserved.</div>
        <div className="footer-status">
          <span className="green-dot" /> Operational • Production Cluster
        </div>
      </footer>
    </div>
  )
}
