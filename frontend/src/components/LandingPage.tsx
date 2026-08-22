import React, { useState, useEffect } from 'react'
import {
  Zap,
  Download,
  CheckCircle,
  ShieldAlert,
  ArrowRight,
  Monitor,
  Apple,
  HardDrive,
  Terminal,
  Globe,
  Sparkles,
  ChevronDown,
  ExternalLink,
  ShieldCheck
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
  const [loadingAssets, setLoadingAssets] = useState<boolean>(true)

  // 1. Auto-detect Visitor's Operating System from Browser UserAgent
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

  // 2. Fetch Latest Release Download Links Dynamically from GitHub API
  useEffect(() => {
    const fetchLatestRelease = async () => {
      try {
        setLoadingAssets(true)
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
        console.warn('Could not fetch GitHub release assets dynamically', err)
      } finally {
        setLoadingAssets(false)
      }
    }
    fetchLatestRelease()
  }, [])

  // Fallback release download URLs if GitHub API rate-limited
  const repoReleaseUrl = 'https://github.com/Shubh-creations/sarvaflow/releases/latest'
  const getDownloadUrl = (os: OperatingSystem) => {
    if (os === 'mac') return releaseAssets.macDmg || `${repoReleaseUrl}`
    if (os === 'windows') return releaseAssets.windowsMsi || `${repoReleaseUrl}`
    if (os === 'linux') return releaseAssets.linuxAppImage || releaseAssets.linuxDeb || `${repoReleaseUrl}`
    return repoReleaseUrl
  }

  return (
    <div className="landing-page-container" style={{ background: 'var(--bg-primary)', color: 'var(--text-primary)', minHeight: '100vh', padding: '2rem' }}>
      {/* Top Brand Bar */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', maxWidth: '1200px', margin: '0 auto 4rem auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ background: 'var(--accent-primary)', width: '36px', height: '36px', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff' }}>
            <Zap size={22} />
          </div>
          <span style={{ fontSize: '1.4rem', fontWeight: '800', letterSpacing: '-0.02em', color: 'var(--text-primary)' }}>SarvaFlow</span>
          <span style={{ fontSize: '0.75rem', background: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa', padding: '0.2rem 0.6rem', borderRadius: '12px', fontWeight: '600', marginLeft: '0.5rem' }}>Enterprise Beta</span>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <button className="button ghost" onClick={onOpenAppDirectly} style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
            Enter Control Room <ArrowRight size={16} style={{ marginLeft: '4px' }} />
          </button>
        </div>
      </header>

      {/* Main Hero Section */}
      <main style={{ maxWidth: '1100px', margin: '0 auto', textAlign: 'center' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(16, 185, 129, 0.1)', color: '#34d399', padding: '0.4rem 1rem', borderRadius: '20px', fontSize: '0.85rem', fontWeight: '600', marginBottom: '1.5rem' }}>
          <Sparkles size={16} /> Autonomous AI CFO & Treasury Operating System
        </div>

        <h1 style={{ fontSize: '3.2rem', fontWeight: '900', lineHeight: '1.15', marginBottom: '1.5rem', letterSpacing: '-0.03em' }}>
          Unify Cash Forecasting, Working Capital &<br />
          <span style={{ background: 'linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            India-First Tax Compliance Automatically
          </span>
        </h1>

        <p style={{ fontSize: '1.2rem', color: 'var(--text-secondary)', maxWidth: '800px', margin: '0 auto 3rem auto', lineHeight: '1.6' }}>
          SarvaFlow autonomously ingests financial documents, flags tax anomalies, detects duplicate invoices, and monitors debt covenants in real-time across Web and Desktop.
        </p>

        {/* Dual Action Buttons (Side by Side) */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '1.5rem', alignItems: 'center', flexWrap: 'wrap', marginBottom: '2rem' }}>
          {/* Button 1: Get Started (Primary Web Sign-In / Flow) */}
          <button
            onClick={onGetStarted}
            className="button primary"
            style={{
              padding: '1rem 2.2rem',
              fontSize: '1.1rem',
              fontWeight: '700',
              borderRadius: '10px',
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              boxShadow: '0 10px 25px -5px rgba(59, 130, 246, 0.4)',
              cursor: 'pointer'
            }}
          >
            <Zap size={22} /> Get Started on Web <ArrowRight size={18} />
          </button>

          {/* Button 2: Download Desktop App (Secondary Outlined Dropdown) */}
          <div style={{ position: 'relative' }}>
            <button
              onClick={() => setShowDownloadDropdown(!showDownloadDropdown)}
              className="button secondary"
              style={{
                padding: '1rem 2rem',
                fontSize: '1.1rem',
                fontWeight: '700',
                borderRadius: '10px',
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                color: 'var(--text-primary)',
                cursor: 'pointer'
              }}
            >
              <Download size={20} />
              <span>
                Download for {selectedOs === 'mac' ? 'macOS (.dmg)' : selectedOs === 'windows' ? 'Windows (.msi)' : 'Linux (.AppImage)'}
              </span>
              <ChevronDown size={18} style={{ transform: showDownloadDropdown ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }} />
            </button>

            {/* Dropdown Panel */}
            {showDownloadDropdown && (
              <div
                style={{
                  position: 'absolute',
                  top: '110%',
                  right: '0',
                  left: '0',
                  minWidth: '320px',
                  background: '#1e293b',
                  border: '1px solid rgba(255, 255, 255, 0.15)',
                  borderRadius: '12px',
                  padding: '1rem',
                  boxShadow: '0 20px 40px rgba(0, 0, 0, 0.5)',
                  zIndex: 1000,
                  textAlign: 'left'
                }}
              >
                <div style={{ fontSize: '0.75rem', fontWeight: '700', textTransform: 'uppercase', color: '#94a3b8', marginBottom: '0.75rem', letterSpacing: '0.05em' }}>
                  Select Platform Architecture
                </div>

                {/* macOS Option */}
                <a
                  href={getDownloadUrl('mac')}
                  target="_blank"
                  rel="noreferrer"
                  onClick={() => setSelectedOs('mac')}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '0.75rem',
                    borderRadius: '8px',
                    background: selectedOs === 'mac' ? 'rgba(59, 130, 246, 0.15)' : 'transparent',
                    border: selectedOs === 'mac' ? '1px solid #3b82f6' : '1px solid transparent',
                    color: 'var(--text-primary)',
                    textDecoration: 'none',
                    marginBottom: '0.5rem'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <Apple size={20} color="#e2e8f0" />
                    <div>
                      <div style={{ fontWeight: '600', fontSize: '0.95rem' }}>macOS Installer</div>
                      <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Apple Silicon & Intel (.dmg)</div>
                    </div>
                  </div>
                  {detectedOs === 'mac' && (
                    <span style={{ fontSize: '0.7rem', background: '#3b82f6', color: '#fff', padding: '0.15rem 0.5rem', borderRadius: '10px', fontWeight: '700' }}>
                      Detected
                    </span>
                  )}
                </a>

                {/* Windows Option */}
                <a
                  href={getDownloadUrl('windows')}
                  target="_blank"
                  rel="noreferrer"
                  onClick={() => setSelectedOs('windows')}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '0.75rem',
                    borderRadius: '8px',
                    background: selectedOs === 'windows' ? 'rgba(59, 130, 246, 0.15)' : 'transparent',
                    border: selectedOs === 'windows' ? '1px solid #3b82f6' : '1px solid transparent',
                    color: 'var(--text-primary)',
                    textDecoration: 'none',
                    marginBottom: '0.5rem'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <Monitor size={20} color="#60a5fa" />
                    <div>
                      <div style={{ fontWeight: '600', fontSize: '0.95rem' }}>Windows Installer</div>
                      <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Windows 10/11 x64 (.msi)</div>
                    </div>
                  </div>
                  {detectedOs === 'windows' && (
                    <span style={{ fontSize: '0.7rem', background: '#3b82f6', color: '#fff', padding: '0.15rem 0.5rem', borderRadius: '10px', fontWeight: '700' }}>
                      Detected
                    </span>
                  )}
                </a>

                {/* Linux Option */}
                <a
                  href={getDownloadUrl('linux')}
                  target="_blank"
                  rel="noreferrer"
                  onClick={() => setSelectedOs('linux')}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '0.75rem',
                    borderRadius: '8px',
                    background: selectedOs === 'linux' ? 'rgba(59, 130, 246, 0.15)' : 'transparent',
                    border: selectedOs === 'linux' ? '1px solid #3b82f6' : '1px solid transparent',
                    color: 'var(--text-primary)',
                    textDecoration: 'none'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <Terminal size={20} color="#34d399" />
                    <div>
                      <div style={{ fontWeight: '600', fontSize: '0.95rem' }}>Linux Package</div>
                      <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>.AppImage & .deb Package</div>
                    </div>
                  </div>
                  {detectedOs === 'linux' && (
                    <span style={{ fontSize: '0.7rem', background: '#3b82f6', color: '#fff', padding: '0.15rem 0.5rem', borderRadius: '10px', fontWeight: '700' }}>
                      Detected
                    </span>
                  )}
                </a>

                {/* Direct Link to GitHub Releases */}
                <div style={{ marginTop: '0.75rem', paddingTop: '0.5rem', borderTop: '1px solid rgba(255,255,255,0.1)', textAlign: 'center' }}>
                  <a href={repoReleaseUrl} target="_blank" rel="noreferrer" style={{ fontSize: '0.75rem', color: '#60a5fa', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                    View all releases on GitHub <ExternalLink size={12} />
                  </a>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Easy Switching Links */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '2rem', fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '3rem' }}>
          <span>
            Prefer the web app?{' '}
            <button onClick={onGetStarted} style={{ background: 'none', border: 'none', color: '#60a5fa', textDecoration: 'underline', cursor: 'pointer', padding: 0, fontWeight: '600' }}>
              Get Started directly on Web
            </button>
          </span>
          <span>•</span>
          <span>
            Want native performance?{' '}
            <button onClick={() => setShowDownloadDropdown(true)} style={{ background: 'none', border: 'none', color: '#60a5fa', textDecoration: 'underline', cursor: 'pointer', padding: 0, fontWeight: '600' }}>
              Download Desktop App
            </button>
          </span>
        </div>

        {/* Honest Code-Signing Security Note (Part 4 Requirement) */}
        <div
          style={{
            maxWidth: '680px',
            margin: '0 auto 4rem auto',
            background: 'rgba(245, 158, 11, 0.08)',
            border: '1px solid rgba(245, 158, 11, 0.25)',
            borderRadius: '10px',
            padding: '1rem 1.25rem',
            textAlign: 'left',
            display: 'flex',
            gap: '0.75rem',
            alignItems: 'flex-start'
          }}
        >
          <ShieldAlert size={20} color="#f59e0b" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div style={{ fontSize: '0.85rem', color: '#fcd34d', lineHeight: '1.5' }}>
            <strong style={{ color: '#fbbf24', display: 'block', marginBottom: '2px' }}>Pre-Release Security Note</strong>
            You may see an OS security prompt (Windows SmartScreen / macOS Gatekeeper) on first launch. This is expected for a brand-new beta app and completely safe to proceed ("Run Anyway" or "Open").
          </div>
        </div>

        {/* Key Feature Pillars */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem', textAlign: 'left', margin: '2rem 0' }}>
          <div style={{ background: 'var(--bg-secondary)', padding: '1.5rem', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
            <div style={{ background: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa', width: '40px', height: '40px', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1rem' }}>
              <Monitor size={22} />
            </div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '0.5rem' }}>Full Parity Web & Desktop</h3>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
              Built with Tauri v2 wrapping the exact same production frontend API. Zero data divergence between web browsers and desktop installers.
            </p>
          </div>

          <div style={{ background: 'var(--bg-secondary)', padding: '1.5rem', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
            <div style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#34d399', width: '40px', height: '40px', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1rem' }}>
              <ShieldCheck size={22} />
            </div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '0.5rem' }}>India-First GST Compliance</h3>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
              Automated GSTR-1/2B/3B tax reconciliation, HSN/SAC code validation, and duplicate invoice detection built directly into cash workflows.
            </p>
          </div>

          <div style={{ background: 'var(--bg-secondary)', padding: '1.5rem', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
            <div style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#fcd34d', width: '40px', height: '40px', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1rem' }}>
              <Zap size={22} />
            </div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '0.5rem' }}>Instant Auto-Updates</h3>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
              Built-in Tauri auto-updater checks GitHub Releases automatically so desktop users always receive new updates without manual downloads.
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}
