'use client';

import { useEffect, useRef, useState, type FormEvent } from 'react';
import { ArrowRight, Check, Clapperboard, Film, FileText, ImagePlus } from 'lucide-react';
import { API_URL } from '@/lib/apiUrl';
import FileDropzone from '@/components/FileDropzone';
import ReelSeedancePrompts from '@/components/ReelSeedancePrompts';
import ReelBlenderScene, { type SceneFile } from '@/components/ReelBlenderScene';
import { ReelBlenderPilot, useReelBlenderRender } from '@/components/ReelBlenderRender';
import ReelBlenderReview, { type BlenderPreview } from '@/components/ReelBlenderReview';

interface Brief {
  product: string;
  brief: string;
  target_seconds: number;
  scheda_run_id: string;
}

interface Concept {
  title: string;
  hook: string;
  sequence: string;
  risk: string;
}

interface Package {
  storyboard: string;
  assets: string;
  audio: string;
  blender: string;
  higgsfield: string;
  pilot_shot_index?: number;
  direction?: { set_design: string; continuity: string; music_bpm: number; music_feel: string };
  shots?: {
    end_ms: number;
    framing: string;
    camera: string;
    lighting: string;
    action: string;
    cut: string;
    design?: { purpose: string; sound: string };
  }[];
}

interface ReferencePhoto {
  id: string;
  filename: string;
}

const MAX_PHOTOS = 3;
const elapsedSeconds = new Intl.NumberFormat('it-IT', { maximumFractionDigits: 2 });

interface Draft extends Brief {
  id: string;
  version: number;
  updated_at: string;
  photos?: ReferencePhoto[];
  concepts?: Concept[];
  recommended?: number;
  recommendation_reason?: string;
  selected?: number | null;
  package?: Package | null;
  package_revision?: string;
  scene?: SceneFile | null;
  previews?: BlenderPreview[];
}

interface Props {
  product?: string;
  pieceId: string;
  initialBrief: string;
}

const STEPS = [
  { title: 'Foto e brief', short: 'Foto e brief', icon: ImagePlus },
  { title: 'Regia del Reel', short: 'Regia', icon: FileText },
  { title: 'Scena Blender', short: 'Blender', icon: Clapperboard },
  { title: 'Prova Seedance', short: 'Seedance', icon: Film },
];

function fieldsFor(draft: Brief): Brief {
  return { product: draft.product, brief: draft.brief, target_seconds: draft.target_seconds, scheda_run_id: draft.scheda_run_id };
}

function rememberDraft(id: string) {
  const url = new URL(window.location.href);
  if (id) url.searchParams.set('bozza', id);
  else url.searchParams.delete('bozza');
  window.history.replaceState(null, '', url);
}

export default function ReelBlenderBrief({ product, pieceId, initialBrief }: Props) {
  const [drafts, setDrafts] = useState<Draft[]>([]);
  const [selected, setSelected] = useState('');
  const [fields, setFields] = useState<Brief | null>(null);
  const [busy, setBusy] = useState('');
  const [error, setError] = useState('');
  const [listError, setListError] = useState(false);
  const [listLoading, setListLoading] = useState(true);
  const [listAttempt, setListAttempt] = useState(0);
  const [newPhotos, setNewPhotos] = useState<File[]>([]);
  const [removedPhotos, setRemovedPhotos] = useState<string[]>([]);
  const [reviewTarget, setReviewTarget] = useState<{ id: string; count: number }>();
  const [requestedStep, setRequestedStep] = useState<number>();
  const heading = useRef<HTMLHeadingElement>(null);
  const restoredDraft = useRef(false);
  const active = drafts.find((draft) => draft.id === selected);
  const values = fields ?? { product: product ?? '', brief: initialBrief, target_seconds: 12, scheda_run_id: pieceId };
  const keptPhotos = (active?.photos ?? []).filter((photo) => !removedPhotos.includes(photo.id));
  const isSaved = !!active && !newPhotos.length && !removedPhotos.length && values.product === active.product &&
    values.brief === active.brief && values.target_seconds === active.target_seconds && values.scheda_run_id === active.scheda_run_id;
  const plan = isSaved ? active.package : null;
  const scene = plan ? active?.scene : null;
  const draftUrl = active ? `${API_URL}/reel-blender/drafts/${encodeURIComponent(active.id)}` : '';
  const renderUrl = scene ? `${draftUrl}/scene/${encodeURIComponent(scene.id)}/render` : '';
  const render = useReelBlenderRender(renderUrl);
  const shotNames = plan?.shots?.map((shot) => shot.framing) ?? [];
  const previews = active?.previews ?? [];
  const hasCurrentReview = !!plan && previews.some((item) => item.package_revision === active?.package_revision);
  const nextStep = !isSaved ? 0 : !plan || !scene ? (hasCurrentReview ? 3 : 1) :
    render.fileBase || hasCurrentReview ? 3 : 2;
  const allowedStep = plan ? 3 : isSaved ? 1 : 0;
  const step = requestedStep !== undefined && requestedStep <= allowedStep ? requestedStep : nextStep;
  const complete = [isSaved, !!plan, !!render.fileBase, !!plan && previews.some((item) =>
    item.package_revision === active?.package_revision && !!item.higgsfield_results?.length)];

  useEffect(() => {
    const controller = new AbortController();
    setListLoading(true);
    setListError(false);
    fetch(`${API_URL}/reel-blender/drafts`, { cache: 'no-store', signal: controller.signal })
      .then(async (res) => {
        if (!res.ok) throw new Error();
        const data: { items: Draft[] } = await res.json();
        if (controller.signal.aborted) return;
        setDrafts((items) => [...items, ...data.items.filter((draft) => !items.some((item) => item.id === draft.id))]);
        if (!restoredDraft.current) {
          restoredDraft.current = true;
          const opened = new URLSearchParams(window.location.search).get('bozza');
          const match = data.items.find((item) => item.id === opened);
          if (match) {
            setSelected(match.id);
            setFields(fieldsFor(match));
          }
        }
      })
      .catch(() => {
        if (!controller.signal.aborted) setListError(true);
      })
      .finally(() => {
        if (!controller.signal.aborted) setListLoading(false);
      });
    return () => controller.abort();
  }, [listAttempt]);

  function go(stepIndex: number) {
    setRequestedStep(stepIndex);
    requestAnimationFrame(() => heading.current?.focus());
  }

  function selectDraft(id: string) {
    const draft = drafts.find((item) => item.id === id);
    setSelected(id);
    rememberDraft(id);
    setRequestedStep(undefined);
    setReviewTarget(undefined);
    setNewPhotos([]);
    setRemovedPhotos([]);
    setFields(draft ? fieldsFor(draft) : null);
    setError('');
  }

  function updateDraft(value: unknown) {
    const draft = value as Draft;
    setDrafts((items) => [draft, ...items.filter((item) => item.id !== draft.id)]);
  }

  async function saveDraft() {
    const form = new FormData();
    for (const [key, value] of Object.entries(values)) form.append(key, String(value));
    if (active) {
      form.append('draft_id', active.id);
      form.append('expected_updated_at', active.updated_at);
    }
    for (const photo of keptPhotos) form.append('keep_photo_ids', photo.id);
    for (const photo of newPhotos) form.append('photos', photo);
    const response = await fetch(`${API_URL}/reel-blender/drafts/with-photos`, { method: 'POST', body: form });
    const draft = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(draft.error || 'Non riesco a salvare il brief. Riprova.');
    updateDraft(draft);
    setSelected(draft.id);
    rememberDraft(draft.id);
    setNewPhotos([]);
    setRemovedPhotos([]);
    setFields(fieldsFor(draft));
    return draft as Draft;
  }

  async function requestPlan(id: string, stage: 'concepts' | 'package', index?: number, refreshDirection = false): Promise<Draft> {
    const response = await fetch(`${API_URL}/reel-blender/drafts/${encodeURIComponent(id)}/${stage}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: index === undefined ? undefined : JSON.stringify({ index, refresh_direction: refreshDirection }),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || 'Non riesco a preparare la regia. Riprova.');
    updateDraft(data);
    return data;
  }

  async function createPlan(draft: Draft, refreshDirection = false) {
    setBusy('Sto preparando la regia…');
    const concepts = draft.concepts?.length ? draft : await requestPlan(draft.id, 'concepts');
    const index = refreshDirection ? (concepts.selected ?? concepts.recommended) : concepts.recommended;
    if (index === undefined || !concepts.concepts?.[index]) throw new Error('Manca la proposta di regia. Salva il brief e riprova.');
    await requestPlan(concepts.id, 'package', index, refreshDirection);
  }

  async function submitBrief(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy) return;
    const submitter = (event.nativeEvent as SubmitEvent).submitter;
    const saveOnly = submitter instanceof HTMLButtonElement && submitter.value === 'save';
    setError('');
    if (!values.product.trim()) {
      setError('Scrivi il nome del prodotto.');
      return;
    }
    if (!Number.isInteger(values.target_seconds) || values.target_seconds < 10 || values.target_seconds > 20) {
      setError('Scegli una durata intera da 10 a 20 secondi.');
      return;
    }
    setBusy('Salvo il brief…');
    try {
      const draft = isSaved ? active : await saveDraft();
      go(1);
      if (!saveOnly && !draft.package) await createPlan(draft);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Non riesco a continuare. Riprova.');
    } finally {
      setBusy('');
    }
  }

  async function refreshPlan() {
    if (!active || !isSaved || busy) return;
    setError('');
    try {
      await createPlan(active, !!plan);
      if (plan) setReviewTarget(undefined);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Non riesco a preparare la regia. Riprova.');
    } finally {
      setBusy('');
    }
  }

  async function download(format: 'md' | 'json') {
    if (!plan || !active) return;
    setError('');
    try {
      let blob: Blob;
      if (format === 'md') {
        const response = await fetch(draftUrl + '/package.md', { cache: 'no-store' });
        if (!response.ok) throw new Error('Non riesco a scaricare il copione. Riprova.');
        blob = await response.blob();
      } else {
        blob = new Blob([JSON.stringify(active, null, 2)], { type: 'application/json' });
      }
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `reel-blender-${active.id}.${format}`;
      document.body.append(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Non riesco a scaricare il copione. Riprova.');
    }
  }

  function reviewRenderedShot(value: unknown, previewId: string) {
    updateDraft(value);
    setReviewTarget((target) => ({ id: previewId, count: (target?.count ?? 0) + 1 }));
    go(3);
  }

  const concept = active?.selected != null ? active.concepts?.[active.selected] : undefined;
  const photoUrl = (id: string) => `${draftUrl}/photos/${encodeURIComponent(id)}`;

  return (
    <section className="rb-workspace" aria-labelledby="reel-blender-title">
      <header className="rb-header">
        <h1 id="reel-blender-title">Reel Blender</h1>
        {drafts.length > 0 && (
          <label className="rb-project">
            <span>Progetto</span>
            <select className="rs-input" value={selected} disabled={!!busy} onChange={(event) => selectDraft(event.target.value)}>
              <option value="">Nuovo Reel</option>
              {drafts.map((draft) => <option key={draft.id} value={draft.id}>{draft.product}</option>)}
            </select>
          </label>
        )}
      </header>
      {listError ? (
        <div className="rb-actions"><span role="alert">Le bozze non si sono caricate.</span>
          <button className="btn-secondary" type="button" onClick={() => setListAttempt((attempt) => attempt + 1)}>Riprova</button>
        </div>
      ) : listLoading ? <p className="rb-muted" role="status">Cerco le bozze salvate…</p> : null}

      <nav className="rb-steps" aria-label="Fasi di Reel Blender">
        <ol>
          {STEPS.map(({ short, icon: Icon }, index) => {
            const current = index === step;
            const finished = complete[index];
            const contents = <><span className="rb-step-mark">
              {finished && !current ? <Check size={16} aria-hidden="true" /> : <Icon size={17} strokeWidth={1.5} aria-hidden="true" />}
            </span><span>{short}</span>{finished && !current && <span className="sr-only">, completata</span>}</>;
            return (
              <li key={short} data-current={current || undefined} data-complete={finished || undefined}>
                {current || index > allowedStep ? (
                  <span className="rb-step" aria-current={current ? 'step' : undefined}>{contents}</span>
                ) : (
                  <button className="rb-step" type="button" disabled={!!busy} onClick={() => go(index)}>{contents}</button>
                )}
              </li>
            );
          })}
        </ol>
      </nav>

      <section className="rb-panel" aria-labelledby="rb-step-title" aria-busy={!!busy || undefined}>
        <h2 id="rb-step-title" ref={heading} tabIndex={-1}>{STEPS[step].title}</h2>
        {busy && <p className="rb-progress" role="status">{busy}</p>}
        {error && <p className="rs-error" role="alert">{error}</p>}

        {step === 0 && (
          <form onSubmit={submitBrief} className="rb-stack" noValidate>
            <div className="rb-brief-grid">
              <div className="rb-stack">
                <label className="rs-field rb-field">
                  <span>Prodotto</span>
                  <input className="rs-input" value={values.product} onChange={(event) => setFields({ ...values, product: event.target.value })}
                    maxLength={120} required disabled={!!busy} placeholder="Es. Giacca ricamata" />
                </label>
                <label className="rs-field rb-field">
                  <span>Cosa vuoi mostrare? <small>Facoltativo</small></span>
                  <textarea className="rs-input" value={values.brief} onChange={(event) => setFields({ ...values, brief: event.target.value })}
                    maxLength={1500} rows={2} disabled={!!busy} placeholder="Es. Il ricamo e come veste la giacca" />
                </label>
              </div>
              <fieldset disabled={!!busy} className="rb-photos">
                <legend>Foto di riferimento <small>Facoltative</small></legend>
                {keptPhotos.length > 0 && (
                  <div className="rb-thumbs">
                    {keptPhotos.map((photo) => (
                      <div key={photo.id}>
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img src={photoUrl(photo.id)} alt={photo.filename} />
                        <button type="button" className="rb-text-button" aria-label={`Togli ${photo.filename}`}
                          onClick={() => setRemovedPhotos((items) => [...items, photo.id])}>Togli</button>
                      </div>
                    ))}
                  </div>
                )}
                {keptPhotos.length < MAX_PHOTOS && (
                  <FileDropzone files={newPhotos} onFiles={(files) => { if (!busy) setNewPhotos(files); }}
                    accept="image/jpeg,image/png,image/webp,image/heic,image/heif,.heic,.heif"
                    max={MAX_PHOTOS - keptPhotos.length} kind="photo" title="Aggiungi foto"
                    hint="Fino a 3 foto · frontale, tre quarti o dettaglio" />
                )}
                {values.scheda_run_id && (
                  <p className="rb-muted">{keptPhotos.length || newPhotos.length ? 'Collegato a una Scheda pezzo.' :
                    'Se disponibile, lo Studio usa la foto della Scheda pezzo.'}{' '}
                    <button className="rb-text-button" type="button" onClick={() => setFields({ ...values, scheda_run_id: '' })}>Scollega</button>
                  </p>
                )}
              </fieldset>
            </div>
            {!isSaved && active?.package && (
              <p className="rb-muted">Salvando le modifiche al brief dovrai preparare di nuovo la regia e la scena.</p>
            )}
            <div className="rb-actions">
              <button className="btn-mission" type="submit" disabled={!!busy}>
                {busy || (plan ? 'Vai alla regia' : 'Prepara la regia')} <ArrowRight size={17} strokeWidth={1.5} aria-hidden="true" />
              </button>
              {!isSaved && <button className="rb-text-button" type="submit" value="save" disabled={!!busy}>Salva bozza</button>}
            </div>
            <details className="rb-details rb-inline-details">
              <summary>Durata del Reel · {Number.isFinite(values.target_seconds) ? `${values.target_seconds} s` : 'da impostare'}</summary>
              <label className="rs-field rb-field">
                <span>Secondi (da 10 a 20)</span>
                <input className="rs-input rb-duration" type="number" min={10} max={20}
                  value={Number.isFinite(values.target_seconds) ? values.target_seconds : ''}
                  onChange={(event) => setFields({ ...values, target_seconds: event.target.valueAsNumber })} required disabled={!!busy} />
              </label>
            </details>
          </form>
        )}

        {step === 1 && active && (
          plan ? (
            <div className="rb-stack">
              <div className="rb-direction-grid">
                <div className="rb-stack">
                  {concept && <h3 className="rb-concept">{concept.title}</h3>}
                  <p>{plan.storyboard}</p>
                  {active.selected === active.recommended && active.recommendation_reason && <p className="rb-muted">{active.recommendation_reason}</p>}
                </div>
                {keptPhotos.length > 0 && (
                  <div className="rb-direction-photos" aria-label="Foto di riferimento">
                    {keptPhotos.map((photo) => (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img key={photo.id} src={photoUrl(photo.id)} alt={photo.filename} />
                    ))}
                  </div>
                )}
              </div>
              <details className="rb-details">
                <summary>Foto da usare o preparare</summary>
                <p className="rb-preline">{plan.assets}</p>
              </details>
              <details className="rb-details">
                <summary>Inquadrature, luce e musica</summary>
                {plan.direction && <p>{plan.direction.set_design} · {plan.direction.music_bpm} BPM</p>}
                {plan.direction?.continuity && <p className="rb-muted">{plan.direction.continuity}</p>}
                {plan.audio && <p>{plan.audio}</p>}
                <ol className="rb-shotlist">
                  {plan.shots?.map((shot, index, shots) => (
                    <li key={shot.end_ms}>
                      <strong>{shot.framing}</strong>
                      <span className="rb-meta">{elapsedSeconds.format((shots[index - 1]?.end_ms ?? 0) / 1000)}–{elapsedSeconds.format(shot.end_ms / 1000)} s</span>
                      <p>{shot.camera} · {shot.lighting} · {shot.action}</p>
                      <p className="rb-muted">{shot.cut}{shot.design?.sound && ` · ${shot.design.sound}`}</p>
                    </li>
                  ))}
                </ol>
              </details>
              <div className="rb-actions">
                <button className="btn-mission" type="button" disabled={!!busy} onClick={() => go(2)}>
                  Vai a Blender <ArrowRight size={17} strokeWidth={1.5} aria-hidden="true" />
                </button>
              </div>
              <details className="rb-details">
                <summary>Prompt, download e aggiornamento della regia</summary>
                <ReelSeedancePrompts draftId={active.id} revision={active.package_revision} />
                <div className="rb-actions">
                  <button className="btn-secondary" type="button" disabled={!!busy} onClick={() => void download('md')}>Scarica copione</button>
                  <button className="btn-secondary" type="button" disabled={!!busy} onClick={() => void download('json')}>Scarica JSON</button>
                  <button className="btn-secondary" type="button" disabled={!!busy} onClick={() => void refreshPlan()}>Aggiorna la regia</button>
                </div>
                {scene && <p className="rb-muted">Se aggiorni la regia, dovrai creare una nuova scena Blender.</p>}
              </details>
            </div>
          ) : (
            <div className="rb-stack">
              <p className="rb-muted">Il brief di «{active.product}» è salvato. Lo Studio sceglie le inquadrature, la luce e il ritmo.</p>
              <div className="rb-actions">
                <button className="btn-mission" type="button" disabled={!!busy} onClick={() => void refreshPlan()}>
                  {busy || 'Prepara la regia'}
                </button>
              </div>
            </div>
          )
        )}

        {step === 2 && plan && active && (
          <ReelBlenderScene key={active.id} draftId={active.id} scene={scene} job={render}
            musicBpm={plan.direction?.music_bpm ?? 100} disabled={!!busy}
            onUpdate={updateDraft} onContinue={() => go(3)} />
        )}

        {step === 3 && plan && active && (
          <div className="rb-stack">
            {!hasCurrentReview && render.fileBase && (
              <div className="rb-test-grid">
                <div className="rb-stack">
                  <p className="rb-muted">Il render è pronto. Rivedi una sola ripresa prima di generarla in Seedance.</p>
                  <ReelBlenderPilot key={render.fileBase} job={render} shotNames={shotNames} pilotShot={plan.pilot_shot_index}
                    disabled={!!busy} onReview={reviewRenderedShot} />
                </div>
                <figure className="rb-test-film">
                  <video src={render.fileBase + '/video'} controls playsInline preload="auto" crossOrigin="use-credentials"
                    aria-label="Montaggio Blender con musica" />
                  <figcaption>Montaggio Blender · {active.target_seconds} s</figcaption>
                </figure>
              </div>
            )}
            {!render.fileBase && !hasCurrentReview && (
              <div className="rb-stack">
                <p className="rb-muted">Per iniziare, renderizza la scena Blender o carica una ripresa che hai già esportato.</p>
                <div className="rb-actions"><button type="button" className="btn-mission" onClick={() => go(2)}>Vai al render Blender</button></div>
              </div>
            )}
            <ReelBlenderReview key={`${active.id}-${reviewTarget?.count ?? 0}`} draftId={active.id}
              revision={active.package_revision} previews={previews} shotNames={shotNames}
              initialSelected={reviewTarget?.id} disabled={!!busy} onUpdate={updateDraft}
              extra={hasCurrentReview && render.fileBase ? (
                <ReelBlenderPilot key={render.fileBase} job={render} shotNames={shotNames} pilotShot={plan.pilot_shot_index}
                  disabled={!!busy} onReview={reviewRenderedShot} />
              ) : null} />
          </div>
        )}
      </section>
    </section>
  );
}
