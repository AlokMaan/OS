import React, { useRef, useEffect, useCallback } from 'react';
import { Play, Pause, SkipForward, RotateCcw } from 'lucide-react';
import { useAppStore } from '@/store/store';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { cn } from '@/lib/utils';

const SPEED_OPTIONS = [0.5, 1, 2, 4, 8];

export default function PlaybackControls() {
  const {
    isSimulated, currentTime, setCurrentTime,
    isPlaying, setIsPlaying, playbackSpeed, setPlaybackSpeed, maxTime,
  } = useAppStore();
  const animRef = useRef<number>(0);
  const lastTimeRef = useRef<number>(0);

  const tick = useCallback(
    (timestamp: number) => {
      if (lastTimeRef.current === 0) lastTimeRef.current = timestamp;
      const delta = (timestamp - lastTimeRef.current) / 1000;
      lastTimeRef.current = timestamp;

      const { currentTime, maxTime, isPlaying, playbackSpeed } = useAppStore.getState();
      if (!isPlaying) return;

      const next = currentTime + delta * playbackSpeed;
      if (next >= maxTime) {
        setCurrentTime(maxTime);
        setIsPlaying(false);
        return;
      }
      setCurrentTime(next);
      animRef.current = requestAnimationFrame(tick);
    },
    [setCurrentTime, setIsPlaying],
  );

  useEffect(() => {
    if (isPlaying) {
      lastTimeRef.current = 0;
      animRef.current = requestAnimationFrame(tick);
    }
    return () => cancelAnimationFrame(animRef.current);
  }, [isPlaying, tick]);

  if (!isSimulated) return null;

  return (
    <div className="flex flex-col sm:flex-row items-center gap-4 p-4 rounded-xl border border-border/50 bg-card/50 backdrop-blur-sm">
      {/* Playback buttons */}
      <div className="flex items-center gap-1">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => { setCurrentTime(0); setIsPlaying(false); }}
          aria-label="Reset"
        >
          <RotateCcw className="h-4 w-4" />
        </Button>
        <Button
          variant={isPlaying ? 'secondary' : 'default'}
          size="icon"
          onClick={() => {
            if (currentTime >= maxTime) setCurrentTime(0);
            setIsPlaying(!isPlaying);
          }}
          aria-label={isPlaying ? 'Pause' : 'Play'}
          className={cn(!isPlaying && 'bg-emerald-600 hover:bg-emerald-700 text-white')}
        >
          {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
        </Button>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => {
            const next = Math.min(Math.floor(currentTime) + 1, maxTime);
            setCurrentTime(next);
          }}
          aria-label="Step forward"
        >
          <SkipForward className="h-4 w-4" />
        </Button>
      </div>

      {/* Timeline slider */}
      <div className="flex-1 flex items-center gap-3 min-w-0 w-full sm:w-auto">
        <Slider
          value={[currentTime]}
          min={0}
          max={maxTime}
          step={0.1}
          onValueChange={([v]) => {
            setCurrentTime(v);
            if (isPlaying) setIsPlaying(false);
          }}
          className="flex-1"
        />
        <span className="font-mono text-sm text-muted-foreground whitespace-nowrap min-w-[80px] text-right">
          t = {Math.floor(currentTime)} / {maxTime}
        </span>
      </div>

      {/* Speed selector */}
      <div className="flex items-center gap-1">
        {SPEED_OPTIONS.map((s) => (
          <Button
            key={s}
            variant={playbackSpeed === s ? 'secondary' : 'ghost'}
            size="sm"
            onClick={() => setPlaybackSpeed(s)}
            className="h-7 px-2 text-xs font-mono"
          >
            {s}x
          </Button>
        ))}
      </div>
    </div>
  );
}
