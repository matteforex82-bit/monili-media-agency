import {Composition, CalculateMetadataFunction} from 'remotion';
import {ReelGrafica, ReelGraficaProps, CLOSING_SECONDS, FPS} from './ReelGrafica';

const defaultProps: ReelGraficaProps = {
  video: 'esempio.mp4',
  videoSeconds: 8,
  hook: 'Non sono semplici orecchini.',
  title: 'Orecchini smaltati a fiore',
  price: '39 €',
  place: 'Via Cavour 21, Ravenna',
  closing: true,
  titleFrom: 2.5,
};

const metadata: CalculateMetadataFunction<ReelGraficaProps> = ({props}) => ({
  durationInFrames: Math.max(1, Math.round((props.videoSeconds + (props.closing ? CLOSING_SECONDS : 0)) * FPS)),
});

export const Root = () => (
  <Composition
    id="ReelGrafica"
    component={ReelGrafica}
    width={1080}
    height={1920}
    fps={FPS}
    durationInFrames={Math.round((defaultProps.videoSeconds + CLOSING_SECONDS) * FPS)}
    defaultProps={defaultProps}
    calculateMetadata={metadata}
  />
);
