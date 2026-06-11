// components/UnoCard.tsx — CAT-THEMED UNO CARD COMPONENTS.
//
// Exports three components:
//   UnoCard   — face-up card with cat PNG illustration
//   CardBack  — face-down card (purple "UNO" back)
//   CardSlot  — dashed empty placeholder
//
// Cat images use mix-blend-mode: multiply so the white PNG background
// "disappears" on coloured cards — the cat looks painted onto the card.

import { cn } from '@/lib/utils'
import type { Card, CardColor, CardKind } from '@/types'

// ── Import all 10 cat images ──────────────────────────────────────────────────
import cat1  from '@/assets/cat1.PNG'
import cat2  from '@/assets/cat2.PNG'
import cat3  from '@/assets/cat3.PNG'
import cat4  from '@/assets/cat4.PNG'
import cat5  from '@/assets/cat5.PNG'
import cat6  from '@/assets/cat6.PNG'
import cat7  from '@/assets/cat7.PNG'
import cat8  from '@/assets/cat8.PNG'
import cat9  from '@/assets/cat9.PNG'
import cat10 from '@/assets/cat10.PNG'

// ── Card kind → cat image ─────────────────────────────────────────────────────
// Numbers 0–9 each get their own unique cat.
// Action / Wild cards reuse a cat that visually fits their meaning:
//   SKIP    → cat6  (jumping cat = running away / skipping)
//   REVERSE → cat7  (another leaping pose = changing direction)
//   DRAW2   → cat8  (grey tabby looking expectant = wait for it…)
//   WILD    → cat10 (bicolor lounging = laid-back, can go anywhere)
//   DRAW4   → cat9  (dark tabby = serious card = dark cat)

const CAT: Record<CardKind, string> = {
  ZERO:    cat1,
  ONE:     cat2,
  TWO:     cat3,
  THREE:   cat4,
  FOUR:    cat5,
  FIVE:    cat6,
  SIX:     cat7,
  SEVEN:   cat8,
  EIGHT:   cat9,
  NINE:    cat10,
  SKIP:    cat6,
  REVERSE: cat7,
  DRAW2:   cat8,
  WILD:    cat10,
  DRAW4:   cat9,
}

// ── Card colour → Tailwind background ────────────────────────────────────────
const BG: Record<CardColor, string> = {
  RED:    'bg-red-500',
  GREEN:  'bg-green-600',
  YELLOW: 'bg-yellow-400',
  BLUE:   'bg-blue-600',
  NONE:   'bg-gray-900',
}

// ── Corner label ──────────────────────────────────────────────────────────────
function cornerLabel(card: Card): string {
  const map: Record<string, string> = {
    ZERO: '0', ONE: '1', TWO: '2', THREE: '3', FOUR: '4',
    FIVE: '5', SIX: '6', SEVEN: '7', EIGHT: '8', NINE: '9',
    SKIP: '⊘', REVERSE: '↺', DRAW2: '+2', WILD: '★', DRAW4: '+4',
  }
  return map[card.kind] ?? '?'
}

// ── Size tokens ───────────────────────────────────────────────────────────────
const SIZES = {
  sm: { outer: 'w-10 h-[58px]',  label: 'text-[9px]',  img: 'w-8 h-8'       },
  md: { outer: 'w-[56px] h-20',  label: 'text-[10px]', img: 'w-11 h-11'     },
  lg: { outer: 'w-24 h-[136px]', label: 'text-sm',     img: 'w-[72px] h-[72px]' },
}

// ── UnoCard ───────────────────────────────────────────────────────────────────

interface UnoCardProps {
  card: Card
  displayColor?: CardColor   // override shown colour (used after a Wild is played)
  size?: 'sm' | 'md' | 'lg'
  playable?: boolean          // green glow = legal to play right now
  onClick?: () => void
  className?: string
}

export function UnoCard({ card, displayColor, size = 'md', playable, onClick, className }: UnoCardProps) {
  const color  = displayColor ?? card.color
  const label  = cornerLabel(card)
  const catImg = CAT[card.kind]
  const s      = SIZES[size]
  const isWild = card.color === 'NONE'

  return (
    <div
      onClick={onClick}
      className={cn(
        'relative rounded-xl select-none flex-shrink-0 overflow-hidden',
        s.outer,
        BG[color],
        onClick && 'card-hover cursor-pointer',
        playable && 'card-playable',
        className,
      )}
    >
      {/* Inner border ring for depth */}
      <div className="absolute inset-1 rounded-lg border-2 border-white/40 pointer-events-none z-10" />

      {/* Wild card: four-colour quadrant layer behind the cat */}
      {isWild && (
        <div className="absolute inset-0 grid grid-cols-2 grid-rows-2">
          <div className="bg-red-500" />
          <div className="bg-blue-600" />
          <div className="bg-yellow-400" />
          <div className="bg-green-600" />
        </div>
      )}

      {/* Top-left corner label */}
      <span className={cn(
        'absolute top-1 left-1.5 font-black leading-none text-white drop-shadow-md z-20',
        s.label,
      )}>
        {label}
      </span>

      {/* Cat illustration — mix-blend-mode:multiply makes white PNG areas
          transparent so the cat sits directly on the card colour */}
      <div className="absolute inset-0 flex items-center justify-center z-10">
        <img
          src={catImg}
          alt={card.kind}
          draggable={false}
          className={cn('object-contain', s.img)}
          style={{ mixBlendMode: 'multiply' }}
        />
      </div>

      {/* Bottom-right corner label (rotated 180°) */}
      <span className={cn(
        'absolute bottom-1 right-1.5 font-black leading-none text-white drop-shadow-md rotate-180 z-20',
        s.label,
      )}>
        {label}
      </span>
    </div>
  )
}

// ── CardBack — face-down card ─────────────────────────────────────────────────

interface CardBackProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
  onClick?: () => void
}

export function CardBack({ size = 'md', onClick, className }: CardBackProps) {
  const s = SIZES[size]
  return (
    <div
      onClick={onClick}
      className={cn(
        'relative rounded-xl flex-shrink-0 overflow-hidden bg-[#1a1040]',
        'border-2 border-[#6c63ff]/70',
        s.outer,
        onClick && 'card-hover cursor-pointer',
        className,
      )}
    >
      {/* Subtle diagonal stripe pattern */}
      <div
        className="absolute inset-0 opacity-10"
        style={{
          backgroundImage: 'repeating-linear-gradient(45deg, #6c63ff 0px, #6c63ff 2px, transparent 2px, transparent 10px)',
        }}
      />
      {/* Inner border */}
      <div className="absolute inset-1 rounded-lg border border-[#6c63ff]/40" />
      {/* UNO label */}
      <div className="absolute inset-0 flex items-center justify-center">
        <span className={cn(
          'font-black italic text-[#a89eff] drop-shadow select-none',
          size === 'sm' ? 'text-[10px]' : size === 'md' ? 'text-xs' : 'text-xl',
        )}>
          UNO
        </span>
      </div>
    </div>
  )
}

// ── CardSlot — empty placeholder ──────────────────────────────────────────────

export function CardSlot({ size = 'lg', label }: { size?: 'sm' | 'md' | 'lg'; label?: string }) {
  const s = SIZES[size]
  return (
    <div className={cn(
      'rounded-xl border-2 border-dashed border-[#2a2a4a] flex items-center justify-center',
      'text-[#555566] text-xs flex-shrink-0',
      s.outer,
    )}>
      {label}
    </div>
  )
}
