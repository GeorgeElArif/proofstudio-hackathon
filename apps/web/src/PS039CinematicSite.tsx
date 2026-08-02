import { useEffect, useMemo, useRef, useState } from "react";
import type { CSSProperties } from "react";
import {
  PS039_PROOF_LAYERS,
  type ProofLayer,
} from "./ps039ProofLayers";

const PS039_ASSETS = {
  video: "/ps039/final-proof-object.mp4",
  sealedPoster: "/ps039/proof-object-sealed-poster.jpg",
  explodedFallback: "/ps039/proof-object-exploded-fallback.jpg",
} as const;

type Ps039CinematicSiteProps = {
  mode?: "landing" | "demo";
};

function useReducedMotionSetting() {
  const [reduced, setReduced] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const forced = params.get("reduced-motion") === "1";
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");

    const update = () => setReduced(forced || media.matches);
    update();
    media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, []);

  return reduced;
}

function useDesktopViewport() {
  const [isDesktop, setIsDesktop] = useState(false);

  useEffect(() => {
    const media = window.matchMedia("(min-width: 721px)");
    const update = () => setIsDesktop(media.matches);
    update();
    media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, []);

  return isDesktop;
}

function useMobileActiveLayers(enabled: boolean) {
  useEffect(() => {
    if (!enabled) return undefined;
    const cards = Array.from(document.querySelectorAll<HTMLElement>(".ps039-mobile-layer"));
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          entry.target.classList.toggle("is-active", entry.isIntersecting);
        });
      },
      { rootMargin: "-18% 0px -34% 0px", threshold: 0.15 },
    );
    cards.forEach((card) => observer.observe(card));
    return () => observer.disconnect();
  }, [enabled]);
}

function useScrollProgress(enabled: boolean) {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (!enabled) {
      setProgress(0);
      return undefined;
    }

    let active = true;
    let cleanup = () => undefined as void;

    void Promise.all([import("gsap"), import("gsap/ScrollTrigger")]).then(
      ([gsapModule, triggerModule]) => {
        if (!active) return;
        const gsap = gsapModule.gsap;
        const ScrollTrigger = triggerModule.ScrollTrigger;
        gsap.registerPlugin(ScrollTrigger);
        const media = gsap.matchMedia();

        media.add("(min-width: 721px)", () => {
          const trigger = ScrollTrigger.create({
            trigger: ".ps039-scroll-cinema",
            start: "top top",
            end: "bottom bottom",
            scrub: 0.45,
            onUpdate: (self) => setProgress(self.progress),
          });

          return () => trigger.kill();
        });

        cleanup = () => {
          media.revert();
          setProgress(0);
        };
      },
    );

    return () => {
      active = false;
      cleanup();
    };
  }, [enabled]);

  return progress;
}

function layerStyle(index: number, row = index): CSSProperties {
  return {
    "--layer-index": String(index),
    "--layer-row": String(row),
  } as CSSProperties;
}

function proofBeatForProgress(progress: number) {
  if (progress < 0.22) return "sealed";
  if (progress < 0.52) return "opening";
  if (progress < 0.78) return "exploded";
  return "room";
}

function StaticProofObject() {
  return (
    <div className="ps039-static-object" aria-hidden="true">
      <div className="ps039-static-object-shell">
        <span className="ps039-static-seal ps039-static-seal-top" />
        <span className="ps039-static-seal ps039-static-seal-bottom" />
        <span className="ps039-static-seal ps039-static-seal-left" />
        <span className="ps039-static-seal ps039-static-seal-right" />
      </div>
    </div>
  );
}

function ProofAssetPair({ eager = false }: { eager?: boolean }) {
  return (
    <div className="ps039-proof-asset-pair" aria-hidden="true">
      <img
        alt=""
        className="ps039-proof-asset ps039-proof-asset-sealed"
        decoding={eager ? "sync" : "async"}
        loading={eager ? "eager" : "lazy"}
        src={PS039_ASSETS.sealedPoster}
      />
      <img
        alt=""
        className="ps039-proof-asset ps039-proof-asset-exploded"
        decoding="async"
        loading={eager ? "eager" : "lazy"}
        src={PS039_ASSETS.explodedFallback}
      />
    </div>
  );
}

function LayerText({
  compact = false,
  layer,
}: {
  compact?: boolean;
  layer: ProofLayer;
}) {
  return (
    <>
      <span className="ps039-layer-label">{layer.label}</span>
      <strong>{layer.descriptor}</strong>
      {!compact && <span>{layer.body}</span>}
    </>
  );
}

function SiteHeader() {
  return (
    <header className="ps039-site-header">
      <span className="ps039-wordmark">PROOFSTUDIO</span>
      <nav aria-label="Public navigation">
        <a href="/judge-cockpit">Judge View</a>
        <a href="/live-proof.html">
          Verified Demo
        </a>
        <a href="/campaign-proof-room">Proof Room</a>
      </nav>
    </header>
  );
}

function MobileLayerUnfolding({ reducedMotion }: { reducedMotion: boolean }) {
  useMobileActiveLayers(!reducedMotion);

  return (
    <section className="ps039-mobile-story" aria-label="Recorded proof layers">
      <div className="ps039-mobile-layers">
        {PS039_PROOF_LAYERS.map((layer, index) => (
          <article
            className={`ps039-mobile-layer ${layer.accent === "archive-orange" ? "is-archive" : ""}`}
            key={layer.id}
            style={layerStyle(index)}
          >
            <LayerText compact layer={layer} />
          </article>
        ))}
      </div>
    </section>
  );
}

function ReducedMotionStory() {
  return (
    <section className="ps039-reduced-story" aria-label="Static proof story">
      <div className="ps039-reduced-visual">
        <ProofAssetPair eager />
      </div>
      <div className="ps039-reduced-grid">
        {PS039_PROOF_LAYERS.map((layer) => (
          <article className="ps039-reduced-layer" key={layer.id}>
            <LayerText compact layer={layer} />
          </article>
        ))}
      </div>
    </section>
  );
}

function DesktopLayerLabels({ progress }: { progress: number }) {
  const visible = progress > 0.62 && progress < 0.88;
  const activeIndex = Math.min(
    PS039_PROOF_LAYERS.length - 1,
    Math.max(0, Math.floor((progress - 0.62) * 20)),
  );

  return (
    <div className={`ps039-layer-orbit ${visible ? "is-visible" : ""}`} aria-label="Visible proof layers">
      {PS039_PROOF_LAYERS.map((layer, index) => (
        <article
          className={[
            "ps039-layer-callout",
            index % 2 === 0 ? "is-left" : "is-right",
            index === activeIndex ? "is-active" : "",
            layer.accent === "archive-orange" ? "is-archive" : "",
          ]
            .filter(Boolean)
            .join(" ")}
          key={layer.id}
          style={layerStyle(index, index)}
        >
          <LayerText compact layer={layer} />
        </article>
      ))}
    </div>
  );
}

function SceneCopy({ progress, reducedMotion }: { progress: number; reducedMotion: boolean }) {
  const scene =
    reducedMotion || progress < 0.22
      ? "record"
      : progress < 0.42
        ? "seal"
        : progress < 0.66
          ? "opening"
          : "layers";

  return (
    <div className="ps039-scene-copy" data-scene={scene}>
      {/* PS-042C4: the landing fold stays useful before any media loads. */}
      <div className="ps039-scene-panel ps039-scene-record" aria-hidden={scene !== "record"}>
        <span className="ps039-kicker ps039-hero-eyebrow">AI media provenance</span>
        <h1>
          When AI work goes public,
          <br />
          the record has to stand up.
        </h1>
        <p>Inspect how an AI media run was created, stored, and verified.</p>
        <div className="ps039-hero-actions">
          <a
            className="ps039-button ps039-button-primary"
            href="/live-proof.html"
          >
            View the verified demo
          </a>
          <a className="ps039-button" href="#how-it-works">
            How it works
          </a>
        </div>
      </div>
      <div className="ps039-scene-panel ps039-scene-seal" aria-hidden={scene !== "seal"}>
        <h2>
          Not ‘trust us.’
          <br />
          Show the record.
        </h2>
      </div>
      <div className="ps039-scene-panel ps039-scene-opening" aria-hidden={scene !== "opening"}>
        <h2>
          The record opens.
          <br />
          Layer by layer.
        </h2>
      </div>
      <div className="ps039-scene-panel ps039-scene-layers" aria-hidden={scene !== "layers"}>
        <h2>
          Eight recorded layers.
          <br />
          One inspectable record.
        </h2>
      </div>
    </div>
  );
}

function HeroAssetStage({
  demoPlaying,
  isDemo,
  isDesktop,
  progress,
  reducedMotion,
}: {
  demoPlaying: boolean;
  isDemo: boolean;
  isDesktop: boolean;
  progress: number;
  reducedMotion: boolean;
}) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const scrubFrameRef = useRef<number | null>(null);
  const targetTimeRef = useRef(0);
  const [videoError, setVideoError] = useState(false);
  const [metadataLoaded, setMetadataLoaded] = useState(false);
  const canUseVideo = isDesktop && !reducedMotion && !videoError;
  const canRunDemoVideo = canUseVideo && isDemo && demoPlaying;
  const showProceduralFallback = isDesktop && !reducedMotion && videoError;
  const beat = proofBeatForProgress(progress);

  useEffect(() => {
    const video = videoRef.current;
    if (!video || !canUseVideo) return;

    if (canRunDemoVideo) {
      void video.play().catch(() => undefined);
    } else {
      video.pause();
    }
  }, [canRunDemoVideo, canUseVideo]);

  useEffect(() => {
    if (isDemo || !canUseVideo || !metadataLoaded) return undefined;
    const video = videoRef.current;
    if (!video || !Number.isFinite(video.duration) || video.duration <= 0) return undefined;

    const duration = video.duration;
    const clampedProgress = Math.max(0, Math.min(1, progress));
    targetTimeRef.current = Math.max(0, Math.min(duration, clampedProgress * duration));

    if (scrubFrameRef.current === null) {
      scrubFrameRef.current = window.requestAnimationFrame(() => {
        scrubFrameRef.current = null;
        video.pause();
        const targetTime = Math.max(0, Math.min(video.duration, targetTimeRef.current));
        if (Math.abs(video.currentTime - targetTime) > 0.03) {
          video.currentTime = targetTime;
        }
      });
    }

    return undefined;
  }, [canUseVideo, isDemo, metadataLoaded, progress]);

  useEffect(() => {
    return () => {
      if (scrubFrameRef.current !== null) {
        window.cancelAnimationFrame(scrubFrameRef.current);
      }
    };
  }, []);

  useEffect(() => {
    const video = videoRef.current;
    if (!video || !isDemo || !Number.isFinite(video.duration) || video.duration <= 0) return;
    if (!demoPlaying) video.currentTime = Math.min(video.duration - 0.1, progress * video.duration);
  }, [demoPlaying, isDemo, progress]);

  return (
    <div className="ps039-hero-stage" data-proof-beat={beat}>
      <div className="ps039-hero-media" aria-label="Cinematic Proof Object">
        <img
          alt="Sealed Proof Object cinematic poster"
          className="ps039-hero-poster"
          decoding="sync"
          loading="eager"
          src={PS039_ASSETS.sealedPoster}
        />
        {canUseVideo && (
          <video
            aria-hidden="true"
            className="ps039-hero-video"
            muted
            onLoadedMetadata={() => {
              setMetadataLoaded(true);
              const video = videoRef.current;
              if (video && !isDemo) {
                video.pause();
                video.currentTime = 0;
              }
            }}
            onError={() => setVideoError(true)}
            playsInline
            poster={PS039_ASSETS.sealedPoster}
            preload="none"
            ref={videoRef}
            src={PS039_ASSETS.video}
          />
        )}
        {!canUseVideo && (
          <img
            alt=""
            className="ps039-hero-exploded-fallback"
            decoding="async"
            loading="eager"
            src={PS039_ASSETS.explodedFallback}
          />
        )}
        <div className="ps039-video-vignette" aria-hidden="true" />
      </div>

      <ol className="ps039-object-explanation" aria-label="Proof Object stages">
        <li>Generate</li>
        <li>Archive</li>
        <li>Rehydrate</li>
        <li>Verify</li>
      </ol>

      {showProceduralFallback && (
        <div className="ps039-canvas-wrap" aria-hidden="true">
          <StaticProofObject />
        </div>
      )}
      {isDesktop && !reducedMotion && <DesktopLayerLabels progress={progress} />}
    </div>
  );
}

function HomeProofFlow() {
  const stages = [
    ["01", "Generate", "The run records its creation path."],
    ["02", "Archive", "Evidence is stored with its manifest."],
    ["03", "Rehydrate", "The record returns without a provider call."],
    ["04", "Verify", "Hashes and access boundaries are checked."],
  ] as const;

  return (
    <section className="ps039-home-proof-flow" id="how-it-works">
      <div className="ps039-section-copy">
        <span className="ps039-kicker">Proof flow</span>
        <h2>Four steps. One inspectable record.</h2>
      </div>
      <ol aria-label="How ProofStudio works">
        {stages.map(([number, title, body]) => (
          <li key={number}>
            <span>{number}</span>
            <strong>{title}</strong>
            <p>{body}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}

function CampaignRoomPreview() {
  const recordGroups = [
    {
      label: "Origin",
      layers: ["PROMPT", "PROVIDER · MODEL"],
    },
    {
      label: "Record",
      layers: ["B2 ARCHIVE", "GENBLAZE MANIFEST", "REHYDRATE CHECK"],
    },
    {
      label: "Decision",
      layers: ["REVIEW DECISION", "PROVENANCE PASSPORT"],
    },
    {
      label: "Export",
      layers: ["EXPORT PACK"],
    },
  ];

  return (
    <section className="ps039-room-preview" id="campaign-proof-room-preview">
      <div className="ps039-section-copy">
        <span className="ps039-kicker">Campaign Proof Room</span>
        <h2>The record, assembled.</h2>
        <p>
          Prompt, model, archive reference, manifest, check, decision, passport, and export —
          arranged as one inspectable record.
        </p>
      </div>
      <div className="ps039-room-surface" aria-label="Campaign Proof Room preview">
        <div className="ps039-room-header">
          <span>CAMPAIGN PROOF ROOM</span>
          <span>ONE ACCEPTED RECORD</span>
        </div>
        <div className="ps039-room-focus">
          <span>Open the record.</span>
          <strong>Campaign Proof Room</strong>
          <p>ProofStudio shows what the accepted AI media pipeline recorded.</p>
        </div>
        <div className="ps039-room-record-map">
          {recordGroups.map((group) => (
            <section className="ps039-room-record-group" key={group.label}>
              <span>{group.label}</span>
              <div>
                {group.layers.map((layer) => (
                  <i className={layer === "B2 ARCHIVE" ? "is-archive" : ""} key={layer}>
                    {layer}
                  </i>
                ))}
              </div>
            </section>
          ))}
        </div>
      </div>
    </section>
  );
}

function TruthBoundarySection() {
  return (
    <section className="ps039-truth-boundary" id="truth-boundary">
      <span className="ps039-kicker">Truth Boundary</span>
      <h2>
        Proof is not truth.
        <br />
        Proof is the record.
      </h2>
      <p>
        ProofStudio does not prove that media is true, legal, authentic, or human-made. It shows
        what the accepted AI media pipeline recorded.
      </p>
    </section>
  );
}

function FinalCta({ demoMode }: { demoMode: boolean }) {
  return (
    <section className="ps039-final-cta" id="see-the-proof">
      <h2>
        See the campaign record in one place.
      </h2>
      <a className="ps039-button" href={demoMode ? "/" : "/campaign-proof-room"}>
        {demoMode ? "Return to Website" : "View the Campaign Proof Room"}
      </a>
    </section>
  );
}

function DemoControls({
  playing,
  progress,
  reducedMotion,
  onPlayToggle,
  onProgressChange,
}: {
  playing: boolean;
  progress: number;
  reducedMotion: boolean;
  onPlayToggle: () => void;
  onProgressChange: (value: number) => void;
}) {
  return (
    <section className="ps039-demo-controls" aria-label="Demo mode controls">
      <div>
        <span className="ps039-kicker">DEMO MODE</span>
        <h2>Judge demo playback</h2>
      </div>
      <div className="ps039-demo-actions">
        <button
          className="ps039-button ps039-button-primary"
          disabled={reducedMotion}
          type="button"
          onClick={onPlayToggle}
        >
          {reducedMotion ? "Playback disabled" : playing ? "Pause" : "Play"}
        </button>
        <label>
          <span>Story position</span>
          <input
            aria-label="Story position"
            disabled={reducedMotion}
            max="100"
            min="0"
            onChange={(event) => onProgressChange(Number(event.target.value) / 100)}
            type="range"
            value={Math.round(progress * 100)}
          />
        </label>
      </div>
    </section>
  );
}

export function PS039CinematicSite({ mode = "landing" }: Ps039CinematicSiteProps) {
  const reducedMotion = useReducedMotionSetting();
  const isDesktop = useDesktopViewport();
  const scrollProgress = useScrollProgress(mode === "landing" && !reducedMotion);
  const [demoPlaying, setDemoPlaying] = useState(false);
  const [demoProgress, setDemoProgress] = useState(0);
  const isDemo = mode === "demo";
  const progress = isDemo ? demoProgress : scrollProgress;
  const splitFocus = !reducedMotion && progress > 0.22 && progress < 0.82;
  const pageClass = useMemo(
    () =>
      [
        "ps039-cinematic",
        reducedMotion ? "is-reduced-motion" : "",
        isDemo ? "is-demo-mode" : "",
        splitFocus ? "is-proof-split" : "",
      ]
        .filter(Boolean)
        .join(" "),
    [isDemo, reducedMotion, splitFocus],
  );

  useEffect(() => {
    if (!isDemo || !demoPlaying || reducedMotion) return undefined;
    const interval = window.setInterval(() => {
      setDemoProgress((current) => (current >= 1 ? 0 : Math.min(1, current + 0.012)));
    }, 90);
    return () => window.clearInterval(interval);
  }, [demoPlaying, isDemo, reducedMotion]);

  useEffect(() => {
    if (reducedMotion) setDemoPlaying(false);
  }, [reducedMotion]);

  return (
    <main className={pageClass}>
      <SiteHeader />

      {isDemo && (
        <DemoControls
          playing={demoPlaying}
          progress={demoProgress}
          reducedMotion={reducedMotion}
          onPlayToggle={() => setDemoPlaying((current) => !current)}
          onProgressChange={setDemoProgress}
        />
      )}

      <section
        className={`ps039-scroll-cinema ${isDemo ? "ps039-demo-cinema" : "ps039-landing-cinema"}`}
        aria-label="Scroll-open Proof Object story"
      >
        <section className="ps039-hero" id="cinematic-proof-object">
          <SceneCopy progress={progress} reducedMotion={reducedMotion} />
          <HeroAssetStage
            demoPlaying={demoPlaying}
            isDemo={isDemo}
            isDesktop={isDesktop}
            progress={progress}
            reducedMotion={reducedMotion}
          />
        </section>

        {isDemo && !reducedMotion && (
          <>
            <section className="ps039-scroll-chapter" data-screenshot="desktop-seal" aria-hidden="true" />
            <section className="ps039-scroll-chapter" data-screenshot="desktop-opening" aria-hidden="true" />
            <section className="ps039-scroll-chapter" data-screenshot="desktop-proof-layers" aria-hidden="true" />
            <section className="ps039-scroll-chapter" data-screenshot="desktop-room" aria-hidden="true" />
          </>
        )}
      </section>

      {isDemo ? (
        reducedMotion ? <ReducedMotionStory /> : <MobileLayerUnfolding reducedMotion={false} />
      ) : (
        <HomeProofFlow />
      )}

      <TruthBoundarySection />
      <CampaignRoomPreview />
      <FinalCta demoMode={isDemo} />

      <footer className="ps039-footer">
        ProofStudio does not prove that media is true, legal, authentic, or human-made. It shows
        what the accepted AI media pipeline recorded.
      </footer>
    </main>
  );
}
