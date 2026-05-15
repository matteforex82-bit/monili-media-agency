'use client';

import { useState, useRef, useCallback } from 'react';

interface CarouselSlide {
  imageUrl: string;
  caption?: string;
  hashtags?: string;
  index: number;
}

interface CarouselWithTextOverlayProps {
  slides: CarouselSlide[];
  brand?: string;
}

export default function CarouselWithTextOverlay({ slides, brand = 'I Monili' }: CarouselWithTextOverlayProps) {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [showTextOverlay, setShowTextOverlay] = useState(true);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [downloadReady, setDownloadReady] = useState(false);

  const slide = slides[currentSlide];

  const generateImageWithOverlay = useCallback(async () => {
    if (!canvasRef.current || !slide) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    try {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = () => {
        canvas.width = img.width;
        canvas.height = img.height;

        ctx.drawImage(img, 0, 0);

        const padding = 30;
        const textY = canvas.height - padding - 80;

        if (slide.caption) {
          ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
          ctx.fillRect(padding, textY - 60, canvas.width - padding * 2, 70);

          ctx.fillStyle = '#FFFFFF';
          ctx.font = 'bold 24px DM Sans';
          ctx.textAlign = 'center';
          ctx.fillText(slide.caption, canvas.width / 2, textY - 30);

          if (slide.hashtags) {
            ctx.font = '16px DM Sans';
            ctx.fillStyle = '#FFD700';
            ctx.fillText(slide.hashtags, canvas.width / 2, textY);
          }
        }

        ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
        ctx.font = '14px DM Mono';
        ctx.textAlign = 'right';
        ctx.fillText(`${brand} · ${slide.index + 1}/${slides.length}`, canvas.width - padding, padding + 20);

        setDownloadReady(true);
      };
      img.src = slide.imageUrl;
    } catch (err) {
      console.error('Errore generazione overlay:', err);
    }
  }, [slide, slides.length, brand]);

  const handleDownload = useCallback(() => {
    if (!canvasRef.current) return;
    const link = document.createElement('a');
    link.href = canvasRef.current.toDataURL('image/jpeg', 0.95);
    link.download = `carousel-slide-${currentSlide + 1}.jpg`;
    link.click();
  }, [currentSlide]);

  return (
    <div style={{ marginTop: 20 }}>
      <div style={{ fontFamily: 'DM Sans', fontSize: 13, fontWeight: 700, color: 'var(--espresso)', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
        <input
          type="checkbox"
          checked={showTextOverlay}
          onChange={(e) => {
            setShowTextOverlay(e.target.checked);
            if (e.target.checked) {
              setTimeout(() => generateImageWithOverlay(), 100);
            }
          }}
          style={{ cursor: 'pointer' }}
        />
        Aggiungere testo direttamente nelle foto carousel?
      </div>

      {showTextOverlay && (
        <div style={{ border: '1px solid var(--border)', borderRadius: 12, padding: 16, background: 'var(--cream)' }}>
          {/* Canvas for overlay generation */}
          <canvas ref={canvasRef} style={{ display: 'none' }} />

          {/* Preview */}
          <div style={{ marginBottom: 16, borderRadius: 10, overflow: 'hidden', background: '#000' }}>
            {slide && (
              <div style={{ position: 'relative', paddingBottom: '100%', overflow: 'hidden' }}>
                <img
                  src={slide.imageUrl}
                  alt={`Carousel slide ${currentSlide + 1}`}
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: '100%',
                    objectFit: 'cover',
                  }}
                  onLoad={() => {
                    if (showTextOverlay) setTimeout(() => generateImageWithOverlay(), 100);
                  }}
                />
              </div>
            )}
          </div>

          {/* Slide navigation */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
            <button
              onClick={() => setCurrentSlide(Math.max(0, currentSlide - 1))}
              disabled={currentSlide === 0}
              style={{
                padding: '6px 12px',
                background: currentSlide === 0 ? 'var(--cream-3)' : 'var(--cream-2)',
                border: '1px solid var(--border)',
                borderRadius: 6,
                fontFamily: 'DM Sans',
                fontSize: 12,
                cursor: currentSlide === 0 ? 'not-allowed' : 'pointer',
                opacity: currentSlide === 0 ? 0.6 : 1,
              }}
            >
              ← Prev
            </button>
            <div style={{ fontFamily: 'DM Mono', fontSize: 12, color: 'var(--espresso-mid)', fontWeight: 600 }}>
              {currentSlide + 1} / {slides.length}
            </div>
            <button
              onClick={() => setCurrentSlide(Math.min(slides.length - 1, currentSlide + 1))}
              disabled={currentSlide === slides.length - 1}
              style={{
                padding: '6px 12px',
                background: currentSlide === slides.length - 1 ? 'var(--cream-3)' : 'var(--cream-2)',
                border: '1px solid var(--border)',
                borderRadius: 6,
                fontFamily: 'DM Sans',
                fontSize: 12,
                cursor: currentSlide === slides.length - 1 ? 'not-allowed' : 'pointer',
                opacity: currentSlide === slides.length - 1 ? 0.6 : 1,
              }}
            >
              Next →
            </button>
          </div>

          {/* Download button */}
          {downloadReady && (
            <button
              onClick={handleDownload}
              className="btn-mission"
              style={{
                width: '100%',
                padding: '10px 12px',
                fontSize: 13,
                fontWeight: 600,
              }}
            >
              ⬇ Scarica slide con testo
            </button>
          )}

          {!downloadReady && (
            <button
              onClick={generateImageWithOverlay}
              className="btn-secondary"
              style={{
                width: '100%',
                padding: '10px 12px',
                fontSize: 13,
              }}
            >
              Genera preview con testo
            </button>
          )}
        </div>
      )}
    </div>
  );
}
