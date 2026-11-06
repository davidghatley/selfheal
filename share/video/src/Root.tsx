import React from 'react';
import {Composition, Still} from 'remotion';
import {SelfHealV, SelfHealSquare, FRAMES} from './SelfHeal';

export const Root: React.FC = () => (
  <>
    <Composition id="SelfHealV" component={SelfHealV} durationInFrames={FRAMES} fps={30} width={1080} height={1920} />
    <Still id="SelfHealSquare" component={SelfHealSquare} width={1080} height={1080} />
  </>
);
